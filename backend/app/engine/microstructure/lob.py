import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum


class OrderSide(str, Enum):
    BID = "BID"
    ASK = "ASK"


@dataclass
class Order:
    order_id: str
    side: OrderSide
    price: float
    quantity: float
    timestamp: float
    filled_quantity: float = 0.0

    @property
    def remaining_quantity(self) -> float:
        return max(0.0, self.quantity - self.filled_quantity)

    @property
    def is_filled(self) -> bool:
        return self.remaining_quantity <= 1e-8


@dataclass
class Trade:
    trade_id: str
    price: float
    quantity: float
    timestamp: float
    maker_order_id: str
    taker_order_id: str
    taker_side: OrderSide


class PriceLevel:
    """FIFO queue representing all limit orders at an exact discrete price."""
    def __init__(self, price: float):
        self.price = round(price, 4)
        self.orders: deque[Order] = deque()
        self.total_quantity: float = 0.0

    def add_order(self, order: Order):
        self.orders.append(order)
        self.total_quantity += order.remaining_quantity

    def remove_order(self, order_id: str) -> Optional[Order]:
        for i, order in enumerate(self.orders):
            if order.order_id == order_id:
                self.total_quantity -= order.remaining_quantity
                del self.orders[i]
                return order
        return None

    def fill(self, incoming_qty: float) -> Tuple[float, List[Tuple[Order, float]]]:
        """
        Fills orders in strict price-time priority.
        Returns: (remaining_incoming_qty, list of (maker_order, filled_qty))
        """
        fills = []
        rem = incoming_qty

        while self.orders and rem > 1e-8:
            head = self.orders[0]
            fill_amount = min(rem, head.remaining_quantity)
            head.filled_quantity += fill_amount
            self.total_quantity -= fill_amount
            rem -= fill_amount
            fills.append((head, fill_amount))

            if head.is_filled:
                self.orders.popleft()

        return rem, fills


class LimitOrderBook:
    """
    Continuous double-auction limit order book with strict price-time priority.
    """
    def __init__(self, symbol: str = "BTC/USD"):
        self.symbol = symbol
        # Bids: price -> PriceLevel (sorted descending)
        self.bids: Dict[float, PriceLevel] = {}
        # Asks: price -> PriceLevel (sorted ascending)
        self.asks: Dict[float, PriceLevel] = {}
        # All live orders indexed by order_id
        self.orders: Dict[str, Order] = {}
        # History of recent executed trades
        self.trades: List[Trade] = []

    @property
    def best_bid(self) -> Optional[float]:
        if not self.bids:
            return None
        return max(self.bids.keys())

    @property
    def best_ask(self) -> Optional[float]:
        if not self.asks:
            return None
        return min(self.asks.keys())

    @property
    def spread(self) -> Optional[float]:
        bb = self.best_bid
        ba = self.best_ask
        if bb is not None and ba is not None:
            return round(ba - bb, 4)
        return None

    @property
    def mid_price(self) -> Optional[float]:
        bb = self.best_bid
        ba = self.best_ask
        if bb is not None and ba is not None:
            return round((bb + ba) / 2.0, 4)
        return None

    @property
    def microprice(self) -> Optional[float]:
        """
        Volume-weighted microprice reflecting immediate queue pressure:
        P_micro = (Q_bid * P_ask + Q_ask * P_bid) / (Q_bid + Q_ask)
        """
        bb = self.best_bid
        ba = self.best_ask
        if bb is None or ba is None:
            return None
        q_bid = self.bids[bb].total_quantity
        q_ask = self.asks[ba].total_quantity
        total_q = q_bid + q_ask
        if total_q <= 1e-8:
            return self.mid_price
        return round((q_bid * ba + q_ask * bb) / total_q, 4)

    @property
    def order_flow_imbalance(self) -> float:
        """
        Order flow imbalance ratio: (Q_bid - Q_ask) / (Q_bid + Q_ask) in [-1, +1].
        """
        bb = self.best_bid
        ba = self.best_ask
        if bb is None or ba is None:
            return 0.0
        q_bid = self.bids[bb].total_quantity
        q_ask = self.asks[ba].total_quantity
        tot = q_bid + q_ask
        if tot <= 1e-8:
            return 0.0
        return round((q_bid - q_ask) / tot, 4)

    def add_limit_order(
        self,
        side: OrderSide,
        price: float,
        quantity: float,
        timestamp: float = 0.0,
        order_id: Optional[str] = None,
    ) -> Tuple[Order, List[Trade]]:
        """
        Insert limit order into matching engine.
        If crossing, matches immediately as taker. Remainder posted to book as maker.
        """
        price = round(price, 4)
        quantity = round(quantity, 4)
        order_id = order_id or str(uuid.uuid4())[:8]

        order = Order(
            order_id=order_id,
            side=side,
            price=price,
            quantity=quantity,
            timestamp=timestamp,
        )

        executed_trades = []

        if side == OrderSide.BID:
            # Check crossing with existing asks (ask_price <= bid_price)
            while self.asks and order.remaining_quantity > 1e-8:
                best_ask_price = min(self.asks.keys())
                if best_ask_price > price:
                    break  # No cross

                level = self.asks[best_ask_price]
                rem, fills = level.fill(order.remaining_quantity)
                order.filled_quantity += (order.remaining_quantity - rem)

                for maker_order, filled_qty in fills:
                    trade = Trade(
                        trade_id=str(uuid.uuid4())[:8],
                        price=best_ask_price,
                        quantity=filled_qty,
                        timestamp=timestamp,
                        maker_order_id=maker_order.order_id,
                        taker_order_id=order.order_id,
                        taker_side=OrderSide.BID,
                    )
                    executed_trades.append(trade)
                    self.trades.append(trade)

                if level.total_quantity <= 1e-8:
                    del self.asks[best_ask_price]

            # If remainder remains, post to bid book
            if not order.is_filled:
                if price not in self.bids:
                    self.bids[price] = PriceLevel(price)
                self.bids[price].add_order(order)
                self.orders[order.order_id] = order

        else:  # ASK
            # Check crossing with existing bids (bid_price >= ask_price)
            while self.bids and order.remaining_quantity > 1e-8:
                best_bid_price = max(self.bids.keys())
                if best_bid_price < price:
                    break  # No cross

                level = self.bids[best_bid_price]
                rem, fills = level.fill(order.remaining_quantity)
                order.filled_quantity += (order.remaining_quantity - rem)

                for maker_order, filled_qty in fills:
                    trade = Trade(
                        trade_id=str(uuid.uuid4())[:8],
                        price=best_bid_price,
                        quantity=filled_qty,
                        timestamp=timestamp,
                        maker_order_id=maker_order.order_id,
                        taker_order_id=order.order_id,
                        taker_side=OrderSide.ASK,
                    )
                    executed_trades.append(trade)
                    self.trades.append(trade)

                if level.total_quantity <= 1e-8:
                    del self.bids[best_bid_price]

            # If remainder remains, post to ask book
            if not order.is_filled:
                if price not in self.asks:
                    self.asks[price] = PriceLevel(price)
                self.asks[price].add_order(order)
                self.orders[order.order_id] = order

        return order, executed_trades

    def cancel_order(self, order_id: str) -> bool:
        """Cancel resting limit order by ID."""
        if order_id not in self.orders:
            return False
        order = self.orders[order_id]
        if order.side == OrderSide.BID:
            if order.price in self.bids:
                self.bids[order.price].remove_order(order_id)
                if self.bids[order.price].total_quantity <= 1e-8:
                    del self.bids[order.price]
        else:
            if order.price in self.asks:
                self.asks[order.price].remove_order(order_id)
                if self.asks[order.price].total_quantity <= 1e-8:
                    del self.asks[order.price]

        del self.orders[order_id]
        return True

    def get_depth_snapshot(self, levels: int = 10) -> Dict[str, Any]:
        """Return standardized L2 depth ladder and microstructure metrics."""
        sorted_bids = sorted(self.bids.keys(), reverse=True)[:levels]
        sorted_asks = sorted(self.asks.keys())[:levels]

        bids_ladder = [
            {"price": p, "quantity": round(self.bids[p].total_quantity, 4), "order_count": len(self.bids[p].orders)}
            for p in sorted_bids
        ]
        asks_ladder = [
            {"price": p, "quantity": round(self.asks[p].total_quantity, 4), "order_count": len(self.asks[p].orders)}
            for p in sorted_asks
        ]

        return {
            "symbol": self.symbol,
            "best_bid": self.best_bid,
            "best_ask": self.best_ask,
            "spread": self.spread,
            "mid_price": self.mid_price,
            "microprice": self.microprice,
            "order_flow_imbalance": self.order_flow_imbalance,
            "total_open_orders": len(self.orders),
            "bids": bids_ladder,
            "asks": asks_ladder,
            "recent_trades": [
                {
                    "trade_id": t.trade_id,
                    "price": t.price,
                    "quantity": t.quantity,
                    "taker_side": t.taker_side.value,
                    "timestamp": t.timestamp,
                }
                for t in self.trades[-15:]
            ],
        }

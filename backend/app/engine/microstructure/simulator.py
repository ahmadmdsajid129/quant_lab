import numpy as np
from typing import Dict, Any, List
from app.engine.microstructure.lob import LimitOrderBook, OrderSide


def simulate_synthetic_order_book(
    symbol: str = "BTC/USD",
    initial_mid: float = 100.0,
    tick_size: float = 0.05,
    num_events: int = 150,
    seed: int = 42,
) -> LimitOrderBook:
    """
    Generate synthetic limit order book with realistic bid-ask queues and trade executions.
    Uses Poisson arrival rates for limit orders, market orders, and order cancellations.
    """
    rng = np.random.default_rng(seed)
    lob = LimitOrderBook(symbol=symbol)

    # 1. Seed initial resting depth on both sides
    for level_i in range(1, 15):
        bid_px = round(initial_mid - (level_i * tick_size), 4)
        ask_px = round(initial_mid + (level_i * tick_size), 4)
        
        # Multiple orders at each depth level
        for _ in range(rng.integers(2, 5)):
            qty = round(float(rng.uniform(0.5, 3.0)), 3)
            lob.add_limit_order(OrderSide.BID, bid_px, qty)

        for _ in range(rng.integers(2, 5)):
            qty = round(float(rng.uniform(0.5, 3.0)), 3)
            lob.add_limit_order(OrderSide.ASK, ask_px, qty)

    # 2. Replay stochastic event stream
    timestamp = 1.0
    for _ in range(num_events):
        timestamp += float(rng.exponential(0.1))
        mid = lob.mid_price or initial_mid
        event_type = rng.choice(["LIMIT", "MARKET", "CANCEL"], p=[0.60, 0.25, 0.15])
        side = OrderSide.BID if rng.random() > 0.5 else OrderSide.ASK

        if event_type == "LIMIT":
            # Post limit order around current spread
            offset = float(rng.integers(1, 6) * tick_size)
            if side == OrderSide.BID:
                px = round(mid - offset, 4)
            else:
                px = round(mid + offset, 4)
            qty = round(float(rng.uniform(0.2, 2.5)), 3)
            lob.add_limit_order(side, px, qty, timestamp=timestamp)

        elif event_type == "MARKET":
            # Aggressive order crossing the best opposite quote
            qty = round(float(rng.uniform(0.1, 1.8)), 3)
            if side == OrderSide.BID and lob.best_ask:
                # Buy at best ask
                lob.add_limit_order(OrderSide.BID, lob.best_ask, qty, timestamp=timestamp)
            elif side == OrderSide.ASK and lob.best_bid:
                # Sell at best bid
                lob.add_limit_order(OrderSide.ASK, lob.best_bid, qty, timestamp=timestamp)

        elif event_type == "CANCEL":
            # Cancel an existing order at random
            if lob.orders:
                order_id_to_cancel = rng.choice(list(lob.orders.keys()))
                lob.cancel_order(order_id_to_cancel)

    return lob

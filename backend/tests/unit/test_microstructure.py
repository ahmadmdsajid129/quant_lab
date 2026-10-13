import pytest
import numpy as np
from app.engine.microstructure.lob import LimitOrderBook, OrderSide
from app.engine.microstructure.simulator import simulate_synthetic_order_book


def test_lob_price_time_priority():
    lob = LimitOrderBook(symbol="ETH/USD")

    # Add two bids at same price level ($2000.0)
    o1, _ = lob.add_limit_order(OrderSide.BID, 2000.0, 1.0, timestamp=1.0, order_id="ord-1")
    o2, _ = lob.add_limit_order(OrderSide.BID, 2000.0, 2.0, timestamp=2.0, order_id="ord-2")

    assert lob.best_bid == 2000.0
    assert lob.bids[2000.0].total_quantity == 3.0

    # Incoming aggressive sell of 1.5 should fill ord-1 first (FIFO) and ord-2 partially
    sell_order, trades = lob.add_limit_order(OrderSide.ASK, 2000.0, 1.5, timestamp=3.0, order_id="ord-taker")

    assert len(trades) == 2
    assert trades[0].maker_order_id == "ord-1"
    assert trades[0].quantity == 1.0
    assert trades[1].maker_order_id == "ord-2"
    assert trades[1].quantity == 0.5

    # Check remainder on ord-2
    assert lob.bids[2000.0].total_quantity == 1.5
    assert o1.is_filled is True
    assert o2.remaining_quantity == 1.5


def test_lob_crossing_execution():
    lob = LimitOrderBook(symbol="BTC/USD")

    # Maker posts ask at 50,000
    lob.add_limit_order(OrderSide.ASK, 50000.0, 1.0, order_id="ask-1")
    assert lob.best_ask == 50000.0

    # Taker bids at 50,100 (crosses book)
    buyer, trades = lob.add_limit_order(OrderSide.BID, 50100.0, 0.4, order_id="bid-1")
    assert len(trades) == 1
    # Trade executes at maker's resting price (50,000)
    assert trades[0].price == 50000.0
    assert trades[0].quantity == 0.4
    assert buyer.is_filled is True
    assert lob.best_ask == 50000.0
    assert lob.asks[50000.0].total_quantity == 0.6


def test_lob_microprice_and_ofi():
    lob = LimitOrderBook(symbol="SOL/USD")
    # Best bid: 100 with qty 10.0
    lob.add_limit_order(OrderSide.BID, 100.0, 10.0)
    # Best ask: 102 with qty 2.0
    lob.add_limit_order(OrderSide.ASK, 102.0, 2.0)

    mid = lob.mid_price
    micro = lob.microprice
    ofi = lob.order_flow_imbalance

    assert mid == 101.0
    # Heavy bid queue (10 vs 2) exerts upward pressure: microprice must be > mid price
    assert micro > mid
    assert ofi > 0.0  # (10 - 2)/(10 + 2) > 0


def test_lob_cancellation():
    lob = LimitOrderBook(symbol="AAPL")
    o, _ = lob.add_limit_order(OrderSide.BID, 150.0, 5.0, order_id="canc-me")
    assert lob.best_bid == 150.0

    success = lob.cancel_order("canc-me")
    assert success is True
    assert lob.best_bid is None
    assert lob.cancel_order("non-existent") is False


def test_microstructure_simulator_and_api(client):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "hft_trader@quantlab.io", "password": "Password123!", "full_name": "Quant HFT"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Run simulation
    res_sim = client.post(
        "/api/v1/microstructure/simulate",
        headers=headers,
        json={"symbol": "BTC/USD", "initial_mid": 65000.0, "tick_size": 1.0, "num_events": 100, "seed": 42},
    )
    assert res_sim.status_code == 200
    snap = res_sim.json()
    assert snap["symbol"] == "BTC/USD"
    assert snap["best_bid"] is not None
    assert snap["best_ask"] is not None
    assert snap["best_bid"] < snap["best_ask"]
    assert len(snap["bids"]) > 0
    assert len(snap["asks"]) > 0

    # 2. Place manual limit order
    res_ord = client.post(
        "/api/v1/microstructure/order",
        headers=headers,
        json={"symbol": "BTC/USD", "side": "BID", "price": snap["best_bid"], "quantity": 0.5},
    )
    assert res_ord.status_code == 200
    updated_snap = res_ord.json()
    assert updated_snap["total_open_orders"] >= snap["total_open_orders"]

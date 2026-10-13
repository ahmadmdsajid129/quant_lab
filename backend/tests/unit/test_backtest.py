import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from app.engine.data.synthetic import generate_synthetic_ohlcv
from app.engine.strategy.templates import (
    BuyAndHoldStrategy,
    MovingAverageCrossoverStrategy,
    MomentumStrategy,
    MeanReversionStrategy,
)
from app.engine.backtest.event import EventBacktestEngine
from app.engine.backtest.vectorized import run_vectorized_backtest


def test_strategy_signal_generation():
    df = generate_synthetic_ohlcv(symbol="STRAT-TEST", periods=100, seed=42)

    # Buy and Hold
    bah = BuyAndHoldStrategy()
    sig_bah = bah.generate_signals(df)
    assert (sig_bah == 1.0).all()

    # MA Crossover
    mac = MovingAverageCrossoverStrategy({"fast_period": 5, "slow_period": 15})
    sig_mac = mac.generate_signals(df)
    assert len(sig_mac) == 100
    assert set(sig_mac.unique()).issubset({0.0, 1.0})

    # Momentum
    mom = MomentumStrategy({"lookback_period": 10})
    sig_mom = mom.generate_signals(df)
    assert len(sig_mom) == 100

    # Mean Reversion
    mr = MeanReversionStrategy({"window": 10, "entry_threshold": 1.5})
    sig_mr = mr.generate_signals(df)
    assert len(sig_mr) == 100


def test_event_backtester_cash_conservation_and_costs():
    df = generate_synthetic_ohlcv(symbol="COST-TEST", periods=252, initial_price=100.0, seed=42)
    strat = MovingAverageCrossoverStrategy({"fast_period": 10, "slow_period": 30})

    engine = EventBacktestEngine(
        initial_capital=100_000.0,
        commission_bps=10.0,  # 10 bps
        slippage_pct=0.10,    # 0.10% slippage
    )
    result = engine.run(df, strat)

    assert result["initial_capital"] == 100_000.0
    assert "final_capital" in result
    assert result["total_fees_paid"] >= 0.0
    assert len(result["equity_curve"]) == 252

    metrics = result["metrics"]
    assert "sharpe_ratio" in metrics
    assert "max_drawdown" in metrics
    assert metrics["max_drawdown"] <= 0.0

    # Verify fees were accounted for in trade logs
    for trade in result["trade_logs"]:
        assert trade["fees"] >= 0.0
        # Net PnL = Gross PnL - Fees within floating point rounding
        assert abs(trade["net_pnl"] - (trade["gross_pnl"] - trade["fees"])) < 0.05


def test_no_lookahead_bias_invariant():
    """
    Look-ahead Bias Test:
    Altering price data at bar t = 50 must NOT affect any decisions or
    trades executed at bar t <= 49.
    """
    df_clean = generate_synthetic_ohlcv(symbol="LOOKAHEAD", periods=100, seed=42)
    df_shocked = df_clean.copy()
    
    # Introduce an extreme future shock at bar 60 (close jumps by 500%)
    df_shocked.loc[60, "close"] = df_shocked.loc[60, "close"] * 6.0
    df_shocked.loc[60, "high"] = df_shocked.loc[60, "high"] * 6.0

    strat = MovingAverageCrossoverStrategy({"fast_period": 5, "slow_period": 15})
    engine = EventBacktestEngine(initial_capital=100_000.0)

    res_clean = engine.run(df_clean, strat)
    res_shocked = engine.run(df_shocked, strat)

    # Decisions and equity up to bar 50 MUST be identical bit-for-bit
    eq_clean_pre = [p["equity"] for p in res_clean["equity_curve"][:50]]
    eq_shocked_pre = [p["equity"] for p in res_shocked["equity_curve"][:50]]
    assert eq_clean_pre == eq_shocked_pre, "Future price alteration at bar 60 leaked into decisions before bar 50!"


def test_backtest_api_execution_and_lineage(client: TestClient):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "trader_bt@quantlab.io", "password": "Password123!", "full_name": "Marcus Dev"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create project
    proj = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"title": "Momentum Backtest Lab", "asset_class": "EQUITIES"},
    ).json()
    proj_id = proj["id"]

    # Generate dataset
    ds = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "QQQ-SYNTH", "periods": 252, "initial_price": 300.0, "seed": 888},
    ).json()
    ds_id = ds["id"]

    # Run Backtest
    bt_resp = client.post(
        "/api/v1/backtests/run",
        headers=headers,
        json={
            "project_id": proj_id,
            "dataset_id": ds_id,
            "strategy_type": "MA_CROSSOVER",
            "parameters": {"fast_period": 10, "slow_period": 30},
            "initial_capital": 100_000.0,
            "commission_bps": 5.0,
            "slippage_pct": 0.05,
        },
    )
    assert bt_resp.status_code == 201
    bt_data = bt_resp.json()
    assert bt_data["status"] == "COMPLETED"
    assert "lineage_hash" in bt_data
    assert len(bt_data["lineage_hash"]) == 64  # SHA-256
    assert len(bt_data["equity_curve"]) == 252
    assert "sharpe_ratio" in bt_data["metrics"]

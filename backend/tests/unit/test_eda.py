import pytest
import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from app.engine.statistics.eda import (
    compute_returns_series,
    compute_rolling_volatility,
    compute_distribution_metrics,
    compute_autocorrelation,
    compute_drawdown_series,
)
from app.engine.data.synthetic import generate_synthetic_ohlcv


def test_eda_returns_and_volatility():
    prices = pd.Series([100.0, 105.0, 102.0, 108.0, 110.0])
    ret_df = compute_returns_series(prices)

    # Check simple returns
    assert round(ret_df["simple_return"].iloc[0], 4) == 0.0500  # (105-100)/100
    assert round(ret_df["simple_return"].iloc[1], 4) == -0.0286  # (102-105)/105

    # Check cumulative return matches total price change
    final_cum = ret_df["cumulative_return"].iloc[-1]
    expected_total = (110.0 - 100.0) / 100.0
    assert abs(final_cum - expected_total) < 1e-6


def test_eda_distribution_and_drawdown():
    df = generate_synthetic_ohlcv(symbol="EDA-TEST", periods=252, seed=42)
    prices = df["close"]
    returns = compute_returns_series(prices)["simple_return"]

    # Distribution diagnostics
    dist = compute_distribution_metrics(returns)
    assert dist["count"] == 251
    assert "skewness" in dist
    assert "excess_kurtosis" in dist
    assert "jarque_bera" in dist
    assert "augmented_dickey_fuller" in dist
    # Returns of stationary series should be stationary under ADF (p < 0.05)
    assert dist["augmented_dickey_fuller"]["is_stationary"] is True

    # Drawdown invariant
    dd_df = compute_drawdown_series(prices)
    assert (dd_df["drawdown"] <= 0.0).all(), "Drawdown percentage must always be <= 0.0"
    assert (dd_df["drawdown"] >= -1.0).all(), "Drawdown cannot exceed -100%"


def test_analytics_api_endpoint(client: TestClient):
    # Register User
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "priya_eda@quantlab.io", "password": "Password123!", "full_name": "Priya Sharma"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate Synthetic Dataset
    ds = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "BTC-SYNTH", "periods": 252, "initial_price": 50000.0, "seed": 77},
    ).json()
    ds_id = ds["id"]

    # Call Analytics Summary API
    resp = client.post(
        "/api/v1/analytics/summary",
        headers=headers,
        json={"dataset_id": ds_id, "rolling_window": 21},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["symbol"] == "BTC-SYNTH"
    assert data["total_bars"] == 252
    assert "distribution" in data
    assert "acf_lags" in data
    assert len(data["acf_lags"]) == 21  # lag 0 to 20
    assert data["max_drawdown"] <= 0.0

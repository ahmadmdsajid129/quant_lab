import pytest
from fastapi.testclient import TestClient
from app.engine.data.synthetic import generate_synthetic_ohlcv
from app.engine.data.quality import run_data_quality_audit


def test_synthetic_data_generator_deterministic_and_invariants():
    # Test identical output for identical seeds
    df1 = generate_synthetic_ohlcv(symbol="TEST", periods=100, seed=123)
    df2 = generate_synthetic_ohlcv(symbol="TEST", periods=100, seed=123)
    pd_diff = (df1["close"] - df2["close"]).abs().sum()
    assert pd_diff == 0.0, "Identical seed must produce bit-for-bit identical price series"

    # Invariants checks
    assert len(df1) == 100
    assert (df1["high"] >= df1[["open", "close"]].max(axis=1)).all(), "High must be >= max(Open, Close)"
    assert (df1["low"] <= df1[["open", "close"]].min(axis=1)).all(), "Low must be <= min(Open, Close)"
    assert (df1["volume"] > 0).all(), "Volume must be strictly positive"
    assert (df1["open"] > 0).all(), "Open price must be strictly positive"


def test_data_quality_audit():
    df = generate_synthetic_ohlcv(symbol="AUDIT", periods=252, seed=42)
    audit = run_data_quality_audit(df)
    assert audit["score"] >= 95.0, f"Expected verified synthetic data to score >= 95%, got {audit['score']}"
    assert audit["status"] == "QUALITY_VERIFIED"
    assert audit["violations_count"] == 0


def test_datasets_api_lifecycle(client: TestClient):
    # Register User
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "marcus_data@quantlab.io", "password": "Password123!", "full_name": "Marcus Chen"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate synthetic dataset via API
    gen_resp = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={
            "symbol": "SPY-SYNTH",
            "periods": 252,
            "initial_price": 400.0,
            "annual_drift": 0.10,
            "annual_volatility": 0.18,
            "seed": 999,
        },
    )
    assert gen_resp.status_code == 201
    dataset = gen_resp.json()
    assert dataset["symbol"] == "SPY-SYNTH"
    assert dataset["total_bars"] == 252
    assert dataset["quality_score"] >= 95.0
    dataset_id = dataset["id"]

    # List datasets
    list_resp = client.get("/api/v1/datasets", headers=headers)
    assert list_resp.status_code == 200
    datasets = list_resp.json()
    assert len(datasets) == 1
    assert datasets[0]["id"] == dataset_id

    # Fetch OHLCV bars from Parquet
    ohlcv_resp = client.get(f"/api/v1/datasets/{dataset_id}/ohlcv?limit=100", headers=headers)
    assert ohlcv_resp.status_code == 200
    bars = ohlcv_resp.json()
    assert len(bars) == 100
    assert "close" in bars[0]
    assert "high" in bars[0]
    assert bars[0]["high"] >= bars[0]["close"]

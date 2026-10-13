import pytest
import numpy as np
import pandas as pd
from app.engine.data.synthetic import generate_synthetic_ohlcv
from app.engine.ml.features import build_financial_features, chronological_split_and_scale
from app.engine.ml.models import train_and_evaluate_model


def test_build_financial_features():
    df = generate_synthetic_ohlcv(periods=250, seed=42)
    X, y = build_financial_features(df)
    
    assert len(X) > 200
    assert len(X) == len(y)
    assert set(y.unique()).issubset({0, 1})
    assert "ret_1d" in X.columns
    assert "vol_10d" in X.columns
    assert "rsi_14d" in X.columns
    assert "macd" in X.columns
    assert "vol_ratio_20d" in X.columns
    assert not X.isna().any().any(), "Features must not contain NaNs"


def test_zero_leakage_scaling_invariant():
    """Verify that test data never influences the train scaler parameters."""
    df = generate_synthetic_ohlcv(periods=250, seed=42)
    X, y = build_financial_features(df)
    
    X_train_1, X_test_1, _, _, scaler_1 = chronological_split_and_scale(X, y, train_ratio=0.7)
    
    # Introduce huge anomaly ONLY into the test set
    X_perturbed = X.copy()
    X_perturbed.iloc[-10:, :] *= 100.0
    
    X_train_2, X_test_2, _, _, scaler_2 = chronological_split_and_scale(X_perturbed, y, train_ratio=0.7)
    
    # Scaler 1 and Scaler 2 means and scales MUST be exactly identical
    np.testing.assert_allclose(scaler_1.mean_, scaler_2.mean_)
    np.testing.assert_allclose(scaler_1.scale_, scaler_2.scale_)
    pd.testing.assert_frame_equal(X_train_1, X_train_2)


def test_train_models_and_drift():
    df = generate_synthetic_ohlcv(periods=250, seed=42)
    X, y = build_financial_features(df)
    X_train, X_test, y_train, y_test, _ = chronological_split_and_scale(X, y, train_ratio=0.75)
    
    for model_type in ["RIDGE", "RANDOM_FOREST", "GBDT"]:
        report = train_and_evaluate_model(X_train, X_test, y_train, y_test, model_type=model_type)
        assert report["model_type"] == model_type
        assert 0.0 <= report["metrics"]["accuracy_test"] <= 1.0
        assert 0.0 <= report["metrics"]["roc_auc_test"] <= 1.0
        assert len(report["feature_importances"]) == len(X.columns)
        assert "concept_drift" in report
        assert report["concept_drift"]["total_features"] == len(X.columns)


def test_ml_api_endpoints(client):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "ml_researcher@quantlab.io", "password": "Password123!", "full_name": "ML Researcher"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Feature definition endpoint
    res_feat = client.get("/api/v1/ml/features", headers=headers)
    assert res_feat.status_code == 200
    features = res_feat.json()
    assert len(features) >= 5

    # 2. Ingest synthetic dataset
    res_gen = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={
            "symbol": "ML-TEST",
            "name": "ML Dataset",
            "asset_class": "EQUITY",
            "periods": 200,
            "seed": 99,
        },
    )
    assert res_gen.status_code == 201
    dataset_id = res_gen.json()["id"]

    # 3. Train ML model
    res_train = client.post(
        "/api/v1/ml/train",
        headers=headers,
        json={
            "dataset_id": dataset_id,
            "model_type": "GBDT",
            "train_ratio": 0.75,
        },
    )
    assert res_train.status_code == 200
    data = res_train.json()
    assert data["model_type"] == "GBDT"
    assert data["metrics"]["accuracy_test"] > 0
    assert "concept_drift" in data


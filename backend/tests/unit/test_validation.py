import pytest
from fastapi.testclient import TestClient
from app.engine.statistics.purged_kfold import PurgedKFold
from app.engine.statistics.dsr import compute_deflated_sharpe_ratio


def test_purged_kfold_no_overlap_and_embargo():
    n_samples = 500
    pkf = PurgedKFold(n_splits=5, embargo_pct=0.02)  # 2% embargo = 10 bars
    
    splits = list(pkf.split(n_samples))
    assert len(splits) == 5

    for train_idx, test_idx in splits:
        # Zero intersection between train and test
        intersection = set(train_idx).intersection(set(test_idx))
        assert len(intersection) == 0, "Train and test folds overlap!"

        # Embargo check: immediately after test interval must not be in train
        test_max = test_idx.max()
        if test_max + 1 < n_samples:
            assert (test_max + 1) not in train_idx, "Embargo bar leaked into train split!"


def test_deflated_sharpe_ratio_multiple_testing_penalty():
    # 1. Single trial with Sharpe 2.0 and 252 bars
    res_1 = compute_deflated_sharpe_ratio(observed_sharpe=2.0, track_length=252, num_trials=1)
    assert res_1["expected_max_sharpe_hurdle"] == 0.0
    assert res_1["is_statistically_significant"] is True

    # 2. 100 trials tested: hurdle must rise and p-value must increase (p-hacking penalty)
    res_100 = compute_deflated_sharpe_ratio(observed_sharpe=2.0, track_length=252, num_trials=100)
    assert res_100["expected_max_sharpe_hurdle"] > 1.5, "Hurdle must increase with 100 trials!"
    assert res_100["p_value"] > res_1["p_value"], "p-value must increase under multiple-testing penalty!"


def test_validation_api_endpoints(client: TestClient):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "val_user@quantlab.io", "password": "Password123!", "full_name": "Validation Lead"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test DSR API
    dsr_resp = client.post(
        "/api/v1/validation/deflated-sharpe",
        json={"observed_sharpe": 1.8, "track_length": 504, "num_trials": 20},
    )
    assert dsr_resp.status_code == 200
    data = dsr_resp.json()
    assert "deflated_sharpe_ratio" in data
    assert "expected_max_sharpe_hurdle" in data
    assert data["num_trials_tested"] == 20

    # Generate synthetic dataset
    ds = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "WF-TEST", "periods": 400, "seed": 55},
    ).json()
    ds_id = ds["id"]

    # Test Walk-Forward API
    wf_resp = client.post(
        "/api/v1/validation/walk-forward",
        headers=headers,
        json={
            "dataset_id": ds_id,
            "strategy_type": "MA_CROSSOVER",
            "parameters": {"fast_period": 5, "slow_period": 15},
            "train_bars": 150,
            "test_bars": 50,
        },
    )
    assert wf_resp.status_code == 200
    wf_data = wf_resp.json()
    assert "total_windows" in wf_data
    assert wf_data["total_windows"] >= 4
    assert "overall_walk_forward_efficiency" in wf_data

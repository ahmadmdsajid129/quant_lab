import pytest
import numpy as np
import pandas as pd
from app.engine.portfolio.covariance import compute_covariance_matrix, compute_risk_contributions
from app.engine.portfolio.optimizers import (
    optimize_equal_weight,
    optimize_inverse_volatility,
    optimize_minimum_variance,
    optimize_max_sharpe,
    optimize_risk_parity,
    optimize_portfolio,
)


def test_covariance_and_ledoit_wolf_shrinkage():
    np.random.seed(42)
    # 100 days of 3 assets
    returns = np.random.normal(0.0005, 0.015, size=(100, 3))
    df = pd.DataFrame(returns, columns=["ASSET_A", "ASSET_B", "ASSET_C"])

    cov_sample, shrink_sample = compute_covariance_matrix(df, method="SAMPLE")
    assert cov_sample.shape == (3, 3)
    assert shrink_sample == 0.0
    assert np.all(np.linalg.eigvals(cov_sample) >= 0), "Covariance must be positive semi-definite"

    cov_lw, shrink_lw = compute_covariance_matrix(df, method="LEDOIT_WOLF")
    assert cov_lw.shape == (3, 3)
    assert 0.0 <= shrink_lw <= 1.0, "Shrinkage intensity must be bounded in [0, 1]"


def test_marginal_risk_contribution_invariant():
    """Mathematical Invariant: sum(RC_i) == sigma_p."""
    np.random.seed(42)
    cov = np.array([
        [0.04, 0.01, 0.005],
        [0.01, 0.09, 0.02],
        [0.005, 0.02, 0.16],
    ])
    weights = np.array([0.4, 0.35, 0.25])

    port_vol, rc, rrc = compute_risk_contributions(weights, cov)
    assert abs(np.sum(rc) - port_vol) < 1e-9, "Sum of risk contributions must equal total portfolio volatility"
    assert abs(np.sum(rrc) - 1.0) < 1e-9, "Sum of relative risk contributions must equal 100%"


def test_portfolio_optimizers_mathematical_properties():
    expected_returns = np.array([0.08, 0.12, 0.15])
    cov = np.array([
        [0.04, 0.005, 0.01],
        [0.005, 0.09, 0.015],
        [0.01, 0.015, 0.16],
    ])
    n = len(expected_returns)

    # 1. Equal Weight
    w_ew = optimize_equal_weight(n)
    np.testing.assert_allclose(w_ew, [1/3, 1/3, 1/3])

    # 2. Inverse Volatility
    w_iv = optimize_inverse_volatility(cov)
    assert np.isclose(np.sum(w_iv), 1.0)
    assert w_iv[0] > w_iv[2], "Asset 0 (vol 0.2) must have higher weight than Asset 2 (vol 0.4)"

    # 3. Minimum Variance
    w_mv = optimize_minimum_variance(cov)
    assert np.isclose(np.sum(w_mv), 1.0)
    var_mv = w_mv.T @ cov @ w_mv
    var_ew = w_ew.T @ cov @ w_ew
    assert var_mv <= var_ew + 1e-9, "Minimum variance must have lower or equal variance than equal weight"

    # 4. Max Sharpe
    w_ms = optimize_max_sharpe(expected_returns, cov, risk_free_rate=0.02)
    assert np.isclose(np.sum(w_ms), 1.0)
    sharpe_ms = (w_ms @ expected_returns - 0.02) / np.sqrt(w_ms.T @ cov @ w_ms)
    sharpe_ew = (w_ew @ expected_returns - 0.02) / np.sqrt(w_ew.T @ cov @ w_ew)
    assert sharpe_ms >= sharpe_ew - 1e-9, "Max Sharpe must have higher or equal Sharpe than equal weight"

    # 5. Equal Risk Parity
    w_rp = optimize_risk_parity(cov)
    assert np.isclose(np.sum(w_rp), 1.0)
    _, _, rrc_rp = compute_risk_contributions(w_rp, cov)
    # In Risk Parity, every asset contributes ~1/3 of total risk
    np.testing.assert_allclose(rrc_rp, [1/3, 1/3, 1/3], atol=0.05)


def test_portfolio_api_endpoint(client):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "portfolio_mgr@quantlab.io", "password": "Password123!", "full_name": "PM Alex"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Generate 2 synthetic datasets
    ds1 = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "PORT-EQ1", "periods": 150, "seed": 101},
    ).json()
    ds2 = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "PORT-EQ2", "periods": 150, "seed": 202},
    ).json()

    # Optimize Portfolio
    res_opt = client.post(
        "/api/v1/portfolio/optimize",
        headers=headers,
        json={
            "dataset_ids": [ds1["id"], ds2["id"]],
            "method": "MAX_SHARPE",
            "covariance_method": "LEDOIT_WOLF",
            "risk_free_rate": 0.02,
        },
    )
    assert res_opt.status_code == 200
    data = res_opt.json()
    assert data["method"] == "MAX_SHARPE"
    assert "PORT-EQ1" in data["weights"]
    assert "PORT-EQ2" in data["weights"]
    assert np.isclose(sum(data["weights"].values()), 1.0, atol=0.01)
    assert "annualized_volatility" in data["metrics"]
    assert "risk_contributions" in data

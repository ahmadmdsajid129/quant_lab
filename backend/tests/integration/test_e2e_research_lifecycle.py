import pytest
import numpy as np


def test_full_quantitative_research_lifecycle(client):
    """
    End-to-End Validation of the Complete Institutional Quantitative Research Lifecycle:
    Research Question -> Hypothesis -> Data -> Analytics -> Strategy -> Backtest ->
    Statistical Validation -> ML Lab -> Portfolio Opt -> LOB Simulation -> Options ->
    AI Copilot -> Paper Trading -> Tearsheet Report
    """
    # =========================================================================
    # STEP 1: Registration & Authentication
    # =========================================================================
    reg_res = client.post(
        "/api/v1/auth/register",
        json={
            "email": "chief_quant@quantlab.io",
            "password": "Password123!",
            "full_name": "Chief Quantitative Strategist",
        },
    )
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    token = user_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # =========================================================================
    # STEP 2: Project & Hypothesis Formulation
    # =========================================================================
    proj_res = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Cross-Asset Volatility Risk Premia",
            "description": "Exploiting structural variance premia across equity indices",
            "asset_class": "EQUITIES",
        },
    )
    assert proj_res.status_code == 201
    proj_id = proj_res.json()["id"]

    hypo_res = client.post(
        f"/api/v1/projects/{proj_id}/hypotheses",
        headers=headers,
        json={
            "statement": "Implied volatility consistently trades at a premium to realized volatility due to tail-risk hedging demand.",
            "mechanism": "Institutional downside insurance buying creates structural variance risk premium.",
            "predicted_outcome": "Annualized Sharpe ratio > 1.2 with max drawdown < 20%.",
            "falsification_criteria": "Net Sharpe ratio <= 0.3 after 5bps transaction friction or DSR p-value > 0.05.",
        },
    )
    assert hypo_res.status_code == 201

    # =========================================================================
    # STEP 3: Market Data Ingestion & 5-Point QA Audit
    # =========================================================================
    ds1_res = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "SPX-INDEX", "periods": 252, "initial_price": 5000.0, "seed": 42},
    )
    assert ds1_res.status_code == 201
    ds1_id = ds1_res.json()["id"]
    assert ds1_res.json()["quality_score"] == 100.0

    ds2_res = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "NDX-INDEX", "periods": 252, "initial_price": 18000.0, "seed": 99},
    )
    assert ds2_res.status_code == 201
    ds2_id = ds2_res.json()["id"]

    # =========================================================================
    # STEP 4: Exploratory Data Analytics (Moments, Stationarity, Autocorrelation)
    # =========================================================================
    eda_res = client.post(
        "/api/v1/analytics/summary",
        headers=headers,
        json={"dataset_id": ds1_id, "rolling_window": 20},
    )
    assert eda_res.status_code == 200
    eda = eda_res.json()
    assert eda["distribution"]["augmented_dickey_fuller"]["is_stationary"] is True
    assert len(eda["acf_lags"]) == 21
    assert eda["max_drawdown"] <= 0.0

    # =========================================================================
    # STEP 5: Event-Driven Backtest (Strict t -> t+1 Time Semantics)
    # =========================================================================
    bt_res = client.post(
        "/api/v1/backtests/run",
        headers=headers,
        json={
            "project_id": proj_id,
            "dataset_id": ds1_id,
            "strategy_name": "MA_CROSSOVER",
            "parameters": {"fast_window": 10, "slow_window": 30},
            "initial_cash": 100_000.0,
            "slippage_pct": 0.0005,
            "commission_bps": 2.0,
        },
    )
    assert bt_res.status_code == 201
    bt = bt_res.json()
    exp_id = bt["experiment_id"]
    lineage_hash = bt["lineage_hash"]
    assert len(lineage_hash) == 64
    assert len(bt["equity_curve"]) > 200
    assert "sharpe_ratio" in bt["metrics"]

    # =========================================================================
    # STEP 6: Statistical Validation Lab (DSR & Walk-Forward Efficiency)
    # =========================================================================
    val_dsr = client.post(
        "/api/v1/validation/deflated-sharpe",
        headers=headers,
        json={
            "observed_sharpe": bt["metrics"]["sharpe_ratio"],
            "track_length": len(bt["equity_curve"]),
            "num_trials": 15,
            "skewness": -0.2,
            "excess_kurtosis": 0.8,
        },
    )
    assert val_dsr.status_code == 200
    assert "deflated_sharpe_ratio" in val_dsr.json()

    # =========================================================================
    # STEP 7: Machine Learning Lab (Zero-Leakage Preprocessing & KS Drift)
    # =========================================================================
    ml_res = client.post(
        "/api/v1/ml/train",
        headers=headers,
        json={"dataset_id": ds1_id, "model_type": "GBDT", "train_ratio": 0.75},
    )
    assert ml_res.status_code == 200
    ml_report = ml_res.json()
    assert ml_report["metrics"]["accuracy_test"] > 0.0
    assert "concept_drift" in ml_report

    # =========================================================================
    # STEP 8: Portfolio Construction (Ledoit-Wolf & Euler Risk Decomposition)
    # =========================================================================
    port_res = client.post(
        "/api/v1/portfolio/optimize",
        headers=headers,
        json={
            "dataset_ids": [ds1_id, ds2_id],
            "method": "MAX_SHARPE",
            "covariance_method": "LEDOIT_WOLF",
            "risk_free_rate": 0.02,
        },
    )
    assert port_res.status_code == 200
    port = port_res.json()
    assert np.isclose(sum(port["weights"].values()), 1.0, atol=0.01)
    assert "risk_contributions" in port

    # =========================================================================
    # STEP 9: Market Microstructure & LOB Simulator
    # =========================================================================
    lob_res = client.post(
        "/api/v1/microstructure/simulate",
        headers=headers,
        json={"symbol": "BTC/USD", "initial_mid": 65000.0, "tick_size": 1.0, "num_events": 50, "seed": 42},
    )
    assert lob_res.status_code == 200
    lob = lob_res.json()
    assert lob["best_bid"] < lob["best_ask"]
    assert len(lob["bids"]) > 0

    # =========================================================================
    # STEP 10: Options & Derivatives Lab (Greeks & Put-Call Parity)
    # =========================================================================
    opt_res = client.post(
        "/api/v1/options/price",
        headers=headers,
        json={"spot": 100.0, "strike": 100.0, "expiry_days": 30.0, "rate": 0.02, "volatility": 0.25},
    )
    assert opt_res.status_code == 200
    opt = opt_res.json()
    assert opt["price"] > 0
    assert opt["put_call_parity_diff"] < 1e-4

    # =========================================================================
    # STEP 11: AI Research Copilot (Artifact-Grounded Reasoning)
    # =========================================================================
    copilot_res = client.post(
        "/api/v1/copilot/chat",
        headers=headers,
        json={"prompt": "Review my active research hypotheses and backtest performance."},
    )
    assert copilot_res.status_code == 200
    assert "Cross-Asset Volatility Risk Premia" in copilot_res.json()["response"]

    # =========================================================================
    # STEP 12: Paper Trading Simulation & Pre-Trade Risk
    # =========================================================================
    trade_res = client.post(
        "/api/v1/paper-trading/orders",
        headers=headers,
        json={"symbol": "SPX-INDEX", "side": "BUY", "quantity": 2.0, "price": 5000.0},
    )
    assert trade_res.status_code == 200
    acc_res = client.get("/api/v1/paper-trading/account", headers=headers)
    assert len(acc_res.json()["positions"]) == 1

    # =========================================================================
    # STEP 13: Institutional Research Tearsheet & Lineage Export
    # =========================================================================
    tear_res = client.get(f"/api/v1/reports/experiments/{exp_id}/tearsheet", headers=headers)
    assert tear_res.status_code == 200
    tear = tear_res.json()
    assert tear["lineage_hash"] == lineage_hash
    assert tear["data_provenance"]["symbol"] == "SPX-INDEX"

    md_export = client.get(f"/api/v1/reports/experiments/{exp_id}/export/markdown", headers=headers)
    assert md_export.status_code == 200
    assert "# Quantitative Research Tearsheet" in md_export.text

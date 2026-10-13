import pytest
from app.services.report_service import report_service


def test_reports_api_and_markdown_export(client):
    # 1. Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "reports_lead@quantlab.io", "password": "Password123!", "full_name": "Dr. Reports"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Project & Hypothesis
    proj = client.post(
        "/api/v1/projects",
        headers=headers,
        json={"title": "Alpha Research Project", "asset_class": "EQUITIES"},
    ).json()
    proj_id = proj["id"]

    client.post(
        f"/api/v1/projects/{proj_id}/hypotheses",
        headers=headers,
        json={
            "statement": "Trend following momentum captures risk premia",
            "mechanism": "Behavioral anchoring to past reference prices",
            "predicted_outcome": "Sharpe ratio exceeds benchmark by 0.5",
            "falsification_criteria": "Max drawdown exceeds 25% over 12 months",
        },
    )

    # 3. Create Dataset
    ds = client.post(
        "/api/v1/datasets/generate-synthetic",
        headers=headers,
        json={"symbol": "ALPHA-ETF", "periods": 150, "seed": 777},
    ).json()

    # 4. Run Backtest to produce Experiment
    bt_res = client.post(
        "/api/v1/backtests/run",
        headers=headers,
        json={
            "project_id": proj_id,
            "dataset_id": ds["id"],
            "strategy_name": "BUY_AND_HOLD",
            "initial_cash": 100_000.0,
            "slippage_pct": 0.0005,
            "commission_bps": 2.0,
        },
    ).json()
    exp_id = bt_res["experiment_id"]

    # 5. Fetch Tearsheet endpoint
    res_tear = client.get(f"/api/v1/reports/experiments/{exp_id}/tearsheet", headers=headers)
    assert res_tear.status_code == 200
    tear = res_tear.json()
    assert tear["experiment_id"] == exp_id
    assert tear["lineage_hash"] == bt_res["lineage_hash"]
    assert tear["data_provenance"]["symbol"] == "ALPHA-ETF"
    assert "sharpe_ratio" in tear["performance_kpis"]
    assert len(tear["project"]["hypotheses"]) == 1

    # 6. Fetch Markdown Export endpoint
    res_md = client.get(f"/api/v1/reports/experiments/{exp_id}/export/markdown", headers=headers)
    assert res_md.status_code == 200
    assert "text/markdown" in res_md.headers["content-type"]
    assert "# Quantitative Research Tearsheet" in res_md.text
    assert "ALPHA-ETF" in res_md.text

    # 7. Fetch JSON Export endpoint
    res_json = client.get(f"/api/v1/reports/experiments/{exp_id}/export/json", headers=headers)
    assert res_json.status_code == 200
    assert res_json.json()["experiment_id"] == exp_id

    # 8. 404 for invalid experiment
    res_404 = client.get("/api/v1/reports/experiments/invalid-uuid/tearsheet", headers=headers)
    assert res_404.status_code == 404

import pytest
from app.copilot.methodology import audit_research_methodology
from app.copilot.provider import copilot_engine
from app.copilot.context import assemble_workspace_research_context


def test_methodology_auditor_pitfalls():
    # 1. Unsound strategy with multiple pitfalls
    report_bad = audit_research_methodology(
        strategy_description="High-frequency momentum",
        slippage_pct=0.0,
        commission_bps=0.0,
        num_trials_tested=50,
        reported_sharpe=3.8,
        uses_chronological_split=False,
        execution_at_next_bar_open=False,
    )
    assert report_bad["is_methodologically_sound"] is False
    assert report_bad["methodology_health_score"] < 50
    assert report_bad["severity_summary"]["HIGH"] >= 3

    # 2. Institutional rigor strategy
    report_good = audit_research_methodology(
        strategy_description="Trend following",
        slippage_pct=0.0005,
        commission_bps=3.0,
        num_trials_tested=2,
        reported_sharpe=1.4,
        uses_chronological_split=True,
        execution_at_next_bar_open=True,
    )
    assert report_good["is_methodologically_sound"] is True
    assert report_good["methodology_health_score"] >= 90
    assert report_good["severity_summary"]["HIGH"] == 0


def test_copilot_grounded_evidence_extraction():
    fake_context = {
        "projects_count": 1,
        "projects": [
            {
                "id": "proj-1",
                "name": "Equity Momentum Lab",
                "hypotheses": [
                    {
                        "id": "hypo-1",
                        "statement": "12-1 momentum earns positive risk-adjusted excess returns.",
                        "economic_mechanism": "Underreaction to earnings announcements.",
                        "falsification_criteria": "Annualized Sharpe < 0.20 over 3 years.",
                        "status": "TESTING",
                    }
                ],
            }
        ],
        "datasets": [
            {"id": "ds-1", "symbol": "AAPL", "asset_class": "EQUITY", "total_bars": 500, "quality_flags": []}
        ],
        "recent_experiments": [
            {
                "id": "exp-1",
                "strategy_name": "MomentumBaseline",
                "status": "COMPLETED",
                "metrics": {"sharpe_ratio": 1.25, "max_drawdown": -0.15, "win_rate": 0.54},
                "created_at": "2026-10-13",
            }
        ],
    }

    # Prompt about hypothesis
    res_h = copilot_engine.generate_response("Review my project hypothesis and falsification criteria", fake_context)
    assert "Equity Momentum Lab" in res_h["response"]
    assert len(res_h["grounded_artifacts"]["hypotheses"]) > 0

    # Prompt about backtest
    res_b = copilot_engine.generate_response("What was the Sharpe ratio of my backtest?", fake_context)
    assert "1.25" in res_b["response"]
    assert len(res_b["grounded_artifacts"]["verified_results"]) > 0


def test_copilot_api_endpoints(client):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "copilot_researcher@quantlab.io", "password": "Password123!", "full_name": "Dr. Elena"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Chat endpoint
    res_chat = client.post(
        "/api/v1/copilot/chat",
        headers=headers,
        json={"prompt": "Suggest feature engineering pipeline for time series."},
    )
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert "response" in data
    assert "grounded_artifacts" in data

    # 2. Audit methodology endpoint
    res_audit = client.post(
        "/api/v1/copilot/audit-methodology",
        headers=headers,
        json={
            "strategy_description": "Mean reversion intraday",
            "slippage_pct": 0.0005,
            "commission_bps": 2.5,
            "num_trials_tested": 1,
            "reported_sharpe": 1.6,
            "uses_chronological_split": True,
            "execution_at_next_bar_open": True,
        },
    )
    assert res_audit.status_code == 200
    audit_data = res_audit.json()
    assert audit_data["is_methodologically_sound"] is True
    assert audit_data["methodology_health_score"] >= 80

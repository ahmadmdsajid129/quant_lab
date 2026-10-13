import pytest
from fastapi.testclient import TestClient


def test_research_project_and_hypothesis_lifecycle(client: TestClient):
    # 1. Register User A
    user_resp = client.post(
        "/api/v1/auth/register",
        json={"email": "elena@quantlab.io", "password": "PasswordElena123!", "full_name": "Elena Vance"},
    )
    assert user_resp.status_code == 201
    token = user_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create Research Project
    proj_resp = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Cross-Sectional Momentum in S&P 500",
            "description": "Investigating 12-month momentum with 1-month reversal skip",
            "asset_class": "EQUITIES",
        },
    )
    assert proj_resp.status_code == 201
    proj_data = proj_resp.json()
    assert proj_data["title"] == "Cross-Sectional Momentum in S&P 500"
    assert proj_data["status"] == "DRAFT"
    proj_id = proj_data["id"]

    # 3. Add Structured Hypothesis
    hypo_resp = client.post(
        f"/api/v1/projects/{proj_id}/hypotheses",
        headers=headers,
        json={
            "statement": "Stocks in the top decile of 12-1m past returns outperform bottom decile over next 21 trading days.",
            "mechanism": "Slow information diffusion by institutional investors creates underreaction to past earnings news.",
            "predicted_outcome": "Annualized Long-Short spread > 6.0% with annualized Sharpe ratio > 0.8.",
            "falsification_criteria": "Net Sharpe ratio <= 0.2 after 10bps transaction costs or Deflated Sharpe Ratio p-value > 0.05.",
        },
    )
    assert hypo_resp.status_code == 201
    hypo_data = hypo_resp.json()
    assert hypo_data["status"] == "UNTESTED"
    assert "mechanism" in hypo_data

    # 4. Add Research Note
    note_resp = client.post(
        f"/api/v1/projects/{proj_id}/notes",
        headers=headers,
        json={
            "title": "Literature Reference & Initial Notes",
            "content": "# Jegadeesh and Titman (1993)\nExcluding the most recent month avoids short-term bid-ask bounce reversals.",
        },
    )
    assert note_resp.status_code == 201

    # 5. Get Project Details
    detail_resp = client.get(f"/api/v1/projects/{proj_id}", headers=headers)
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["hypotheses_count"] == 1
    assert len(detail_data["hypotheses"]) == 1
    assert len(detail_data["notes"]) == 1

    # 6. Update Project Status
    upd_resp = client.put(
        f"/api/v1/projects/{proj_id}",
        headers=headers,
        json={"status": "IN_PROGRESS"},
    )
    assert upd_resp.status_code == 200
    assert upd_resp.json()["status"] == "IN_PROGRESS"


def test_project_cross_tenant_isolation(client: TestClient):
    # Register User A
    user_a = client.post(
        "/api/v1/auth/register",
        json={"email": "alice_p@quantlab.io", "password": "Password123!", "full_name": "Alice"},
    ).json()
    token_a = user_a["access_token"]

    # Register User B
    user_b = client.post(
        "/api/v1/auth/register",
        json={"email": "bob_p@quantlab.io", "password": "Password123!", "full_name": "Bob"},
    ).json()
    token_b = user_b["access_token"]

    # Alice creates Project A
    proj_a = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"title": "Alice Secret Alpha", "asset_class": "CRYPTO"},
    ).json()
    proj_a_id = proj_a["id"]

    # Bob attempts to access Alice's Project A -> MUST get 404 (Not found in Bob's workspace)
    resp = client.get(
        f"/api/v1/projects/{proj_a_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code == 404

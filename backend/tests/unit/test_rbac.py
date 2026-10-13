import pytest
from fastapi.testclient import TestClient


def test_multi_tenant_workspace_isolation(client: TestClient):
    # 1. Register User A
    user_a_resp = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@quantlab.io", "password": "PasswordAlice123!", "full_name": "Alice Quants"},
    )
    assert user_a_resp.status_code == 201
    token_a = user_a_resp.json()["access_token"]
    user_a_id = user_a_resp.json()["user"]["id"]
    ws_a_id = user_a_resp.json()["user"]["workspaces"][0]["id"]

    # 2. Register User B
    user_b_resp = client.post(
        "/api/v1/auth/register",
        json={"email": "bob@quantlab.io", "password": "PasswordBob123!", "full_name": "Bob Trader"},
    )
    assert user_b_resp.status_code == 201
    token_b = user_b_resp.json()["access_token"]
    ws_b_id = user_b_resp.json()["user"]["workspaces"][0]["id"]

    # 3. User A lists workspaces: should only see ws_a_id
    workspaces_a = client.get("/api/v1/workspaces", headers={"Authorization": f"Bearer {token_a}"}).json()
    ws_a_ids = [w["id"] for w in workspaces_a]
    assert ws_a_id in ws_a_ids
    assert ws_b_id not in ws_a_ids

    # 4. User A attempts to access members of User B's workspace -> MUST get 403 Forbidden
    forbidden_resp = client.get(
        f"/api/v1/workspaces/{ws_b_id}/members",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert forbidden_resp.status_code == 403

    # 5. User B invites User A as RESEARCHER to Workspace B
    invite_resp = client.post(
        f"/api/v1/workspaces/{ws_b_id}/members",
        headers={"Authorization": f"Bearer {token_b}"},
        json={"user_id": user_a_id, "role": "RESEARCHER"},
    )
    assert invite_resp.status_code == 201

    # 6. Now User A CAN view members of Workspace B
    allowed_resp = client.get(
        f"/api/v1/workspaces/{ws_b_id}/members",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert allowed_resp.status_code == 200
    members = allowed_resp.json()
    assert len(members) == 2

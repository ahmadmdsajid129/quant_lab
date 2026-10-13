import pytest
from fastapi.testclient import TestClient


def test_auth_registration_and_login(client: TestClient):
    email = "researcher@quantlab.io"
    password = "SuperSecretPassword123!"
    full_name = "Dr. Elena Vance"

    # 1. Register new user
    reg_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert reg_resp.status_code == 201, reg_resp.text
    data = reg_resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == email
    assert data["user"]["full_name"] == full_name
    assert len(data["user"]["workspaces"]) == 1
    assert data["user"]["workspaces"][0]["role"] == "ADMIN"
    token = data["access_token"]

    # 2. Duplicate registration fails
    dup_resp = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name},
    )
    assert dup_resp.status_code == 400

    # 3. Login with correct password
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == email

    # 4. Login with incorrect password fails
    bad_login = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword"},
    )
    assert bad_login.status_code == 401

    # 5. Access /me with token
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == email
    assert me_data["full_name"] == full_name

    # 6. Access /me without token fails
    no_auth_resp = client.get("/api/v1/auth/me")
    assert no_auth_resp.status_code == 401

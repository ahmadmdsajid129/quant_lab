import pytest
from app.services.paper_trading_service import paper_trading_service


def test_paper_trading_lifecycle(client):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "paper_trader@quantlab.io", "password": "Password123!", "full_name": "Paper Trader"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch initial account
    res_acc = client.get("/api/v1/paper-trading/account", headers=headers)
    assert res_acc.status_code == 200
    acc = res_acc.json()
    assert acc["initial_cash"] == 100_000.0
    assert acc["current_cash"] == 100_000.0
    assert len(acc["positions"]) == 0

    # 2. Execute BUY order (e.g. 10 shares of NVDA at $120)
    res_buy = client.post(
        "/api/v1/paper-trading/orders",
        headers=headers,
        json={"symbol": "NVDA", "side": "BUY", "quantity": 10.0, "price": 120.0},
    )
    assert res_buy.status_code == 200
    buy_ord = res_buy.json()
    assert buy_ord["status"] == "FILLED"
    assert buy_ord["filled_quantity"] == 10.0
    assert buy_ord["filled_price"] > 120.0  # Slippage applied

    # 3. Verify updated account and position
    res_acc2 = client.get("/api/v1/paper-trading/account", headers=headers)
    acc2 = res_acc2.json()
    assert acc2["current_cash"] < 100_000.0
    assert len(acc2["positions"]) == 1
    assert acc2["positions"][0]["symbol"] == "NVDA"
    assert acc2["positions"][0]["quantity"] == 10.0

    # 4. Pre-trade Risk Check: Try to SELL more than owned
    res_oversell = client.post(
        "/api/v1/paper-trading/orders",
        headers=headers,
        json={"symbol": "NVDA", "side": "SELL", "quantity": 25.0, "price": 125.0},
    )
    assert res_oversell.status_code == 400
    assert "Insufficient position" in res_oversell.json()["error"]["message"]

    # 5. Pre-trade Risk Check: Order notional exceeding $50k limit
    res_huge = client.post(
        "/api/v1/paper-trading/orders",
        headers=headers,
        json={"symbol": "BTC", "side": "BUY", "quantity": 1.0, "price": 60_000.0},
    )
    assert res_huge.status_code == 400
    assert "exceeds risk limit" in res_huge.json()["error"]["message"]

    # 6. SELL position
    res_sell = client.post(
        "/api/v1/paper-trading/orders",
        headers=headers,
        json={"symbol": "NVDA", "side": "SELL", "quantity": 10.0, "price": 125.0},
    )
    assert res_sell.status_code == 200

    # Verify position is closed
    res_acc3 = client.get("/api/v1/paper-trading/account", headers=headers)
    assert len(res_acc3.json()["positions"]) == 0

    # 7. Kill switch test
    res_kill = client.post("/api/v1/paper-trading/kill-switch", headers=headers)
    assert res_kill.status_code == 200
    assert res_kill.json()["status"] == "HALTED"

    # 8. Reset account test
    res_reset = client.post("/api/v1/paper-trading/reset", headers=headers)
    assert res_reset.status_code == 200
    assert res_reset.json()["current_cash"] == 100_000.0

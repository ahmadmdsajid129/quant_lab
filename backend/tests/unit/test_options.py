import pytest
import numpy as np
from app.engine.options.black_scholes import black_scholes_price, black_scholes_greeks
from app.engine.options.binomial_tree import crr_binomial_tree_price
from app.engine.options.implied_vol import compute_implied_volatility
from app.engine.options.payoffs import build_strategy_payoff


def test_black_scholes_pricing_and_put_call_parity():
    spot = 100.0
    strike = 100.0
    t = 1.0  # 1 year
    r = 0.05  # 5%
    vol = 0.20  # 20%
    q = 0.0

    call_px = black_scholes_price(spot, strike, t, r, vol, q, "CALL")
    put_px = black_scholes_price(spot, strike, t, r, vol, q, "PUT")

    # Known textbook result: for S=100, K=100, r=0.05, sigma=0.2, T=1, Call ~ 10.4506, Put ~ 5.5735
    assert abs(call_px - 10.4506) < 0.05
    assert abs(put_px - 5.5735) < 0.05

    # Put-Call Parity Exact Invariant: C - P == S*e^(-qT) - K*e^(-rT)
    lhs = call_px - put_px
    rhs = spot * np.exp(-q * t) - strike * np.exp(-r * t)
    assert abs(lhs - rhs) < 1e-7, "Put-Call parity must hold exactly"


def test_black_scholes_greeks_invariants():
    spot = 100.0
    strike = 100.0
    t = 0.5
    r = 0.03
    vol = 0.25

    c_greeks = black_scholes_greeks(spot, strike, t, r, vol, option_type="CALL")
    p_greeks = black_scholes_greeks(spot, strike, t, r, vol, option_type="PUT")

    # Delta invariants
    assert 0.0 < c_greeks["delta"] < 1.0
    assert -1.0 < p_greeks["delta"] < 0.0
    assert abs((c_greeks["delta"] - p_greeks["delta"]) - 1.0) < 1e-4

    # Gamma & Vega invariants (identical for Call & Put)
    assert c_greeks["gamma"] > 0.0
    assert abs(c_greeks["gamma"] - p_greeks["gamma"]) < 1e-6
    assert c_greeks["vega"] > 0.0
    assert abs(c_greeks["vega"] - p_greeks["vega"]) < 1e-4

    # Time decay
    assert c_greeks["theta"] < 0.0


def test_binomial_tree_convergence():
    spot = 100.0
    strike = 100.0
    t = 0.5
    r = 0.05
    vol = 0.30

    bs_price = black_scholes_price(spot, strike, t, r, vol, option_type="CALL")
    crr_price_50 = crr_binomial_tree_price(spot, strike, t, r, vol, steps=50, option_type="CALL")
    crr_price_200 = crr_binomial_tree_price(spot, strike, t, r, vol, steps=200, option_type="CALL")

    # CRR tree converges to continuous Black-Scholes as N increases
    assert abs(crr_price_200 - bs_price) < abs(crr_price_50 - bs_price) + 0.05
    assert abs(crr_price_200 - bs_price) < 0.05


def test_implied_volatility_inversion():
    spot = 150.0
    strike = 145.0
    t = 0.25
    r = 0.04
    true_vol = 0.35

    # Generate market price with true_vol = 35%
    mkt_price = black_scholes_price(spot, strike, t, r, true_vol, option_type="CALL")

    # Invert price back to implied vol
    solved_iv = compute_implied_volatility(mkt_price, spot, strike, t, r, option_type="CALL")
    assert solved_iv is not None
    assert abs(solved_iv - true_vol) < 1e-3


def test_options_strategy_payoffs():
    spot = 100.0
    report = build_strategy_payoff("BULL_CALL_SPREAD", spot=spot, volatility=0.25)
    assert report["strategy"] == "BULL_CALL_SPREAD"
    assert len(report["legs"]) == 2
    assert report["max_profit"] != "UNLIMITED"
    assert report["max_loss"] != "UNLIMITED"
    assert len(report["curve"]) == 50


def test_options_api_endpoints(client):
    # Register user
    user = client.post(
        "/api/v1/auth/register",
        json={"email": "options_trader@quantlab.io", "password": "Password123!", "full_name": "Trader Sarah"},
    ).json()
    token = user["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Price endpoint
    res_pr = client.post(
        "/api/v1/options/price",
        headers=headers,
        json={"spot": 100.0, "strike": 100.0, "expiry_days": 30.0, "rate": 0.02, "volatility": 0.20},
    )
    assert res_pr.status_code == 200
    data = res_pr.json()
    assert data["price"] > 0
    assert "greeks" in data
    assert data["put_call_parity_diff"] < 1e-4

    # 2. Implied vol endpoint
    res_iv = client.post(
        "/api/v1/options/implied-vol",
        headers=headers,
        json={"market_price": data["price"], "spot": 100.0, "strike": 100.0, "expiry_days": 30.0, "rate": 0.02},
    )
    assert res_iv.status_code == 200
    iv_data = res_iv.json()
    assert abs(iv_data["implied_volatility"] - 0.20) < 0.01

    # 3. Payoff endpoint
    res_po = client.post(
        "/api/v1/options/payoff",
        headers=headers,
        json={"strategy": "IRON_CONDOR", "spot": 100.0, "volatility": 0.20, "expiry_days": 30.0},
    )
    assert res_po.status_code == 200
    po_data = res_po.json()
    assert po_data["strategy"] == "IRON_CONDOR"
    assert len(po_data["legs"]) == 4

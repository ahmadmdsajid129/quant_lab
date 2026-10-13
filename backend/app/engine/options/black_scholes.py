from typing import Dict, Any, Tuple
import numpy as np
from scipy.stats import norm


def black_scholes_price(
    spot: float,
    strike: float,
    expiry_years: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
    option_type: str = "CALL",
) -> float:
    """
    Analytical Black-Scholes-Merton European option pricing.
    """
    if expiry_years <= 1e-6:
        # Intrinsic value at expiration
        if option_type.upper() == "CALL":
            return max(0.0, spot - strike)
        else:
            return max(0.0, strike - spot)

    if volatility <= 1e-6:
        discounted_strike = strike * np.exp(-rate * expiry_years)
        discounted_spot = spot * np.exp(-dividend_yield * expiry_years)
        if option_type.upper() == "CALL":
            return max(0.0, discounted_spot - discounted_strike)
        else:
            return max(0.0, discounted_strike - discounted_spot)

    d1 = (
        np.log(spot / strike)
        + (rate - dividend_yield + 0.5 * volatility**2) * expiry_years
    ) / (volatility * np.sqrt(expiry_years))
    d2 = d1 - volatility * np.sqrt(expiry_years)

    df_q = np.exp(-dividend_yield * expiry_years)
    df_r = np.exp(-rate * expiry_years)

    if option_type.upper() == "CALL":
        price = spot * df_q * norm.cdf(d1) - strike * df_r * norm.cdf(d2)
    elif option_type.upper() == "PUT":
        price = strike * df_r * norm.cdf(-d2) - spot * df_q * norm.cdf(-d1)
    else:
        raise ValueError(f"Invalid option_type '{option_type}'. Must be 'CALL' or 'PUT'.")

    return max(0.0, float(price))


def black_scholes_greeks(
    spot: float,
    strike: float,
    expiry_years: float,
    rate: float,
    volatility: float,
    dividend_yield: float = 0.0,
    option_type: str = "CALL",
) -> Dict[str, float]:
    """
    Compute first- and second-order analytical Black-Scholes Greeks:
    Delta, Gamma, Vega (per 1% vol), Theta (per calendar day), Rho (per 1% rate).
    """
    option_type = option_type.upper()
    if expiry_years <= 1e-6 or volatility <= 1e-6:
        delta = 1.0 if (option_type == "CALL" and spot > strike) else (-1.0 if (option_type == "PUT" and spot < strike) else 0.0)
        return {
            "price": black_scholes_price(spot, strike, expiry_years, rate, volatility, dividend_yield, option_type),
            "delta": delta,
            "gamma": 0.0,
            "vega": 0.0,
            "theta": 0.0,
            "rho": 0.0,
        }

    sqrt_t = np.sqrt(expiry_years)
    d1 = (
        np.log(spot / strike)
        + (rate - dividend_yield + 0.5 * volatility**2) * expiry_years
    ) / (volatility * sqrt_t)
    d2 = d1 - volatility * sqrt_t

    df_q = np.exp(-dividend_yield * expiry_years)
    df_r = np.exp(-rate * expiry_years)
    n_prime_d1 = norm.pdf(d1)

    price = black_scholes_price(spot, strike, expiry_years, rate, volatility, dividend_yield, option_type)

    if option_type == "CALL":
        delta = df_q * norm.cdf(d1)
        theta_ann = (
            - (spot * df_q * n_prime_d1 * volatility) / (2 * sqrt_t)
            - rate * strike * df_r * norm.cdf(d2)
            + dividend_yield * spot * df_q * norm.cdf(d1)
        )
        rho_ann = strike * expiry_years * df_r * norm.cdf(d2)
    else:
        delta = - df_q * norm.cdf(-d1)
        theta_ann = (
            - (spot * df_q * n_prime_d1 * volatility) / (2 * sqrt_t)
            + rate * strike * df_r * norm.cdf(-d2)
            - dividend_yield * spot * df_q * norm.cdf(-d1)
        )
        rho_ann = - strike * expiry_years * df_r * norm.cdf(-d2)

    # Gamma and Vega are identical for Calls and Puts
    gamma = (df_q * n_prime_d1) / (spot * volatility * sqrt_t)
    # Vega per 1% change in implied volatility
    vega = (spot * df_q * sqrt_t * n_prime_d1) / 100.0
    # Theta per 1 calendar day (1 / 365)
    theta_1d = theta_ann / 365.0
    # Rho per 1% change in interest rate
    rho_1pct = rho_ann / 100.0

    return {
        "price": round(price, 4),
        "delta": round(float(delta), 4),
        "gamma": round(float(gamma), 6),
        "vega": round(float(vega), 4),
        "theta": round(float(theta_1d), 4),
        "rho": round(float(rho_1pct), 4),
    }

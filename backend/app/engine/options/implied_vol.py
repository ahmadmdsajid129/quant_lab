from typing import Optional
from scipy.optimize import brentq
from app.engine.options.black_scholes import black_scholes_price


def compute_implied_volatility(
    market_price: float,
    spot: float,
    strike: float,
    expiry_years: float,
    rate: float,
    option_type: str = "CALL",
    dividend_yield: float = 0.0,
    min_vol: float = 0.001,
    max_vol: float = 5.0,
) -> Optional[float]:
    """
    Invert Black-Scholes formula using Brent's root-finding method
    to find implied volatility sigma such that BS(sigma) == market_price.
    """
    # Quick intrinsic check
    intrinsic = max(0.0, spot - strike if option_type.upper() == "CALL" else strike - spot)
    if market_price < intrinsic:
        return None

    def obj(sigma: float) -> float:
        return (
            black_scholes_price(
                spot=spot,
                strike=strike,
                expiry_years=expiry_years,
                rate=rate,
                volatility=sigma,
                dividend_yield=dividend_yield,
                option_type=option_type,
            )
            - market_price
        )

    try:
        f_min = obj(min_vol)
        f_max = obj(max_vol)
        if f_min * f_max > 0:
            return None  # No root in [0.001, 5.0]

        iv = brentq(obj, min_vol, max_vol, xtol=1e-5, maxiter=100)
        return round(float(iv), 4)
    except Exception:
        return None

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.db.models import User
from app.schemas.options import (
    OptionPriceRequest,
    OptionPriceResponse,
    ImpliedVolRequest,
    ImpliedVolResponse,
    StrategyPayoffRequest,
    StrategyPayoffResponse,
)
from app.engine.options.black_scholes import black_scholes_price, black_scholes_greeks
from app.engine.options.binomial_tree import crr_binomial_tree_price
from app.engine.options.implied_vol import compute_implied_volatility
from app.engine.options.payoffs import build_strategy_payoff

router = APIRouter(prefix="/options", tags=["Options & Derivatives Laboratory"])


@router.post("/price", response_model=OptionPriceResponse)
def calculate_option_price(
    request: OptionPriceRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate option fair value using Black-Scholes or Binomial Tree, along with exact Greeks and Put-Call parity check.
    """
    t_years = request.expiry_days / 365.0
    model = request.pricing_model.upper()

    # Calculate analytical Greeks via Black-Scholes
    greeks_dict = black_scholes_greeks(
        spot=request.spot,
        strike=request.strike,
        expiry_years=t_years,
        rate=request.rate,
        volatility=request.volatility,
        dividend_yield=request.dividend_yield,
        option_type=request.option_type,
    )

    if model == "BINOMIAL_TREE":
        price = crr_binomial_tree_price(
            spot=request.spot,
            strike=request.strike,
            expiry_years=t_years,
            rate=request.rate,
            volatility=request.volatility,
            steps=request.tree_steps,
            option_type=request.option_type,
            exercise_style=request.exercise_style,
            dividend_yield=request.dividend_yield,
        )
    else:
        price = greeks_dict["price"]

    # Put-Call Parity Check: C - P == S*e^(-qT) - K*e^(-rT)
    c_val = black_scholes_price(
        request.spot, request.strike, t_years, request.rate, request.volatility, request.dividend_yield, "CALL"
    )
    p_val = black_scholes_price(
        request.spot, request.strike, t_years, request.rate, request.volatility, request.dividend_yield, "PUT"
    )
    lhs = c_val - p_val
    rhs = (
        request.spot * np.exp(-request.dividend_yield * t_years)
        - request.strike * np.exp(-request.rate * t_years)
    )
    parity_diff = round(float(abs(lhs - rhs)), 6)

    return {
        "model_used": model,
        "exercise_style": request.exercise_style,
        "price": price,
        "greeks": greeks_dict,
        "put_call_parity_diff": parity_diff,
    }


@router.post("/implied-vol", response_model=ImpliedVolResponse)
def solve_implied_volatility(
    request: ImpliedVolRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Invert market option price using Brent's method to compute implied volatility.
    """
    t_years = request.expiry_days / 365.0
    iv = compute_implied_volatility(
        market_price=request.market_price,
        spot=request.spot,
        strike=request.strike,
        expiry_years=t_years,
        rate=request.rate,
        option_type=request.option_type,
    )
    return {
        "implied_volatility": iv,
        "market_price": request.market_price,
        "spot": request.spot,
        "strike": request.strike,
    }


@router.post("/payoff", response_model=StrategyPayoffResponse)
def generate_strategy_payoff(
    request: StrategyPayoffRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate terminal PnL profile across underlying prices for multi-leg option strategies.
    """
    t_years = request.expiry_days / 365.0
    try:
        report = build_strategy_payoff(
            strategy_name=request.strategy,
            spot=request.spot,
            rate=request.rate,
            volatility=request.volatility,
            expiry_years=t_years,
        )
        return report
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payoff computation failed: {str(exc)}",
        )

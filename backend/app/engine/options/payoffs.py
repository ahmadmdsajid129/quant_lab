from typing import List, Dict, Any, Tuple
import numpy as np
from app.engine.options.black_scholes import black_scholes_price


def build_strategy_payoff(
    strategy_name: str,
    spot: float,
    rate: float = 0.02,
    volatility: float = 0.25,
    expiry_years: float = 30.0 / 365.0,
    price_range_pct: float = 0.30,
    num_points: int = 50,
) -> Dict[str, Any]:
    """
    Generate PnL profiles across terminal underlying prices for options strategies.
    Computes both terminal payoff at expiration and theoretical value today.
    """
    strategy_name = strategy_name.upper()

    # Define standard leg configurations based on current spot
    # Each leg: (option_type, strike, position: +1 long / -1 short)
    legs: List[Tuple[str, float, float]] = []

    if strategy_name == "LONG_CALL":
        legs = [("CALL", round(spot, 2), 1.0)]
    elif strategy_name == "LONG_PUT":
        legs = [("PUT", round(spot, 2), 1.0)]
    elif strategy_name == "BULL_CALL_SPREAD":
        legs = [
            ("CALL", round(spot * 0.98, 2), 1.0),
            ("CALL", round(spot * 1.04, 2), -1.0),
        ]
    elif strategy_name == "BEAR_PUT_SPREAD":
        legs = [
            ("PUT", round(spot * 1.02, 2), 1.0),
            ("PUT", round(spot * 0.96, 2), -1.0),
        ]
    elif strategy_name == "LONG_STRADDLE":
        legs = [
            ("CALL", round(spot, 2), 1.0),
            ("PUT", round(spot, 2), 1.0),
        ]
    elif strategy_name == "LONG_STRANGLE":
        legs = [
            ("CALL", round(spot * 1.05, 2), 1.0),
            ("PUT", round(spot * 0.95, 2), 1.0),
        ]
    elif strategy_name == "IRON_CONDOR":
        legs = [
            ("PUT", round(spot * 0.90, 2), 1.0),
            ("PUT", round(spot * 0.95, 2), -1.0),
            ("CALL", round(spot * 1.05, 2), -1.0),
            ("CALL", round(spot * 1.10, 2), 1.0),
        ]
    else:
        raise ValueError(f"Unknown strategy '{strategy_name}'. Available: LONG_CALL, LONG_PUT, BULL_CALL_SPREAD, BEAR_PUT_SPREAD, LONG_STRADDLE, LONG_STRANGLE, IRON_CONDOR")

    # Initial net entry premium paid (+) or received (-)
    net_premium_paid = 0.0
    leg_summaries = []
    for opt_type, strike, pos in legs:
        leg_price = black_scholes_price(spot, strike, expiry_years, rate, volatility, option_type=opt_type)
        net_premium_paid += pos * leg_price
        leg_summaries.append({
            "type": opt_type,
            "strike": strike,
            "position": "LONG" if pos > 0 else "SHORT",
            "premium": round(leg_price, 4),
        })

    # Spot simulation grid
    min_spot = spot * (1.0 - price_range_pct)
    max_spot = spot * (1.0 + price_range_pct)
    spot_grid = np.linspace(min_spot, max_spot, num_points)

    payoff_curve = []
    for s_t in spot_grid:
        # Expiration terminal value
        terminal_val = 0.0
        for opt_type, strike, pos in legs:
            intrinsic = max(0.0, s_t - strike) if opt_type == "CALL" else max(0.0, strike - s_t)
            terminal_val += pos * intrinsic

        pnl_at_expiry = terminal_val - net_premium_paid
        payoff_curve.append({
            "underlying_price": round(float(s_t), 2),
            "pnl": round(float(pnl_at_expiry), 2),
        })

    # Key payoff characteristics
    pnls = [pt["pnl"] for pt in payoff_curve]
    max_profit = max(pnls)
    max_loss = min(pnls)

    return {
        "strategy": strategy_name,
        "spot": spot,
        "net_debit_credit": round(net_premium_paid, 4),
        "max_profit": round(max_profit, 2) if max_profit < 1e5 else "UNLIMITED",
        "max_loss": round(max_loss, 2) if abs(max_loss) < 1e5 else "UNLIMITED",
        "legs": leg_summaries,
        "curve": payoff_curve,
    }

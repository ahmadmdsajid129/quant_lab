from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from app.engine.backtest.metrics import compute_performance_metrics


def run_vectorized_backtest(
    prices: pd.Series,
    signals: pd.Series,
    initial_capital: float = 100_000.0,
    cost_per_trade_bps: float = 5.0,  # 5 bps
) -> Dict[str, Any]:
    """
    Vectorized matrix backtesting with non-negotiable next-bar execution shift:
    Strategy position at t+1 = Signal calculated at t.
    Zero look-ahead bias guaranteed.
    """
    clean_p = prices.dropna().astype(float)
    clean_s = signals.dropna().astype(float)

    # Align indexes
    aligned = pd.DataFrame({"price": clean_p, "signal": clean_s}).dropna()
    if len(aligned) < 2:
        raise ValueError("Insufficient observations for vectorized backtest")

    # Shift signals by 1: Decision at t executes at t+1
    position = aligned["signal"].shift(1).fillna(0.0)
    asset_returns = aligned["price"].pct_change().fillna(0.0)

    # Turnover for transaction costs
    turnover = (position - position.shift(1).fillna(0.0)).abs()
    cost_factor = cost_per_trade_bps / 10_000.0
    costs = turnover * cost_factor

    # Strategy net returns
    strategy_returns = (position * asset_returns) - costs

    # Cumulative equity curve
    equity_curve = initial_capital * (1.0 + strategy_returns).cumprod()

    metrics = compute_performance_metrics(equity_curve)
    cum_max = equity_curve.cummax()
    drawdowns = (equity_curve - cum_max) / cum_max

    return {
        "initial_capital": initial_capital,
        "final_capital": round(float(equity_curve.iloc[-1]), 2),
        "total_turnover": round(float(turnover.sum()), 2),
        "total_cost_drag": round(float(costs.sum() * initial_capital), 2),
        "metrics": metrics,
        "equity_curve": equity_curve.to_list(),
        "drawdowns": drawdowns.to_list(),
    }

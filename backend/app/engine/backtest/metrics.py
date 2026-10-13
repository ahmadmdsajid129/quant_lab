from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd


def compute_performance_metrics(
    equity_series: pd.Series,
    trade_pnls: Optional[List[float]] = None,
    risk_free_rate: float = 0.02,  # 2% annual risk-free rate
    periods_per_year: int = 252,
) -> Dict[str, Any]:
    """
    Compute rigorous financial performance and tail risk metrics:
    Handles zero volatility, invalid denominators, and missing values safely.
    """
    clean_equity = equity_series.dropna().astype(float).values
    n = len(clean_equity)
    if n < 2:
        return {
            "total_return": 0.0,
            "cagr": 0.0,
            "annualized_volatility": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "max_drawdown": 0.0,
            "calmar_ratio": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "total_trades": 0,
            "var_95": 0.0,
            "cvar_95": 0.0,
        }

    initial_nav = clean_equity[0]
    final_nav = clean_equity[-1]
    total_return = (final_nav - initial_nav) / initial_nav

    # CAGR calculation
    years = max(1e-4, n / periods_per_year)
    if final_nav > 0 and initial_nav > 0:
        cagr = (final_nav / initial_nav) ** (1.0 / years) - 1.0
    else:
        cagr = -1.0

    # Daily returns series
    daily_returns = np.diff(clean_equity) / clean_equity[:-1]
    
    # Volatility
    daily_vol = np.std(daily_returns, ddof=1) if len(daily_returns) > 1 else 0.0
    ann_vol = daily_vol * np.sqrt(periods_per_year)
    ann_mean = np.mean(daily_returns) * periods_per_year if len(daily_returns) > 0 else 0.0

    # Sharpe ratio with zero-volatility protection
    if ann_vol > 1e-8:
        sharpe = (ann_mean - risk_free_rate) / ann_vol
    else:
        sharpe = 0.0

    # Sortino ratio (downside deviation)
    downside_returns = daily_returns[daily_returns < 0]
    if len(downside_returns) > 1:
        downside_std = np.sqrt(np.mean(downside_returns ** 2)) * np.sqrt(periods_per_year)
        sortino = (ann_mean - risk_free_rate) / downside_std if downside_std > 1e-8 else 0.0
    else:
        sortino = sharpe if sharpe > 0 else 0.0

    # Drawdown series & Max Drawdown
    cum_max = np.maximum.accumulate(clean_equity)
    drawdowns = (clean_equity - cum_max) / cum_max
    max_dd = float(np.min(drawdowns))  # <= 0.0

    # Calmar ratio
    calmar = cagr / abs(max_dd) if abs(max_dd) > 1e-6 else 0.0

    # Tail Risk: VaR 95% and CVaR 95% (Historical daily)
    if len(daily_returns) >= 10:
        var_95 = float(np.percentile(daily_returns, 5.0))  # 5th percentile
        tail_losses = daily_returns[daily_returns <= var_95]
        cvar_95 = float(np.mean(tail_losses)) if len(tail_losses) > 0 else var_95
    else:
        var_95 = 0.0
        cvar_95 = 0.0

    # Trade-level statistics
    trade_pnls = trade_pnls or []
    total_trades = len(trade_pnls)
    if total_trades > 0:
        pnls = np.array(trade_pnls)
        wins = pnls[pnls > 0]
        losses = pnls[pnls < 0]
        win_rate = len(wins) / total_trades
        gross_profits = float(np.sum(wins)) if len(wins) > 0 else 0.0
        gross_losses = float(np.abs(np.sum(losses))) if len(losses) > 0 else 0.0
        profit_factor = gross_profits / gross_losses if gross_losses > 1e-6 else 999.0
        avg_win = float(np.mean(wins)) if len(wins) > 0 else 0.0
        avg_loss = float(np.abs(np.mean(losses))) if len(losses) > 0 else 0.0
        expectancy = (win_rate * avg_win) - ((1.0 - win_rate) * avg_loss)
    else:
        win_rate = 0.0
        profit_factor = 0.0
        avg_win = 0.0
        avg_loss = 0.0
        expectancy = 0.0

    return {
        "total_return": round(float(total_return), 4),
        "cagr": round(float(cagr), 4),
        "annualized_volatility": round(float(ann_vol), 4),
        "sharpe_ratio": round(float(sharpe), 4),
        "sortino_ratio": round(float(sortino), 4),
        "max_drawdown": round(float(max_dd), 4),
        "calmar_ratio": round(float(calmar), 4),
        "var_95_daily": round(float(var_95), 4),
        "cvar_95_daily": round(float(cvar_95), 4),
        "trade_metrics": {
            "total_trades": total_trades,
            "win_rate": round(float(win_rate), 4),
            "profit_factor": round(float(profit_factor), 4),
            "avg_win": round(float(avg_win), 2),
            "avg_loss": round(float(avg_loss), 2),
            "expectancy": round(float(expectancy), 2),
        },
    }

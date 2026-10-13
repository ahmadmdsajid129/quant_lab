from typing import Dict, Any, List
import numpy as np
import pandas as pd
from app.engine.strategy.base import BaseStrategy
from app.engine.backtest.event import EventBacktestEngine


def run_walk_forward_analysis(
    df: pd.DataFrame,
    strategy_factory,
    train_bars: int = 252,
    test_bars: int = 63,
    expanding: bool = False,
) -> Dict[str, Any]:
    """
    Chronological Walk-Forward Optimization & Validation:
    Trains on in-sample window, tests on out-of-sample window, advances forward.
    Computes Walk-Forward Efficiency (WFE): Sharpe_OOS / Sharpe_IS.
    """
    total_bars = len(df)
    min_required = train_bars + test_bars
    if total_bars < min_required:
        raise ValueError(f"Insufficient bars for walk forward: {total_bars} < {min_required}")

    windows: List[Dict[str, Any]] = []
    oos_equity_segments = []

    start_idx = 0
    engine = EventBacktestEngine(initial_capital=100_000.0)

    while start_idx + train_bars + test_bars <= total_bars:
        # In-sample train slice
        train_start = 0 if expanding else start_idx
        train_end = start_idx + train_bars
        train_df = df.iloc[train_start:train_end].copy().reset_index(drop=True)

        # Out-of-sample test slice
        test_start = train_end
        test_end = test_start + test_bars
        test_df = df.iloc[test_start:test_end].copy().reset_index(drop=True)

        # Run In-Sample
        strat_is = strategy_factory()
        res_is = engine.run(train_df, strat_is)
        sharpe_is = float(res_is["metrics"]["sharpe_ratio"])

        # Run Out-Of-Sample
        strat_oos = strategy_factory()
        res_oos = engine.run(test_df, strat_oos)
        sharpe_oos = float(res_oos["metrics"]["sharpe_ratio"])

        wfe = round(sharpe_oos / sharpe_is, 2) if sharpe_is > 1e-4 else 0.0

        windows.append({
            "window_index": len(windows) + 1,
            "train_start": str(train_df["timestamp"].iloc[0]),
            "train_end": str(train_df["timestamp"].iloc[-1]),
            "test_start": str(test_df["timestamp"].iloc[0]),
            "test_end": str(test_df["timestamp"].iloc[-1]),
            "sharpe_is": sharpe_is,
            "sharpe_oos": sharpe_oos,
            "walk_forward_efficiency": wfe,
            "oos_total_return": float(res_oos["metrics"]["total_return"]),
        })

        start_idx += test_bars

    mean_is = float(np.mean([w["sharpe_is"] for w in windows]))
    mean_oos = float(np.mean([w["sharpe_oos"] for w in windows]))
    overall_wfe = round(mean_oos / mean_is, 2) if mean_is > 1e-4 else 0.0

    return {
        "total_windows": len(windows),
        "mean_in_sample_sharpe": round(mean_is, 4),
        "mean_out_of_sample_sharpe": round(mean_oos, 4),
        "overall_walk_forward_efficiency": overall_wfe,
        "is_robust": bool(overall_wfe >= 0.50),
        "windows": windows,
    }

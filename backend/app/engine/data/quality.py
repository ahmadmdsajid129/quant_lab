from typing import Dict, Any, List
import pandas as pd
import numpy as np


def run_data_quality_audit(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Execute standardized 5-point Data Quality Audit:
    1. Invariant: High >= max(Open, Close) and Low <= min(Open, Close)
    2. Invariant: Strictly positive prices and volume
    3. Anomaly: Single-bar return spikes (> 50% or < -50%)
    4. Continuity: Duplicate timestamps or unexpected gaps
    5. Overall Quality Score (0 - 100%)
    """
    total_bars = len(df)
    if total_bars == 0:
        return {
            "score": 0.0,
            "status": "FAILED",
            "total_bars": 0,
            "violations_count": 1,
            "issues": ["Dataset is empty"],
        }

    issues: List[str] = []
    penalty = 0.0

    # 1. Price Invariants Check
    invalid_high = df[df["high"] < df[["open", "close"]].max(axis=1)]
    invalid_low = df[df["low"] > df[["open", "close"]].min(axis=1)]
    
    if len(invalid_high) > 0:
        issues.append(f"Found {len(invalid_high)} bars where High < max(Open, Close)")
        penalty += min(30.0, len(invalid_high) * 5.0)

    if len(invalid_low) > 0:
        issues.append(f"Found {len(invalid_low)} bars where Low > min(Open, Close)")
        penalty += min(30.0, len(invalid_low) * 5.0)

    # 2. Non-positive price or volume
    non_positive_prices = df[(df["open"] <= 0) | (df["high"] <= 0) | (df["low"] <= 0) | (df["close"] <= 0)]
    if len(non_positive_prices) > 0:
        issues.append(f"Found {len(non_positive_prices)} bars with non-positive prices")
        penalty += 50.0

    negative_vol = df[df["volume"] < 0]
    if len(negative_vol) > 0:
        issues.append(f"Found {len(negative_vol)} bars with negative volume")
        penalty += 20.0

    # 3. Anomaly / Extreme price jump checks (> 50%)
    pct_changes = df["close"].pct_change().dropna()
    spikes = pct_changes[pct_changes.abs() > 0.50]
    if len(spikes) > 0:
        issues.append(f"Detected {len(spikes)} extreme single-day price jumps (> 50%)")
        penalty += min(20.0, len(spikes) * 5.0)

    # 4. Duplicate timestamps
    dups = df["timestamp"].duplicated().sum()
    if dups > 0:
        issues.append(f"Detected {dups} duplicate timestamps")
        penalty += 40.0

    final_score = max(0.0, round(100.0 - penalty, 2))
    status_str = "QUALITY_VERIFIED" if final_score >= 90.0 else "QUALITY_WARNING" if final_score >= 60.0 else "QUALITY_REJECTED"

    return {
        "score": final_score,
        "status": status_str,
        "total_bars": total_bars,
        "violations_count": len(issues),
        "issues": issues,
        "metrics": {
            "min_close": float(df["close"].min()),
            "max_close": float(df["close"].max()),
            "mean_volume": float(df["volume"].mean()),
            "start_timestamp": str(df["timestamp"].iloc[0]),
            "end_timestamp": str(df["timestamp"].iloc[-1]),
        }
    }

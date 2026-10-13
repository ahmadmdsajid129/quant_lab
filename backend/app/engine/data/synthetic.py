from datetime import datetime, timedelta, timezone
from typing import List, Optional
import numpy as np
import pandas as pd


def generate_synthetic_ohlcv(
    symbol: str = "SYNTH",
    start_date: Optional[datetime] = None,
    periods: int = 252,  # ~1 trading year
    initial_price: float = 100.0,
    annual_drift: float = 0.08,
    annual_volatility: float = 0.20,
    jump_intensity: float = 0.05,
    jump_mean: float = 0.0,
    jump_std: float = 0.03,
    base_volume: float = 1_000_000.0,
    substeps_per_day: int = 40,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Generate realistic financial OHLCV bars using a Merton Jump-Diffusion model:
    dS_t = mu * S_t * dt + sigma * S_t * dW_t + J_t * S_t * dN_t
    
    Sub-day discretization ensures realistic High and Low values relative to Open and Close.
    Guaranteed deterministic output when seed is provided.
    """
    rng = np.random.default_rng(seed)
    
    if start_date is None:
        start_date = datetime(2023, 1, 3, 9, 30, tzinfo=timezone.utc)
    elif start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=timezone.utc)

    # Time steps setup
    dt = 1.0 / (252.0 * substeps_per_day)
    daily_dt = 1.0 / 252.0
    
    total_substeps = periods * substeps_per_day
    
    # Wiener increments
    dw = rng.normal(0, np.sqrt(dt), total_substeps)
    
    # Jump process (Poisson arrivals per sub-step)
    jump_prob = (jump_intensity * daily_dt) / substeps_per_day
    has_jump = rng.uniform(0, 1, total_substeps) < jump_prob
    jump_sizes = rng.normal(jump_mean, jump_std, total_substeps) * has_jump
    
    # Drift and diffusion drift adjustment
    drift_step = (annual_drift - 0.5 * (annual_volatility ** 2)) * dt
    diffusion_step = annual_volatility * dw
    
    # Log-returns path
    log_returns = drift_step + diffusion_step + jump_sizes
    price_path = np.zeros(total_substeps + 1)
    price_path[0] = initial_price
    price_path[1:] = initial_price * np.exp(np.cumsum(log_returns))
    
    # Aggregate sub-steps into daily OHLCV
    rows = []
    current_date = start_date
    
    for i in range(periods):
        sub_slice = price_path[i * substeps_per_day : (i + 1) * substeps_per_day + 1]
        
        o = float(sub_slice[0])
        c = float(sub_slice[-1])
        h = float(np.max(sub_slice))
        l = float(np.min(sub_slice))
        
        # Enforce analytical price sanity invariants
        h = max(h, o, c)
        l = min(l, o, c)
        
        # Volume with positive correlation to volatility/price range
        price_range_ratio = (h - l) / max(l, 1e-4)
        vol_multiplier = np.exp(rng.normal(0, 0.3)) * (1.0 + 5.0 * price_range_ratio)
        vol = float(np.round(base_volume * vol_multiplier))
        
        # Microprice VWAP estimate
        vwap = float(np.round(o * 0.2 + h * 0.2 + l * 0.2 + c * 0.4, 4))
        trades = int(max(100, rng.poisson(vol / 200)))
        
        rows.append({
            "timestamp": current_date,
            "symbol": symbol,
            "open": np.round(o, 4),
            "high": np.round(h, 4),
            "low": np.round(l, 4),
            "close": np.round(c, 4),
            "volume": vol,
            "vwap": vwap,
            "trades_count": trades,
        })
        
        # Advance by 1 day (skipping weekends)
        current_date += timedelta(days=1)
        while current_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
            current_date += timedelta(days=1)

    df = pd.DataFrame(rows)
    return df

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from app.engine.strategy.base import BaseStrategy


class BuyAndHoldStrategy(BaseStrategy):
    """Educational baseline: 100% passive long allocation."""
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(1.0, index=df.index)


class MovingAverageCrossoverStrategy(BaseStrategy):
    """
    Moving Average Crossover (Trend Following):
    Fast SMA > Slow SMA => Long (+1.0)
    Fast SMA <= Slow SMA => Flat (0.0) or Short (-1.0)
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast_period = int(self.parameters.get("fast_period", 20))
        slow_period = int(self.parameters.get("slow_period", 50))
        allow_short = bool(self.parameters.get("allow_short", False))

        close = df["close"]
        fast_ma = close.rolling(window=fast_period).mean()
        slow_ma = close.rolling(window=slow_period).mean()

        signal = pd.Series(0.0, index=df.index)
        signal[fast_ma > slow_ma] = 1.0
        if allow_short:
            signal[fast_ma < slow_ma] = -1.0

        # Replace NaN warmup periods with 0.0
        signal[:slow_period] = 0.0
        return signal


class MomentumStrategy(BaseStrategy):
    """
    Time-Series Momentum:
    Rate-of-Change ROC_L = (P_t - P_{t-L}) / P_{t-L} > 0 => Long
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        lookback = int(self.parameters.get("lookback_period", 60))
        allow_short = bool(self.parameters.get("allow_short", False))

        close = df["close"]
        roc = (close - close.shift(lookback)) / close.shift(lookback)

        signal = pd.Series(0.0, index=df.index)
        signal[roc > 0] = 1.0
        if allow_short:
            signal[roc < 0] = -1.0

        signal[:lookback] = 0.0
        return signal


class MeanReversionStrategy(BaseStrategy):
    """
    Bollinger Z-Score Mean Reversion:
    Z_score = (P_t - MA_w) / Std_w
    Z < -threshold => Oversold (Buy +1.0)
    Z > threshold => Overbought (Exit 0.0 or Short -1.0)
    """
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        window = int(self.parameters.get("window", 20))
        entry_threshold = float(self.parameters.get("entry_threshold", 2.0))
        allow_short = bool(self.parameters.get("allow_short", False))

        close = df["close"]
        ma = close.rolling(window=window).mean()
        std = close.rolling(window=window).std()
        z_score = (close - ma) / std.replace(0, np.nan)

        signal = pd.Series(0.0, index=df.index)
        signal[z_score < -entry_threshold] = 1.0
        if allow_short:
            signal[z_score > entry_threshold] = -1.0

        signal[:window] = 0.0
        return signal.ffill().fillna(0.0)


def get_strategy_by_name(name: str, parameters: Optional[Dict[str, Any]] = None) -> BaseStrategy:
    strategies = {
        "BUY_AND_HOLD": BuyAndHoldStrategy,
        "MA_CROSSOVER": MovingAverageCrossoverStrategy,
        "MOMENTUM": MomentumStrategy,
        "MEAN_REVERSION": MeanReversionStrategy,
    }
    cls = strategies.get(name.upper())
    if not cls:
        raise ValueError(f"Unknown strategy template '{name}'. Available: {list(strategies.keys())}")
    return cls(parameters)

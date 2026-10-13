from typing import Tuple, Dict, Any, List
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index without lookahead."""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.fillna(50.0)


def build_financial_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Construct standardized financial machine-learning feature matrix X and target y.
    
    Target y_t: Direction of bar t+1 relative to bar t:
    y_t = 1 if Close_{t+1} > Close_t else 0.
    
    All features in X_t use strictly observations <= t.
    """
    close = df["close"].astype(float)
    volume = df["volume"].astype(float)

    features = pd.DataFrame(index=df.index)

    # 1. Return Momentum features
    features["ret_1d"] = close.pct_change(1)
    features["ret_5d"] = close.pct_change(5)
    features["ret_20d"] = close.pct_change(20)

    # 2. Volatility features
    ret_1d = features["ret_1d"]
    features["vol_10d"] = ret_1d.rolling(window=10).std()
    features["vol_30d"] = ret_1d.rolling(window=30).std()

    # 3. Technical indicators
    features["rsi_14d"] = compute_rsi(close, period=14)
    ema_12 = close.ewm(span=12, adjust=False).mean()
    ema_26 = close.ewm(span=26, adjust=False).mean()
    features["macd"] = (ema_12 - ema_26) / close

    # 4. Volume momentum
    features["vol_ratio_20d"] = volume / volume.rolling(window=20).mean().replace(0, np.nan)

    # Forward 1-day target: y_t = (Close_{t+1} > Close_t)
    target = (close.shift(-1) > close).astype(int)

    # Align and drop boundary NaNs
    valid_idx = features.dropna().index.intersection(target.iloc[:-1].index)
    X = features.loc[valid_idx].copy()
    y = target.loc[valid_idx].copy()

    return X, y


def chronological_split_and_scale(
    X: pd.DataFrame,
    y: pd.Series,
    train_ratio: float = 0.75,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StandardScaler]:
    """
    Chronological partition with zero data leakage:
    Scaler fits EXCLUSIVELY on X_train. X_test is only transformed.
    """
    n = len(X)
    split_idx = int(n * train_ratio)

    X_train_raw = X.iloc[:split_idx].copy()
    X_test_raw = X.iloc[split_idx:].copy()
    y_train = y.iloc[:split_idx].copy()
    y_test = y.iloc[split_idx:].copy()

    # Fit scaler ONLY on train set
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train_raw),
        columns=X.columns,
        index=X_train_raw.index,
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test_raw),
        columns=X.columns,
        index=X_test_raw.index,
    )

    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

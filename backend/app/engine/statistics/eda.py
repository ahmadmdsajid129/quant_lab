from typing import Dict, Any, List
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, acf


def compute_returns_series(prices: pd.Series) -> pd.DataFrame:
    """Compute simple, logarithmic, and cumulative returns."""
    clean_prices = prices.dropna().astype(float)
    simple_ret = clean_prices.pct_change().dropna()
    log_ret = np.log(clean_prices / clean_prices.shift(1)).dropna()
    cum_ret = (1.0 + simple_ret).cumprod() - 1.0

    return pd.DataFrame({
        "simple_return": simple_ret,
        "log_return": log_ret,
        "cumulative_return": cum_ret,
    })


def compute_rolling_volatility(
    returns: pd.Series,
    window: int = 21,
    annualization_factor: float = np.sqrt(252.0),
) -> pd.Series:
    """Compute rolling annualized volatility."""
    clean_ret = returns.dropna().astype(float)
    return clean_ret.rolling(window=window).std() * annualization_factor


def compute_distribution_metrics(returns: pd.Series) -> Dict[str, Any]:
    """
    Compute rigorous statistical moments and stationarity diagnostics:
    - Mean, Standard Deviation (Annualized)
    - Skewness and Excess Kurtosis (Fisher)
    - Jarque-Bera Test for Normality
    - Augmented Dickey-Fuller (ADF) Test for Unit-Root Stationarity
    """
    clean_ret = returns.dropna().astype(float).values
    if len(clean_ret) < 10:
        raise ValueError("Insufficient sample size for distribution analytics (n < 10)")

    mean_daily = float(np.mean(clean_ret))
    std_daily = float(np.std(clean_ret, ddof=1))
    ann_mean = mean_daily * 252.0
    ann_std = std_daily * np.sqrt(252.0)

    skew = float(stats.skew(clean_ret))
    kurt = float(stats.kurtosis(clean_ret))  # Fisher excess kurtosis (0 for normal)

    # Jarque-Bera test
    jb_stat, jb_pval = stats.jarque_bera(clean_ret)

    # Augmented Dickey-Fuller test
    adf_res = adfuller(clean_ret, autolag="AIC")
    adf_stat = float(adf_res[0])
    adf_pval = float(adf_res[1])
    crit_vals = {k: float(v) for k, v in adf_res[4].items()}

    return {
        "count": len(clean_ret),
        "mean_daily": round(mean_daily, 6),
        "mean_annualized": round(ann_mean, 4),
        "std_daily": round(std_daily, 6),
        "std_annualized": round(ann_std, 4),
        "skewness": round(skew, 4),
        "excess_kurtosis": round(kurt, 4),
        "jarque_bera": {
            "statistic": round(float(jb_stat), 4),
            "p_value": round(float(jb_pval), 6),
            "is_normal": bool(jb_pval > 0.05),
        },
        "augmented_dickey_fuller": {
            "test_statistic": round(adf_stat, 4),
            "p_value": round(adf_pval, 6),
            "is_stationary": bool(adf_pval < 0.05),
            "critical_values": crit_vals,
        },
    }


def compute_autocorrelation(series: pd.Series, max_lag: int = 20) -> List[float]:
    """Compute Autocorrelation Function (ACF) up to max_lag."""
    clean = series.dropna().astype(float).values
    if len(clean) <= max_lag:
        max_lag = max(1, len(clean) // 2)
    acf_vals = acf(clean, nlags=max_lag, fft=True)
    return [round(float(x), 4) for x in acf_vals]


def compute_drawdown_series(prices: pd.Series) -> pd.DataFrame:
    """Compute running historical peak, drawdown percentage, and max drawdown."""
    clean = prices.dropna().astype(float)
    peak = clean.cummax()
    dd = (clean - peak) / peak
    return pd.DataFrame({
        "price": clean,
        "peak": peak,
        "drawdown": dd,
    })

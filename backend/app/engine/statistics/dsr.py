import numpy as np
from scipy import stats
from typing import Dict, Any


def compute_deflated_sharpe_ratio(
    observed_sharpe: float,
    track_length: int,
    skewness: float = 0.0,
    kurtosis: float = 3.0,  # Pearson kurtosis (3.0 for normal)
    num_trials: int = 1,
    sharpe_variance: float = 0.5,
) -> Dict[str, Any]:
    """
    Compute Deflated Sharpe Ratio (DSR) based on Bailey and López de Prado (2014):
    Adjusts Sharpe ratio for selection bias (multiple testing) and non-normality.
    
    Returns:
    - dsr_p_value: Prob(observed_SR > SR*) under null hypothesis of zero skill.
    - expected_max_sharpe: Hurdle SR* that must be exceeded given K trials.
    """
    if track_length <= 1:
        return {"dsr": 0.0, "p_value": 1.0, "hurdle": 0.0, "is_statistically_significant": False}

    num_trials = max(1, int(num_trials))
    euler_mascheroni = 0.57721566490153286

    # Expected maximum Sharpe under null hypothesis of zero skill across K trials
    if num_trials > 1:
        z_1 = stats.norm.ppf(1.0 - (1.0 / num_trials))
        z_2 = stats.norm.ppf(1.0 - (1.0 / (num_trials * np.e)))
        expected_max_sr = np.sqrt(sharpe_variance) * ((1.0 - euler_mascheroni) * z_1 + euler_mascheroni * z_2)
    else:
        expected_max_sr = 0.0

    # Standard error of the Sharpe ratio accounting for skewness and kurtosis
    # Var(SR) = (1 - skew * SR + (kurt - 1) / 4 * SR^2) / (T - 1)
    denom = 1.0 - skewness * observed_sharpe + ((kurtosis - 1.0) / 4.0) * (observed_sharpe ** 2)
    denom = max(1e-8, denom)
    std_error = np.sqrt(denom / (track_length - 1))

    # Test statistic z
    z_stat = (observed_sharpe - expected_max_sr) / std_error

    # DSR p-value: P(Z <= z_stat)
    dsr_val = float(stats.norm.cdf(z_stat))
    p_value = float(1.0 - dsr_val)

    return {
        "observed_sharpe": round(float(observed_sharpe), 4),
        "expected_max_sharpe_hurdle": round(float(expected_max_sr), 4),
        "num_trials_tested": num_trials,
        "track_length": track_length,
        "deflated_sharpe_ratio": round(dsr_val, 4),
        "p_value": round(p_value, 4),
        "is_statistically_significant": bool(p_value < 0.05),
    }

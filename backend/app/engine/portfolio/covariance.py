from typing import Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf


def compute_covariance_matrix(
    returns_df: pd.DataFrame,
    method: str = "LEDOIT_WOLF",
) -> Tuple[np.ndarray, float]:
    """
    Compute annualized asset covariance matrix using either:
    - 'SAMPLE': Empirical sample covariance
    - 'LEDOIT_WOLF': Optimal shrinkage towards constant correlation target
    
    Returns:
        (cov_matrix_annualized, shrinkage_intensity)
    """
    clean_returns = returns_df.dropna().values
    n_samples, n_assets = clean_returns.shape

    if n_samples < 5:
        raise ValueError(f"Insufficient observations ({n_samples}) for covariance estimation.")

    method = method.upper()
    if method == "SAMPLE":
        cov = np.cov(clean_returns, rowvar=False) * 252.0
        shrinkage = 0.0
    elif method == "LEDOIT_WOLF":
        lw = LedoitWolf()
        lw.fit(clean_returns)
        cov = lw.covariance_ * 252.0
        shrinkage = float(lw.shrinkage_)
    else:
        raise ValueError(f"Unknown covariance method '{method}'. Available: SAMPLE, LEDOIT_WOLF")

    # Ensure symmetric positive semi-definite
    cov = (cov + cov.T) / 2.0
    return cov, shrinkage


def compute_risk_contributions(
    weights: np.ndarray,
    cov_matrix: np.ndarray,
) -> Tuple[float, np.ndarray, np.ndarray]:
    """
    Decompose portfolio total volatility into marginal and percentage risk contributions.
    
    Portfolio Volatility: sigma_p = sqrt(w^T * Sigma * w)
    Marginal Risk Contribution (MRC): MRC_i = (Sigma * w)_i / sigma_p
    Risk Contribution (RC): RC_i = w_i * MRC_i
    Relative Risk Contribution (RRC): RRC_i = RC_i / sigma_p
    
    Invariant: sum(RC_i) == sigma_p
    """
    weights = np.asarray(weights, dtype=float)
    port_var = float(weights.T @ cov_matrix @ weights)
    port_vol = np.sqrt(max(port_var, 1e-12))

    # Marginal risk contribution
    mrc = (cov_matrix @ weights) / port_vol

    # Component risk contribution
    rc = weights * mrc

    # Percentage / relative contribution
    rrc = rc / port_vol if port_vol > 0 else np.zeros_like(rc)

    return port_vol, rc, rrc

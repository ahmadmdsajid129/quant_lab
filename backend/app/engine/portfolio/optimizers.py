from typing import Dict, Any, List, Optional
import numpy as np
from scipy.optimize import minimize
from app.engine.portfolio.covariance import compute_risk_contributions


def optimize_equal_weight(n_assets: int) -> np.ndarray:
    """Equal weight benchmark: w_i = 1 / N."""
    if n_assets <= 0:
        raise ValueError("Number of assets must be positive.")
    return np.ones(n_assets) / float(n_assets)


def optimize_inverse_volatility(cov_matrix: np.ndarray) -> np.ndarray:
    """Inverse volatility allocation: w_i propto 1 / sigma_i."""
    vols = np.sqrt(np.diag(cov_matrix))
    inv_vols = 1.0 / np.maximum(vols, 1e-8)
    return inv_vols / np.sum(inv_vols)


def optimize_minimum_variance(
    cov_matrix: np.ndarray,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> np.ndarray:
    """
    Global Minimum Variance (GMV) portfolio:
    min w^T * Sigma * w s.t. sum(w) = 1, min_w <= w_i <= max_w.
    """
    n = cov_matrix.shape[0]
    w0 = np.ones(n) / n
    bounds = [(min_weight, max_weight) for _ in range(n)]
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    def objective(w: np.ndarray) -> float:
        return float(w.T @ cov_matrix @ w)

    res = minimize(objective, w0, method="SLSQP", bounds=bounds, constraints=constraints)
    if not res.success:
        raise RuntimeError(f"Minimum Variance solver failed to converge: {res.message}")
    
    weights = np.maximum(res.x, 0.0)
    return weights / np.sum(weights)


def optimize_max_sharpe(
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.02,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
) -> np.ndarray:
    """
    Tangency portfolio maximizing Sharpe ratio:
    max (mu^T * w - r_f) / sqrt(w^T * Sigma * w) s.t. sum(w) = 1.
    """
    n = len(expected_returns)
    w0 = np.ones(n) / n
    bounds = [(min_weight, max_weight) for _ in range(n)]
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    def neg_sharpe(w: np.ndarray) -> float:
        port_ret = float(w @ expected_returns)
        port_vol = float(np.sqrt(max(w.T @ cov_matrix @ w, 1e-12)))
        return - (port_ret - risk_free_rate) / port_vol

    res = minimize(neg_sharpe, w0, method="SLSQP", bounds=bounds, constraints=constraints)
    if not res.success:
        raise RuntimeError(f"Max Sharpe solver failed to converge: {res.message}")

    weights = np.maximum(res.x, 0.0)
    return weights / np.sum(weights)


def optimize_risk_parity(
    cov_matrix: np.ndarray,
    max_iter: int = 500,
) -> np.ndarray:
    """
    Equal Risk Parity (ERP) solver:
    Finds weights such that each asset contributes exactly 1/N of total portfolio risk:
    min sum_i ( RC_i / sigma_p - 1/N )^2 s.t. sum(w) = 1, w_i >= 0.001.
    """
    n = cov_matrix.shape[0]
    w0 = np.ones(n) / n
    target_risk = 1.0 / n
    bounds = [(0.001, 1.0) for _ in range(n)]
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]

    def risk_budget_objective(w: np.ndarray) -> float:
        _, _, rrc = compute_risk_contributions(w, cov_matrix)
        return float(np.sum((rrc - target_risk) ** 2))

    res = minimize(
        risk_budget_objective,
        w0,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": max_iter, "ftol": 1e-9},
    )

    if not res.success:
        raise RuntimeError(f"Risk Parity solver failed to converge: {res.message}")

    weights = np.maximum(res.x, 0.0)
    return weights / np.sum(weights)


def optimize_portfolio(
    method: str,
    asset_names: List[str],
    expected_returns: np.ndarray,
    cov_matrix: np.ndarray,
    risk_free_rate: float = 0.02,
    min_weight: float = 0.0,
    max_weight: float = 1.0,
    current_weights: Optional[np.ndarray] = None,
    turnover_penalty_bps: float = 0.0,
) -> Dict[str, Any]:
    """
    Unified entry point for portfolio construction and risk analytics.
    """
    method = method.upper()
    n = len(asset_names)

    if method == "EQUAL_WEIGHT":
        weights = optimize_equal_weight(n)
    elif method == "INVERSE_VOL":
        weights = optimize_inverse_volatility(cov_matrix)
    elif method == "MIN_VARIANCE":
        weights = optimize_minimum_variance(cov_matrix, min_weight, max_weight)
    elif method == "MAX_SHARPE":
        weights = optimize_max_sharpe(expected_returns, cov_matrix, risk_free_rate, min_weight, max_weight)
    elif method == "RISK_PARITY":
        weights = optimize_risk_parity(cov_matrix)
    else:
        raise ValueError(
            f"Unknown portfolio optimization method '{method}'. "
            f"Available: EQUAL_WEIGHT, INVERSE_VOL, MIN_VARIANCE, MAX_SHARPE, RISK_PARITY"
        )

    # Compute risk breakdown
    port_ret = float(weights @ expected_returns)
    port_vol, rc, rrc = compute_risk_contributions(weights, cov_matrix)
    sharpe = float((port_ret - risk_free_rate) / port_vol) if port_vol > 0 else 0.0

    # Turnover if current weights provided
    turnover = 0.0
    turnover_cost = 0.0
    if current_weights is not None:
        turnover = float(0.5 * np.sum(np.abs(weights - current_weights)))
        turnover_cost = float(turnover * (turnover_penalty_bps / 10000.0))

    return {
        "method": method,
        "weights": {name: round(float(w), 4) for name, w in zip(asset_names, weights)},
        "metrics": {
            "expected_annual_return": round(port_ret, 4),
            "annualized_volatility": round(port_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "turnover": round(turnover, 4),
            "turnover_cost": round(turnover_cost, 6),
        },
        "risk_contributions": {
            name: {
                "risk_contribution_vol": round(float(c), 4),
                "relative_risk_pct": round(float(pct * 100.0), 2),
            }
            for name, c, pct in zip(asset_names, rc, rrc)
        },
    }

from typing import List, Dict, Any
import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_workspace
from app.db.models import User, Workspace, Dataset
from app.services.data_service import DataService
from app.schemas.portfolio import PortfolioOptimizeRequest, PortfolioOptimizeResponse
from app.engine.portfolio.covariance import compute_covariance_matrix
from app.engine.portfolio.optimizers import optimize_portfolio

router = APIRouter(prefix="/portfolio", tags=["Portfolio Optimization & Risk"])


@router.post("/optimize", response_model=PortfolioOptimizeResponse)
def run_portfolio_optimization(
    request: PortfolioOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Optimize multi-asset portfolio weights and compute Ledoit-Wolf risk attribution.
    """
    if len(request.dataset_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Portfolio optimization requires at least 2 distinct assets.",
        )

    # 1. Fetch datasets and load price histories
    datasets = (
        db.query(Dataset)
        .filter(
            Dataset.id.in_(request.dataset_ids),
            Dataset.workspace_id == workspace.id,
        )
        .all()
    )

    if len(datasets) != len(request.dataset_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more specified datasets could not be found in this workspace.",
        )

    prices_dict: Dict[str, pd.Series] = {}
    for ds in datasets:
        df = DataService.load_ohlcv(ds)
        if df is not None and not df.empty and "close" in df.columns:
            prices_dict[ds.symbol] = df["close"]

    if len(prices_dict) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 2 valid price series required for portfolio optimization.",
        )

    # 2. Align series and compute clean daily returns
    prices_df = pd.DataFrame(prices_dict).dropna()
    if len(prices_df) < 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient overlapping price observations across selected assets (minimum 20 required).",
        )

    returns_df = prices_df.pct_change().dropna()
    asset_symbols = list(returns_df.columns)

    # Annualized mean expected returns (sample mean x 252)
    expected_returns = returns_df.mean().values * 252.0

    # 3. Covariance matrix with optional Ledoit-Wolf shrinkage
    try:
        cov_matrix, shrinkage = compute_covariance_matrix(
            returns_df, method=request.covariance_method
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Covariance estimation failed: {str(exc)}",
        )

    # 4. Numerical Optimization Solver
    try:
        result = optimize_portfolio(
            method=request.method,
            asset_names=asset_symbols,
            expected_returns=expected_returns,
            cov_matrix=cov_matrix,
            risk_free_rate=request.risk_free_rate,
            min_weight=request.min_weight,
            max_weight=request.max_weight,
            turnover_penalty_bps=request.turnover_penalty_bps,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Portfolio optimization solver failed: {str(exc)}",
        )

    return {
        "method": result["method"],
        "covariance_method": request.covariance_method,
        "shrinkage_intensity": round(shrinkage, 4),
        "weights": result["weights"],
        "metrics": result["metrics"],
        "risk_contributions": result["risk_contributions"],
    }

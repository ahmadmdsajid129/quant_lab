from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Dataset, Workspace
from app.schemas.analytics import AnalyticsRequest, AnalyticsSummaryResponse
from app.services.data_service import DataService
from app.engine.statistics.eda import (
    compute_returns_series,
    compute_rolling_volatility,
    compute_distribution_metrics,
    compute_autocorrelation,
    compute_drawdown_series,
)
from app.core.deps import get_current_workspace

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.post("/summary", response_model=AnalyticsSummaryResponse)
def get_analytics_summary(
    req: AnalyticsRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """
    Compute full statistical EDA profile for a financial time series:
    Moments, Jarque-Bera normality, ADF stationarity, Autocorrelation, and Drawdowns.
    """
    dataset = db.query(Dataset).filter(
        Dataset.id == req.dataset_id,
        Dataset.workspace_id == workspace.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    df = DataService.load_ohlcv(dataset, start_date=req.start_date, end_date=req.end_date)
    if len(df) < 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset has too few bars for statistical analysis (minimum 15 required)",
        )

    prices = df["close"]
    returns_df = compute_returns_series(prices)
    returns = returns_df["simple_return"]

    # Rolling Volatility
    rolling_vol = compute_rolling_volatility(returns, window=req.rolling_window)
    current_vol = float(rolling_vol.dropna().iloc[-1]) if len(rolling_vol.dropna()) > 0 else 0.0

    # Moments & Stationarity Diagnostics
    dist_metrics = compute_distribution_metrics(returns)

    # Autocorrelation
    acf_vals = compute_autocorrelation(returns, max_lag=20)

    # Drawdown
    dd_df = compute_drawdown_series(prices)
    max_dd = float(dd_df["drawdown"].min())

    return AnalyticsSummaryResponse(
        dataset_id=dataset.id,
        symbol=dataset.symbol,
        total_bars=len(df),
        distribution=dist_metrics,
        acf_lags=acf_vals,
        max_drawdown=round(max_dd, 4),
        current_annualized_volatility=round(current_vol, 4),
    )

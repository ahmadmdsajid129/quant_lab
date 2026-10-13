from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Dataset, Workspace
from app.schemas.validation import DSRRequest, DSRResponse, WalkForwardRequest
from app.services.data_service import DataService
from app.engine.strategy.templates import get_strategy_by_name
from app.engine.statistics.dsr import compute_deflated_sharpe_ratio
from app.engine.statistics.walk_forward import run_walk_forward_analysis
from app.core.deps import get_current_workspace

router = APIRouter(prefix="/validation", tags=["validation"])


@router.post("/deflated-sharpe", response_model=DSRResponse)
def calculate_dsr(req: DSRRequest):
    """
    Calculate the Deflated Sharpe Ratio (DSR) based on Bailey & López de Prado (2014).
    Penalizes Sharpe ratio for selection bias from multiple parameter trials and non-normality.
    """
    res = compute_deflated_sharpe_ratio(
        observed_sharpe=req.observed_sharpe,
        track_length=req.track_length,
        skewness=req.skewness,
        kurtosis=req.excess_kurtosis + 3.0,  # Convert Fisher excess kurtosis to Pearson
        num_trials=req.num_trials,
        sharpe_variance=req.sharpe_variance,
    )
    return DSRResponse(**res)


@router.post("/walk-forward")
def execute_walk_forward(
    req: WalkForwardRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """
    Execute out-of-sample walk-forward analysis with rolling/expanding train windows.
    Returns Walk-Forward Efficiency (WFE) score and window breakdown.
    """
    dataset = db.query(Dataset).filter(
        Dataset.id == req.dataset_id,
        Dataset.workspace_id == workspace.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    df = DataService.load_ohlcv(dataset)
    if len(df) < req.train_bars + req.test_bars:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset has {len(df)} bars, which is insufficient for train ({req.train_bars}) + test ({req.test_bars})",
        )

    strategy_factory = lambda: get_strategy_by_name(req.strategy_type, req.parameters)

    try:
        results = run_walk_forward_analysis(
            df=df,
            strategy_factory=strategy_factory,
            train_bars=req.train_bars,
            test_bars=req.test_bars,
            expanding=req.expanding,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

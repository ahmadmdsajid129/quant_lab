from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_workspace
from app.db.models import User, Workspace, Dataset
from app.services.data_service import DataService
from app.schemas.ml import MLTrainRequest, MLTrainResponse
from app.engine.ml.features import build_financial_features, chronological_split_and_scale
from app.engine.ml.models import train_and_evaluate_model

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/features", response_model=List[Dict[str, str]])
def list_available_features(
    current_user: User = Depends(get_current_user),
):
    """Return available feature definitions in the standardized ML pipeline."""
    return [
        {"name": "ret_1d", "category": "Momentum", "description": "1-day close-to-close return"},
        {"name": "ret_5d", "category": "Momentum", "description": "5-day rolling cumulative return"},
        {"name": "ret_20d", "category": "Momentum", "description": "20-day rolling monthly return"},
        {"name": "vol_10d", "category": "Volatility", "description": "10-day rolling return standard deviation"},
        {"name": "vol_30d", "category": "Volatility", "description": "30-day rolling return standard deviation"},
        {"name": "rsi_14d", "category": "Oscillator", "description": "14-day Wilder Relative Strength Index"},
        {"name": "macd", "category": "Trend", "description": "Normalized Moving Average Convergence Divergence"},
        {"name": "vol_ratio_20d", "category": "Volume", "description": "Volume relative to 20-day moving average"},
    ]


@router.post("/train", response_model=MLTrainResponse)
def train_financial_model(
    request: MLTrainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Train a supervised financial ML model with chronological scaling and drift testing.
    """
    dataset = db.query(Dataset).filter(
        Dataset.id == request.dataset_id,
        Dataset.workspace_id == workspace.id,
    ).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found",
        )

    df = DataService.load_ohlcv(dataset)
    if df is None or len(df) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset contains insufficient observations (minimum 50 required for ML).",
        )

    # 1. Feature Engineering
    X, y = build_financial_features(df)
    if len(X) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient valid sample size after alignment and indicator warmup.",
        )

    # 2. Optional feature subselection
    if request.features_selected:
        valid_cols = [c for c in request.features_selected if c in X.columns]
        if valid_cols:
            X = X[valid_cols]

    # 3. Chronological split & Train-only scaling (zero data leakage)
    X_train, X_test, y_train, y_test, _ = chronological_split_and_scale(
        X, y, train_ratio=request.train_ratio
    )

    # 4. Fit & Diagnostics
    try:
        report = train_and_evaluate_model(
            X_train, X_test, y_train, y_test, model_type=request.model_type
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model training failed: {str(exc)}",
        )

    return report

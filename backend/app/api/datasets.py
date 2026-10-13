from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Dataset, Workspace
from app.schemas.datasets import (
    DatasetResponse,
    SyntheticGenerateRequest,
    OHLCVBarResponse,
)
from app.services.data_service import DataService
from app.core.deps import get_current_workspace

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.get("", response_model=List[DatasetResponse])
def list_datasets(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """List all market datasets available in active workspace."""
    datasets = db.query(Dataset).filter(Dataset.workspace_id == workspace.id).all()
    return [DatasetResponse.model_validate(d) for d in datasets]


@router.post("/generate-synthetic", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def generate_synthetic(
    req: SyntheticGenerateRequest,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """
    Generate and persist a reproducible synthetic jump-diffusion market dataset.
    Guaranteed reproducible output based on random seed.
    """
    dataset = DataService.create_synthetic_dataset(
        db=db,
        workspace_id=workspace.id,
        symbol=req.symbol,
        periods=req.periods,
        initial_price=req.initial_price,
        annual_drift=req.annual_drift,
        annual_volatility=req.annual_volatility,
        seed=req.seed,
    )
    return DatasetResponse.model_validate(dataset)


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Retrieve metadata and quality audit for a specific dataset."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.workspace_id == workspace.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return DatasetResponse.model_validate(dataset)


@router.get("/{dataset_id}/ohlcv", response_model=List[OHLCVBarResponse])
def get_dataset_ohlcv(
    dataset_id: str,
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    limit: Optional[int] = Query(1000, le=5000),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Fetch paginated OHLCV bars directly from high-throughput columnar Parquet storage."""
    dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.workspace_id == workspace.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    try:
        df = DataService.load_ohlcv(dataset, start_date=start_date, end_date=end_date, limit=limit)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parquet data file missing")

    # Convert to schema
    records = df.to_dict(orient="records")
    return [OHLCVBarResponse(**r) for r in records]

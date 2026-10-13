from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class SyntheticGenerateRequest(BaseModel):
    symbol: str = Field("SYNTH", min_length=1, max_length=20)
    periods: int = Field(504, ge=20, le=5000, description="Number of trading bars (252 ~ 1 year)")
    initial_price: float = Field(100.0, gt=0.0)
    annual_drift: float = Field(0.08, description="Annualized drift mu (e.g. 0.08 for 8%)")
    annual_volatility: float = Field(0.20, gt=0.0, description="Annualized volatility sigma (e.g. 0.20 for 20%)")
    seed: int = Field(42, description="Random seed for exact deterministic reproducibility")


class OHLCVBarResponse(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    trades_count: Optional[int] = None


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    symbol: str
    name: str
    source: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    total_bars: int
    quality_score: float
    quality_audit: Dict[str, Any]
    created_at: datetime


class DatasetDetailResponse(DatasetResponse):
    bars: List[OHLCVBarResponse] = []

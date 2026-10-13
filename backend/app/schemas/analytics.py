from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class AnalyticsRequest(BaseModel):
    dataset_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    rolling_window: int = Field(21, ge=5, le=252)


class AnalyticsSummaryResponse(BaseModel):
    dataset_id: str
    symbol: str
    total_bars: int
    distribution: Dict[str, Any]
    acf_lags: List[float]
    max_drawdown: float
    current_annualized_volatility: float

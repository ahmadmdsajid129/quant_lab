from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class DSRRequest(BaseModel):
    observed_sharpe: float
    track_length: int = Field(252, ge=10)
    skewness: float = Field(0.0)
    excess_kurtosis: float = Field(0.0)
    num_trials: int = Field(1, ge=1, description="Number of backtests / parameter sets evaluated")
    sharpe_variance: float = Field(0.5, gt=0.0)


class DSRResponse(BaseModel):
    observed_sharpe: float
    expected_max_sharpe_hurdle: float
    num_trials_tested: int
    track_length: int
    deflated_sharpe_ratio: float
    p_value: float
    is_statistically_significant: bool


class WalkForwardRequest(BaseModel):
    dataset_id: str
    strategy_type: str = "MA_CROSSOVER"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    train_bars: int = Field(252, ge=50)
    test_bars: int = Field(63, ge=10)
    expanding: bool = False

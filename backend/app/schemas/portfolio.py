from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class PortfolioOptimizeRequest(BaseModel):
    dataset_ids: List[str] = Field(..., min_length=2, description="List of dataset IDs to include in portfolio")
    method: str = Field(
        default="MAX_SHARPE",
        description="Optimization method: EQUAL_WEIGHT, INVERSE_VOL, MIN_VARIANCE, MAX_SHARPE, RISK_PARITY",
    )
    covariance_method: str = Field(
        default="LEDOIT_WOLF",
        description="Covariance estimator: SAMPLE, LEDOIT_WOLF",
    )
    risk_free_rate: float = Field(default=0.02, description="Annual risk-free rate")
    min_weight: float = Field(default=0.0, ge=0.0, le=0.5, description="Minimum asset weight bound")
    max_weight: float = Field(default=1.0, ge=0.1, le=1.0, description="Maximum asset weight bound")
    turnover_penalty_bps: float = Field(default=10.0, ge=0.0, description="Turnover transaction cost penalty in basis points")


class AssetRiskDetail(BaseModel):
    risk_contribution_vol: float
    relative_risk_pct: float


class PortfolioMetrics(BaseModel):
    expected_annual_return: float
    annualized_volatility: float
    sharpe_ratio: float
    turnover: float
    turnover_cost: float


class PortfolioOptimizeResponse(BaseModel):
    method: str
    covariance_method: str
    shrinkage_intensity: float
    weights: Dict[str, float]
    metrics: PortfolioMetrics
    risk_contributions: Dict[str, AssetRiskDetail]

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


class OptionPriceRequest(BaseModel):
    spot: float = Field(..., gt=0.0)
    strike: float = Field(..., gt=0.0)
    expiry_days: float = Field(default=30.0, gt=0.0)
    rate: float = Field(default=0.02)
    volatility: float = Field(default=0.25, gt=0.0)
    dividend_yield: float = Field(default=0.0, ge=0.0)
    option_type: str = Field(default="CALL", description="CALL or PUT")
    pricing_model: str = Field(default="BLACK_SCHOLES", description="BLACK_SCHOLES or BINOMIAL_TREE")
    exercise_style: str = Field(default="EUROPEAN", description="EUROPEAN or AMERICAN")
    tree_steps: int = Field(default=100, ge=10, le=500)


class OptionGreeks(BaseModel):
    price: float
    delta: float
    gamma: float
    vega: float
    theta: float
    rho: float


class OptionPriceResponse(BaseModel):
    model_used: str
    exercise_style: str
    price: float
    greeks: OptionGreeks
    put_call_parity_diff: Optional[float] = None


class ImpliedVolRequest(BaseModel):
    market_price: float = Field(..., gt=0.0)
    spot: float = Field(..., gt=0.0)
    strike: float = Field(..., gt=0.0)
    expiry_days: float = Field(default=30.0, gt=0.0)
    rate: float = Field(default=0.02)
    option_type: str = Field(default="CALL")


class ImpliedVolResponse(BaseModel):
    implied_volatility: Optional[float]
    market_price: float
    spot: float
    strike: float


class StrategyPayoffRequest(BaseModel):
    strategy: str = Field(default="BULL_CALL_SPREAD")
    spot: float = Field(default=100.0, gt=0.0)
    volatility: float = Field(default=0.25, gt=0.0)
    expiry_days: float = Field(default=30.0, gt=0.0)
    rate: float = Field(default=0.02)


class PayoffPoint(BaseModel):
    underlying_price: float
    pnl: float


class StrategyPayoffResponse(BaseModel):
    strategy: str
    spot: float
    net_debit_credit: float
    max_profit: Union[float, str]
    max_loss: Union[float, str]
    legs: List[Dict[str, Any]]
    curve: List[PayoffPoint]

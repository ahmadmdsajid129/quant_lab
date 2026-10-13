from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class BacktestRunRequest(BaseModel):
    project_id: str
    dataset_id: str
    strategy_type: str = Field("MA_CROSSOVER", description="BUY_AND_HOLD, MA_CROSSOVER, MOMENTUM, MEAN_REVERSION")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    initial_capital: float = Field(100_000.0, gt=0.0)
    commission_bps: float = Field(5.0, ge=0.0, description="Commission in basis points (5 bps = 0.05%)")
    slippage_pct: float = Field(0.05, ge=0.0, description="Execution slippage percentage")
    borrow_rate_annual: float = Field(0.02, ge=0.0, description="Annual short borrow financing rate")


class EquityPoint(BaseModel):
    timestamp: str
    equity: float
    drawdown: float


class TradeLogResponse(BaseModel):
    symbol: str
    entry_time: Union[datetime, str]
    exit_time: Union[datetime, str]
    side: str
    quantity: float
    entry_price: float
    exit_price: float
    gross_pnl: float
    fees: float
    net_pnl: float
    return_pct: float


class BacktestResultResponse(BaseModel):
    experiment_id: str
    project_id: str
    dataset_id: str
    strategy_type: str
    status: str
    lineage_hash: str
    initial_capital: float
    final_capital: float
    total_fees_paid: float
    metrics: Dict[str, Any]
    equity_curve: List[EquityPoint] = []
    trade_logs: List[TradeLogResponse] = []

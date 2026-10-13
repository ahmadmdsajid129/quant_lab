from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ProjectSummary(BaseModel):
    id: str
    title: str
    asset_class: str
    hypotheses: List[Dict[str, Any]]


class DataProvenance(BaseModel):
    symbol: str
    source: str
    total_bars: int
    start_date: str
    end_date: str
    quality_score: float


class MethodologyAssumptions(BaseModel):
    execution_timing: str
    lookahead_bias_guarantee: str
    slippage_rate: float
    commission_bps: float
    initial_cash: float


class PerformanceKPIs(BaseModel):
    total_return_pct: float
    cagr_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    calmar_ratio: float
    win_rate_pct: float
    profit_factor: float
    var_95_pct: float
    cvar_95_pct: float
    total_trades: int


class TearsheetResponse(BaseModel):
    title: str
    experiment_id: str
    status: str
    lineage_hash: str
    created_at: str
    project: ProjectSummary
    data_provenance: DataProvenance
    methodology_assumptions: MethodologyAssumptions
    performance_kpis: PerformanceKPIs
    reproducibility_notice: str

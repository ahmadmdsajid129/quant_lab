from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class CopilotChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    project_id: Optional[str] = None


class GroundedArtifacts(BaseModel):
    verified_results: List[str]
    statistical_inferences: List[str]
    hypotheses: List[str]


class CopilotChatResponse(BaseModel):
    response: str
    grounded_artifacts: GroundedArtifacts
    source_projects_count: int
    source_datasets_count: int
    source_experiments_count: int


class AuditMethodologyRequest(BaseModel):
    strategy_description: str = Field(...)
    slippage_pct: float = Field(default=0.0)
    commission_bps: float = Field(default=0.0)
    num_trials_tested: int = Field(default=1)
    reported_sharpe: float = Field(default=1.0)
    uses_chronological_split: bool = Field(default=True)
    execution_at_next_bar_open: bool = Field(default=True)


class FindingDetail(BaseModel):
    category: str
    severity: str
    title: str
    description: str


class AuditMethodologyResponse(BaseModel):
    is_methodologically_sound: bool
    methodology_health_score: int
    severity_summary: Dict[str, int]
    findings: List[FindingDetail]
    recommended_next_experiments: List[str]

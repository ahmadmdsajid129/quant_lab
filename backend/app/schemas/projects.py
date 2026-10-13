from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class HypothesisCreate(BaseModel):
    statement: str = Field(..., min_length=5, description="Core hypothesis statement")
    mechanism: str = Field(..., min_length=5, description="Economic / market mechanism explaining hypothesis")
    predicted_outcome: str = Field(..., min_length=5, description="Specific quantifiable outcome")
    falsification_criteria: str = Field(..., min_length=5, description="Criteria under which hypothesis is rejected")


class HypothesisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    statement: str
    mechanism: str
    predicted_outcome: str
    falsification_criteria: str
    status: str
    created_at: datetime


class ResearchNoteCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    content: str = Field(..., min_length=1, description="Markdown research content")


class ResearchNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    user_id: str
    title: str
    content: str
    created_at: datetime


class ProjectCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    asset_class: str = Field("EQUITIES", pattern="^(EQUITIES|CRYPTO|FX|DERIVATIVES|MULTI_ASSET)$")


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(DRAFT|IN_PROGRESS|VALIDATED|REJECTED|ARCHIVED)$")


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    title: str
    description: Optional[str] = None
    asset_class: str
    status: str
    created_at: datetime
    updated_at: datetime
    hypotheses_count: int = 0
    experiments_count: int = 0


class ProjectDetailResponse(ProjectResponse):
    hypotheses: List[HypothesisResponse] = []
    notes: List[ResearchNoteResponse] = []

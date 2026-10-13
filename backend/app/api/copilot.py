from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_workspace
from app.db.models import User, Workspace
from app.schemas.copilot import (
    CopilotChatRequest,
    CopilotChatResponse,
    AuditMethodologyRequest,
    AuditMethodologyResponse,
)
from app.copilot.context import assemble_workspace_research_context
from app.copilot.provider import copilot_engine
from app.copilot.methodology import audit_research_methodology

router = APIRouter(prefix="/copilot", tags=["AI Research Copilot"])


@router.post("/chat", response_model=CopilotChatResponse)
def copilot_chat(
    request: CopilotChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Submit a prompt to the AI Research Copilot with active workspace artifact grounding.
    """
    context = assemble_workspace_research_context(db, workspace.id)
    result = copilot_engine.generate_response(
        prompt=request.prompt,
        context=context,
        selected_project_id=request.project_id,
    )
    return result


@router.post("/audit-methodology", response_model=AuditMethodologyResponse)
def audit_strategy_methodology(
    request: AuditMethodologyRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Perform econometric methodology audit to detect lookahead bias, data leakage, and multiple testing pitfalls.
    """
    report = audit_research_methodology(
        strategy_description=request.strategy_description,
        slippage_pct=request.slippage_pct,
        commission_bps=request.commission_bps,
        num_trials_tested=request.num_trials_tested,
        reported_sharpe=request.reported_sharpe,
        uses_chronological_split=request.uses_chronological_split,
        execution_at_next_bar_open=request.execution_at_next_bar_open,
    )
    return report

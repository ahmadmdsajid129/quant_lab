from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user, get_current_workspace
from app.db.models import User, Workspace
from app.schemas.reports import TearsheetResponse
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Research Reports & Exports"])


@router.get("/experiments/{experiment_id}/tearsheet", response_model=TearsheetResponse)
def get_experiment_tearsheet(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Generate complete institutional research tearsheet from persisted experiment artifacts.
    """
    try:
        return report_service.build_experiment_tearsheet(db, experiment_id, workspace.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/experiments/{experiment_id}/export/markdown")
def export_tearsheet_markdown(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Export research tearsheet as a publication-ready Markdown report.
    """
    try:
        tearsheet = report_service.build_experiment_tearsheet(db, experiment_id, workspace.id)
        md_text = report_service.export_markdown_report(tearsheet)
        return Response(content=md_text, media_type="text/markdown")
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/experiments/{experiment_id}/export/json")
def export_tearsheet_json(
    experiment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
):
    """
    Export research tearsheet with complete cryptographic lineage and metadata as JSON.
    """
    try:
        return report_service.build_experiment_tearsheet(db, experiment_id, workspace.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

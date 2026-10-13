from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Project, Hypothesis, ResearchNote, Workspace, User, AuditLog
from app.schemas.projects import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailResponse,
    HypothesisCreate,
    HypothesisResponse,
    ResearchNoteCreate,
    ResearchNoteResponse,
)
from app.core.deps import get_current_user, get_current_workspace

router = APIRouter(prefix="/projects", tags=["projects"])


def verify_project_access(project_id: str, workspace_id: str, db: Session) -> Project:
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.workspace_id == workspace_id
    ).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found in current workspace",
        )
    return project


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """List all research projects scoped to current active workspace."""
    projects = db.query(Project).filter(Project.workspace_id == workspace.id).all()
    results = []
    for p in projects:
        hypo_cnt = len(p.hypotheses)
        exp_cnt = len(p.experiments)
        results.append(
            ProjectResponse(
                id=p.id,
                workspace_id=p.workspace_id,
                title=p.title,
                description=p.description,
                asset_class=p.asset_class,
                status=p.status,
                created_at=p.created_at,
                updated_at=p.updated_at,
                hypotheses_count=hypo_cnt,
                experiments_count=exp_cnt,
            )
        )
    return results


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    p_in: ProjectCreate,
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Create a new research project within active workspace."""
    new_p = Project(
        workspace_id=workspace.id,
        title=p_in.title,
        description=p_in.description,
        asset_class=p_in.asset_class,
        status="DRAFT",
    )
    db.add(new_p)
    db.flush()

    audit = AuditLog(
        user_id=user.id,
        action="PROJECT_CREATED",
        resource_type="PROJECT",
        resource_id=new_p.id,
        details={"title": new_p.title, "workspace_id": workspace.id},
    )
    db.add(audit)

    db.commit()
    db.refresh(new_p)

    return ProjectResponse(
        id=new_p.id,
        workspace_id=new_p.workspace_id,
        title=new_p.title,
        description=new_p.description,
        asset_class=new_p.asset_class,
        status=new_p.status,
        created_at=new_p.created_at,
        updated_at=new_p.updated_at,
        hypotheses_count=0,
        experiments_count=0,
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(
    project_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Get project details including hypotheses, notes, and metrics."""
    project = verify_project_access(project_id, workspace.id, db)
    hypotheses = [HypothesisResponse.model_validate(h) for h in project.hypotheses]
    notes = [ResearchNoteResponse.model_validate(n) for n in project.notes]

    return ProjectDetailResponse(
        id=project.id,
        workspace_id=project.workspace_id,
        title=project.title,
        description=project.description,
        asset_class=project.asset_class,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        hypotheses_count=len(hypotheses),
        experiments_count=len(project.experiments),
        hypotheses=hypotheses,
        notes=notes,
    )


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str,
    p_in: ProjectUpdate,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Update research project title, description, or research status."""
    project = verify_project_access(project_id, workspace.id, db)
    if p_in.title is not None:
        project.title = p_in.title
    if p_in.description is not None:
        project.description = p_in.description
    if p_in.status is not None:
        project.status = p_in.status

    db.commit()
    db.refresh(project)

    return ProjectResponse(
        id=project.id,
        workspace_id=project.workspace_id,
        title=project.title,
        description=project.description,
        asset_class=project.asset_class,
        status=project.status,
        created_at=project.created_at,
        updated_at=project.updated_at,
        hypotheses_count=len(project.hypotheses),
        experiments_count=len(project.experiments),
    )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Delete a research project and associated hypotheses."""
    project = verify_project_access(project_id, workspace.id, db)
    db.delete(project)
    db.commit()
    return None


@router.post("/{project_id}/hypotheses", response_model=HypothesisResponse, status_code=status.HTTP_201_CREATED)
def add_hypothesis(
    project_id: str,
    hypo_in: HypothesisCreate,
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Attach a formal scientific hypothesis to a research project."""
    project = verify_project_access(project_id, workspace.id, db)
    new_h = Hypothesis(
        project_id=project.id,
        statement=hypo_in.statement,
        mechanism=hypo_in.mechanism,
        predicted_outcome=hypo_in.predicted_outcome,
        falsification_criteria=hypo_in.falsification_criteria,
        status="UNTESTED",
    )
    db.add(new_h)
    db.commit()
    db.refresh(new_h)
    return HypothesisResponse.model_validate(new_h)


@router.post("/{project_id}/notes", response_model=ResearchNoteResponse, status_code=status.HTTP_201_CREATED)
def add_note(
    project_id: str,
    note_in: ResearchNoteCreate,
    user: User = Depends(get_current_user),
    workspace: Workspace = Depends(get_current_workspace),
    db: Session = Depends(get_db)
):
    """Add a rich Markdown research note to a project."""
    project = verify_project_access(project_id, workspace.id, db)
    new_n = ResearchNote(
        project_id=project.id,
        user_id=user.id,
        title=note_in.title,
        content=note_in.content,
    )
    db.add(new_n)
    db.commit()
    db.refresh(new_n)
    return ResearchNoteResponse.model_validate(new_n)

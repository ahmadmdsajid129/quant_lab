import uuid
import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Workspace, WorkspaceMember, User, AuditLog
from app.schemas.auth import WorkspaceResponse
from app.core.deps import get_current_user

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)


class MemberAdd(BaseModel):
    user_id: str
    role: str = Field("RESEARCHER", pattern="^(ADMIN|RESEARCHER|VIEWER)$")


class MemberResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str


@router.get("", response_model=List[WorkspaceResponse])
def list_workspaces(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """List all workspaces the authenticated user belongs to."""
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == current_user.id).all()
    results = []
    for m in memberships:
        ws = db.query(Workspace).filter(Workspace.id == m.workspace_id).first()
        if ws:
            results.append(WorkspaceResponse(id=ws.id, name=ws.name, slug=ws.slug, role=m.role))
    return results


@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
def create_workspace(
    ws_in: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workspace and designate creator as ADMIN."""
    slug = f"{slugify(ws_in.name)}-{str(uuid.uuid4())[:8]}"
    new_ws = Workspace(
        name=ws_in.name,
        slug=slug,
        owner_id=current_user.id,
    )
    db.add(new_ws)
    db.flush()

    member = WorkspaceMember(
        workspace_id=new_ws.id,
        user_id=current_user.id,
        role="ADMIN",
    )
    db.add(member)

    audit = AuditLog(
        user_id=current_user.id,
        action="WORKSPACE_CREATED",
        resource_type="WORKSPACE",
        resource_id=new_ws.id,
        details={"name": new_ws.name},
    )
    db.add(audit)

    db.commit()
    db.refresh(new_ws)

    return WorkspaceResponse(id=new_ws.id, name=new_ws.name, slug=new_ws.slug, role="ADMIN")


@router.get("/{workspace_id}/members", response_model=List[MemberResponse])
def get_members(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve members of specified workspace if user has access."""
    # Check user is a member
    user_membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not user_membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this workspace",
        )

    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.workspace_id == workspace_id).all()
    out = []
    for m in memberships:
        u = db.query(User).filter(User.id == m.user_id).first()
        if u:
            out.append(MemberResponse(user_id=u.id, email=u.email, full_name=u.full_name, role=m.role))
    return out


@router.post("/{workspace_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(
    workspace_id: str,
    member_in: MemberAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a user to workspace (Requires ADMIN role)."""
    user_membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not user_membership or user_membership.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only workspace ADMINs can add members",
        )

    target_user = db.query(User).filter(User.id == member_in.user_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    existing = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == member_in.user_id
    ).first()
    if existing:
        existing.role = member_in.role
    else:
        new_m = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=member_in.user_id,
            role=member_in.role
        )
        db.add(new_m)

    db.commit()
    return {"status": "success", "message": f"User {target_user.email} added as {member_in.role}"}

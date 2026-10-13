from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Workspace, WorkspaceMember
from app.core.security import decode_access_token

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Validate JWT token and return active user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or account deactivated",
        )
    return user


def get_current_workspace(
    x_workspace_id: Optional[str] = Header(None, alias="X-Workspace-Id"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Workspace:
    """Resolve active tenant workspace and verify user authorization."""
    if x_workspace_id:
        membership = db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == x_workspace_id,
            WorkspaceMember.user_id == current_user.id
        ).first()
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to requested workspace",
            )
        workspace = db.query(Workspace).filter(Workspace.id == x_workspace_id).first()
        if not workspace:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workspace not found")
        return workspace

    # Fall back to user's first available workspace
    membership = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).first()
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No workspace available for this user",
        )
    workspace = db.query(Workspace).filter(Workspace.id == membership.workspace_id).first()
    return workspace

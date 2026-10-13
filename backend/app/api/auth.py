import uuid
import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User, Workspace, WorkspaceMember, AuditLog
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse, WorkspaceResponse
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[-\s]+", "-", text)


def format_user_response(user: User, db: Session) -> UserResponse:
    memberships = db.query(WorkspaceMember).filter(WorkspaceMember.user_id == user.id).all()
    workspaces = []
    for m in memberships:
        ws = db.query(Workspace).filter(Workspace.id == m.workspace_id).first()
        if ws:
            workspaces.append(WorkspaceResponse(id=ws.id, name=ws.name, slug=ws.slug, role=m.role))
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        workspaces=workspaces,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    """Register a new user and provision personal research workspace."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists",
        )

    # Create User
    new_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(new_user)
    db.flush()

    # Create Default Personal Workspace
    base_slug = f"{slugify(user_in.full_name)}-workspace-{str(uuid.uuid4())[:8]}"
    workspace = Workspace(
        name=f"{user_in.full_name}'s Workspace",
        slug=base_slug,
        owner_id=new_user.id,
    )
    db.add(workspace)
    db.flush()

    # Add User as Admin of Workspace
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=new_user.id,
        role="ADMIN",
    )
    db.add(member)

    # Audit Log
    audit = AuditLog(
        user_id=new_user.id,
        action="USER_REGISTERED",
        resource_type="USER",
        resource_id=new_user.id,
        details={"email": new_user.email},
    )
    db.add(audit)

    db.commit()
    db.refresh(new_user)

    # Generate token
    token = create_access_token(subject=new_user.id)
    user_resp = format_user_response(new_user, db)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_resp,
    )


@router.post("/login", response_model=TokenResponse)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email and password to receive JWT token."""
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is deactivated",
        )

    token = create_access_token(subject=user.id)
    user_resp = format_user_response(user, db)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=user_resp,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Retrieve profile and workspaces for authenticated user."""
    return format_user_response(current_user, db)

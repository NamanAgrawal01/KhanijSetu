from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.auth.jwt_handler import verify_password, create_access_token, get_current_user
from app.auth.rbac import get_user_accessible_modules
from app.schemas.auth import LoginRequest, DemoLoginRequest, TokenResponse, UserResponse
from app.models.audit import AuditLog
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])

DEMO_ACCOUNTS = {
    "admin": "admin@khanijsetu.gov.in",
    "mine_operator": "operator@khanijsetu.gov.in",
    "inspector": "inspector@khanijsetu.gov.in",
    "analyst": "analyst@khanijsetu.gov.in",
    "viewer": "viewer@khanijsetu.gov.in",
}


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    # Audit log
    db.add(AuditLog(
        user_id=user.id, user_name=user.name, user_role=user.role,
        action="login", module="auth", entity="user", entity_id=user.id,
        details=f"User logged in: {user.email}", status="success"
    ))
    db.commit()

    modules = get_user_accessible_modules(user.role)
    user_response = UserResponse(
        id=user.id, email=user.email, name=user.name, role=user.role,
        designation=user.designation or "", phone=user.phone or "",
        subsidiary_id=user.subsidiary_id, mine_id=user.mine_id,
        is_active=user.is_active, avatar_url=user.avatar_url or "",
        accessible_modules=modules
    )

    return TokenResponse(access_token=token, user=user_response)


@router.post("/demo-login", response_model=TokenResponse)
async def demo_login(request: DemoLoginRequest, db: Session = Depends(get_db)):
    """One-click demo login by role."""
    email = DEMO_ACCOUNTS.get(request.role)
    if not email:
        raise HTTPException(status_code=400, detail=f"Invalid demo role: {request.role}")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Demo account not found. Run seed_data.py first.")

    token = create_access_token(data={"sub": str(user.id), "role": user.role})

    db.add(AuditLog(
        user_id=user.id, user_name=user.name, user_role=user.role,
        action="demo_login", module="auth", entity="user", entity_id=user.id,
        details=f"Demo login as {user.role}", status="success"
    ))
    db.commit()

    modules = get_user_accessible_modules(user.role)
    user_response = UserResponse(
        id=user.id, email=user.email, name=user.name, role=user.role,
        designation=user.designation or "", phone=user.phone or "",
        subsidiary_id=user.subsidiary_id, mine_id=user.mine_id,
        is_active=user.is_active, avatar_url=user.avatar_url or "",
        accessible_modules=modules
    )

    return TokenResponse(access_token=token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    modules = get_user_accessible_modules(current_user.role)
    return UserResponse(
        id=current_user.id, email=current_user.email, name=current_user.name,
        role=current_user.role, designation=current_user.designation or "",
        phone=current_user.phone or "",
        subsidiary_id=current_user.subsidiary_id, mine_id=current_user.mine_id,
        is_active=current_user.is_active, avatar_url=current_user.avatar_url or "",
        accessible_modules=modules
    )

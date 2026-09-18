"""
KhanijSetu Users Management API — CRUD operations for user accounts.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User, Subsidiary
from app.models.audit import AuditLog
from app.auth.jwt_handler import get_current_user, get_password_hash
from app.auth.rbac import require_role
from datetime import datetime, timezone

router = APIRouter(prefix="/users", tags=["Users"])


class UserCreateRequest(BaseModel):
    email: str
    name: str
    password: str
    role: str
    designation: str = ""
    phone: str = ""
    subsidiary_id: Optional[int] = None
    mine_id: Optional[int] = None


class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    designation: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    subsidiary_id: Optional[int] = None
    mine_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    designation: str
    phone: str
    subsidiary_id: Optional[int] = None
    mine_id: Optional[int] = None
    is_active: bool
    subsidiary_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


@router.get("")
async def list_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all users. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    users = query.order_by(User.id).all()
    result = []
    for u in users:
        sub = db.query(Subsidiary).filter(Subsidiary.id == u.subsidiary_id).first() if u.subsidiary_id else None
        result.append({
            "id": u.id, "email": u.email, "name": u.name,
            "role": u.role, "designation": u.designation,
            "phone": u.phone, "subsidiary_id": u.subsidiary_id,
            "mine_id": u.mine_id, "is_active": u.is_active,
            "subsidiary_name": sub.name if sub else None,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        })
    return {"users": result, "total": len(result)}


@router.post("")
async def create_user(
    data: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new user. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        name=data.name,
        password_hash=get_password_hash(data.password),
        role=data.role,
        designation=data.designation,
        phone=data.phone,
        subsidiary_id=data.subsidiary_id,
        mine_id=data.mine_id,
    )
    db.add(user)

    # Audit log
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name,
        user_role=current_user.role, action="created", module="users",
        entity="user", details=f"Created user: {data.name} ({data.email}) with role {data.role}",
        status="success",
    ))
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role, "message": "User created successfully"}


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    data: UserUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a user. Admin or self only."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    # Non-admins cannot change role
    if current_user.role != "admin" and "role" in update_data:
        del update_data["role"]

    for key, value in update_data.items():
        setattr(user, key, value)

    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name,
        user_role=current_user.role, action="updated", module="users",
        entity="user", entity_id=user_id,
        details=f"Updated user: {user.name} — fields: {', '.join(update_data.keys())}",
        status="success",
    ))
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role, "message": "User updated"}


@router.patch("/{user_id}/disable")
async def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Disable a user. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot disable your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = not user.is_active
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name,
        user_role=current_user.role, action="updated", module="users",
        entity="user", entity_id=user_id,
        details=f"{'Disabled' if not user.is_active else 'Enabled'} user: {user.name}",
        status="success",
    ))
    db.commit()
    return {"id": user.id, "is_active": user.is_active, "message": f"User {'enabled' if user.is_active else 'disabled'}"}


@router.get("/subsidiaries")
async def list_subsidiaries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all subsidiaries."""
    subs = db.query(Subsidiary).all()
    return [{"id": s.id, "name": s.name, "code": s.code, "region": s.region} for s in subs]


class SubsidiaryCreate(BaseModel):
    name: str
    code: str
    region: Optional[str] = None
    address: Optional[str] = None


@router.post("/subsidiaries")
async def create_subsidiary(data: SubsidiaryCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin required")
    s = Subsidiary(name=data.name, code=data.code, region=data.region, address=data.address)
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "name": s.name, "code": s.code}

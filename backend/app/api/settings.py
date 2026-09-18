"""Profile, alert rules, and system configuration."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.auth.jwt_handler import get_current_user, get_password_hash, verify_password
from app.database import get_db
from app.models.alert import Alert
from app.models.audit import AuditLog
from app.models.user import User

router = APIRouter(prefix="/settings", tags=["Settings"])

# In-memory demo config (persisted via audit; prototype)
SYSTEM_CONFIG = {
    "risk_low_max": 25,
    "risk_medium_max": 50,
    "risk_high_max": 75,
    "due_soon_days": 7,
    "escalation_overdue_days": 3,
    "disclaimer": "KhanijSetu is a decision-support prototype. Regulatory and safety decisions must be verified by authorized personnel and applicable official sources.",
}


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


class ConfigUpdate(BaseModel):
    risk_low_max: Optional[int] = None
    risk_medium_max: Optional[int] = None
    risk_high_max: Optional[int] = None
    due_soon_days: Optional[int] = None
    escalation_overdue_days: Optional[int] = None


@router.get("")
async def get_settings(current_user: User = Depends(get_current_user)):
    data = {
        "profile": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "role": current_user.role,
            "designation": current_user.designation,
            "phone": current_user.phone,
        },
        "disclaimer": SYSTEM_CONFIG["disclaimer"],
    }
    if current_user.role == "admin":
        data["system"] = SYSTEM_CONFIG
    return data


@router.put("/profile")
async def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(current_user, k, v)
    db.add(current_user)
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name, user_role=current_user.role,
        action="updated", module="settings", entity="user", entity_id=current_user.id,
        details="Updated profile", status="success",
    ))
    db.commit()
    return {"status": "success"}


@router.put("/password")
async def change_password(data: PasswordUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    current_user.password_hash = get_password_hash(data.new_password)
    db.add(current_user)
    db.commit()
    return {"status": "success"}


@router.put("/system")
async def update_system(data: ConfigUpdate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    for k, v in data.model_dump(exclude_unset=True).items():
        SYSTEM_CONFIG[k] = v
    return {"status": "success", "system": SYSTEM_CONFIG}


@router.post("/alerts")
async def create_alert_rule_instance(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role not in ("admin", "viewer", "inspector", "mine_operator"):
        raise HTTPException(status_code=403, detail="Not permitted")
    alert = Alert(
        mine_id=payload.get("mine_id"),
        mine_name=payload.get("mine_name"),
        type=payload.get("type") or "system",
        severity=payload.get("severity") or "warning",
        title=payload.get("title") or "Alert",
        message=payload.get("message"),
        source=current_user.role,
        link=payload.get("link"),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"id": alert.id}


@router.post("/alerts/{alert_id}/escalate")
async def escalate_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.escalation_level = (alert.escalation_level or 0) + 1
    history = alert.escalation_history or ""
    alert.escalation_history = history + f"\nL{alert.escalation_level} by {current_user.name}"
    db.commit()
    return {"id": alert.id, "escalation_level": alert.escalation_level}

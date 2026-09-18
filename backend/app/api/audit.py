from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.auth.jwt_handler import get_current_user
from app.schemas.common import AuditLogResponse, AuditLogListResponse
from typing import Optional

router = APIRouter(prefix="/audit", tags=["Audit Trail"])


@router.get("", response_model=AuditLogListResponse)
async def get_audit_logs(
    module: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(AuditLog)
    if module:
        query = query.filter(AuditLog.module == module)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

    result = [AuditLogResponse(
        id=log.id, user_name=log.user_name, user_role=log.user_role,
        action=log.action, module=log.module,
        entity=log.entity, entity_id=log.entity_id,
        details=log.details, status=log.status,
        created_at=log.created_at,
    ) for log in logs]

    return AuditLogListResponse(logs=result, total=total)

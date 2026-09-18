from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.auth.jwt_handler import get_current_user
from app.schemas.common import AlertResponse, AlertListResponse
from typing import Optional

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=AlertListResponse)
async def get_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)

    total = query.count()
    alerts = query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()

    critical = db.query(Alert).filter(Alert.severity == "critical", Alert.status == "active").count()
    high = db.query(Alert).filter(Alert.severity == "high", Alert.status == "active").count()
    warning = db.query(Alert).filter(Alert.severity == "warning", Alert.status == "active").count()
    info = db.query(Alert).filter(Alert.severity == "info", Alert.status == "active").count()

    result = [AlertResponse(
        id=a.id, mine_id=a.mine_id, mine_name=a.mine_name,
        type=a.type, severity=a.severity, title=a.title,
        message=a.message, status=a.status,
        escalation_level=a.escalation_level,
        source=a.source, link=a.link, created_at=a.created_at,
    ) for a in alerts]

    return AlertListResponse(
        alerts=result, total=total,
        critical=critical, high=high, warning=warning, info=info,
    )


@router.put("/{alert_id}")
async def update_alert(alert_id: int, status: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = status
    db.commit()
    return {"status": "success"}

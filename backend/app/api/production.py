from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.production import ProductionRecord
from app.auth.jwt_handler import get_current_user
from app.schemas.common import ProductionListResponse, ProductionRecordResponse
from app.ai import ai_service
from typing import Optional
from pydantic import BaseModel
from datetime import date
from app.services.scoring import production_anomaly
from app.models.audit import AuditLog

router = APIRouter(prefix="/production", tags=["Production"])


class ProductionCreate(BaseModel):
    mine_id: int
    date: date
    target_tonnes: float
    actual_tonnes: float
    shift: str = "day"
    downtime_hours: float = 0
    downtime_reason: Optional[str] = None
    notes: Optional[str] = None
    safety_incidents: int = 0

router = APIRouter(prefix="/production", tags=["Production"])


@router.get("")
async def get_production(
    mine_id: Optional[int] = None,
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(ProductionRecord)
    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(ProductionRecord.mine_id == current_user.mine_id)
    if mine_id:
        query = query.filter(ProductionRecord.mine_id == mine_id)

    total = query.count()
    records = query.order_by(ProductionRecord.date.desc()).offset(skip).limit(limit).all()

    total_target = sum(r.target_tonnes for r in records)
    total_actual = sum(r.actual_tonnes for r in records)
    total_downtime = sum(r.downtime_hours for r in records)
    count = len(records) or 1

    result = []
    for r in records:
        mine = db.query(Mine).filter(Mine.id == r.mine_id).first()
        result.append(ProductionRecordResponse(
            id=r.id, mine_id=r.mine_id,
            mine_name=mine.name if mine else "",
            date=r.date, shift=r.shift,
            target_tonnes=r.target_tonnes, actual_tonnes=r.actual_tonnes,
            overburden_removed=r.overburden_removed,
            equipment_hours=r.equipment_hours,
            downtime_hours=r.downtime_hours,
            downtime_reason=r.downtime_reason,
            safety_incidents=r.safety_incidents,
        ))

    # Check for anomalies
    anomaly_data = await ai_service.detect_anomalies({
        "target": total_target / count,
        "actual": total_actual / count,
    })
    mine_anomalies = []
    mine_ids = {r.mine_id for r in records}
    for mid in mine_ids:
        a = production_anomaly(db, mid)
        if a:
            mine_anomalies.append(a)

    return {
        "records": [r.model_dump() for r in result],
        "total": total,
        "daily_avg_target": round(total_target / count, 1),
        "daily_avg_actual": round(total_actual / count, 1),
        "total_downtime": round(total_downtime, 1),
        "anomalies": anomaly_data,
        "operational_anomalies": mine_anomalies,
    }


@router.post("")
async def create_production(data: ProductionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rec = ProductionRecord(
        mine_id=data.mine_id,
        date=data.date,
        shift=data.shift,
        target_tonnes=data.target_tonnes,
        actual_tonnes=data.actual_tonnes,
        downtime_hours=data.downtime_hours,
        downtime_reason=data.downtime_reason,
        safety_incidents=data.safety_incidents,
        notes=data.notes,
        recorded_by=current_user.name,
    )
    db.add(rec)
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name, user_role=current_user.role,
        action="created", module="production", entity="production",
        details=f"Production record {data.date} mine {data.mine_id}", status="success",
    ))
    db.commit()
    db.refresh(rec)
    mine = db.query(Mine).filter(Mine.id == rec.mine_id).first()
    return ProductionRecordResponse(
        id=rec.id, mine_id=rec.mine_id, mine_name=mine.name if mine else "",
        date=rec.date, shift=rec.shift, target_tonnes=rec.target_tonnes,
        actual_tonnes=rec.actual_tonnes, downtime_hours=rec.downtime_hours,
        downtime_reason=rec.downtime_reason, safety_incidents=rec.safety_incidents,
    )

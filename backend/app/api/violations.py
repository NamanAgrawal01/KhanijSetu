from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.violation import Violation
from app.auth.jwt_handler import get_current_user
from app.schemas.violation import ViolationCreate, ViolationUpdate, ViolationResponse, ViolationListResponse
from typing import Optional
from datetime import date
from app.services.scoring import recalculate_mine

router = APIRouter(prefix="/violations", tags=["Violations"])


@router.get("", response_model=ViolationListResponse)
async def get_violations(
    mine_id: Optional[int] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Violation)
    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(Violation.mine_id == current_user.mine_id)
    if mine_id:
        query = query.filter(Violation.mine_id == mine_id)
    if category:
        query = query.filter(Violation.category == category)
    if severity:
        query = query.filter(Violation.severity == severity)
    if status:
        query = query.filter(Violation.status == status)

    total = query.count()
    violations = query.order_by(Violation.detected_date.desc()).offset(skip).limit(limit).all()

    result = []
    for v in violations:
        mine = db.query(Mine).filter(Mine.id == v.mine_id).first()
        result.append(ViolationResponse(
            id=v.id, violation_code=v.violation_code, mine_id=v.mine_id,
            mine_name=mine.name if mine else "",
            category=v.category, severity=v.severity, title=v.title,
            description=v.description, reported_by_name=v.reported_by_name,
            assigned_to_name=v.assigned_to_name, detected_date=v.detected_date,
            deadline=v.deadline, status=v.status, resolution_notes=v.resolution_notes,
            evidence_url=v.evidence_url, is_recurring=v.is_recurring,
            recurrence_count=v.recurrence_count,
            created_at=v.created_at, updated_at=v.updated_at,
        ))
    return ViolationListResponse(violations=result, total=total)


@router.get("/{violation_id}", response_model=ViolationResponse)
async def get_violation(violation_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    v = db.query(Violation).filter(Violation.id == violation_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Violation not found")
    mine = db.query(Mine).filter(Mine.id == v.mine_id).first()
    return ViolationResponse(
        id=v.id, violation_code=v.violation_code, mine_id=v.mine_id,
        mine_name=mine.name if mine else "",
        category=v.category, severity=v.severity, title=v.title,
        description=v.description, reported_by_name=v.reported_by_name,
        assigned_to_name=v.assigned_to_name, detected_date=v.detected_date,
        deadline=v.deadline, status=v.status, resolution_notes=v.resolution_notes,
        evidence_url=v.evidence_url, is_recurring=v.is_recurring,
        recurrence_count=v.recurrence_count,
        created_at=v.created_at, updated_at=v.updated_at,
    )


@router.post("", response_model=ViolationResponse)
async def create_violation(data: ViolationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a violation. Admin or Inspector only."""
    if current_user.role not in ["admin", "inspector"]:
        raise HTTPException(status_code=403, detail="Only admin or inspector can create violations")
    count = db.query(Violation).count()
    v = Violation(
        violation_code=f"VIO-2026-{count + 1:04d}",
        mine_id=data.mine_id, category=data.category, severity=data.severity,
        title=data.title, description=data.description,
        reported_by=current_user.id, reported_by_name=data.reported_by_name or current_user.name,
        assigned_to_name=data.assigned_to_name, detected_date=data.detected_date,
        deadline=data.deadline, inspection_id=data.inspection_id,
    )

    # Check for recurring violations
    existing = db.query(Violation).filter(
        Violation.mine_id == data.mine_id,
        Violation.category == data.category,
        Violation.title.ilike(f"%{data.title.split()[0] if data.title else ''}%")
    ).count()
    if existing > 0:
        v.is_recurring = 1
        v.recurrence_count = existing

    db.add(v)
    db.commit()
    recalculate_mine(db, data.mine_id)
    db.commit()
    db.refresh(v)
    mine = db.query(Mine).filter(Mine.id == v.mine_id).first()
    return ViolationResponse(
        id=v.id, violation_code=v.violation_code, mine_id=v.mine_id,
        mine_name=mine.name if mine else "",
        category=v.category, severity=v.severity, title=v.title,
        description=v.description, reported_by_name=v.reported_by_name,
        assigned_to_name=v.assigned_to_name, detected_date=v.detected_date,
        deadline=v.deadline, status=v.status,
        is_recurring=v.is_recurring, recurrence_count=v.recurrence_count,
        created_at=v.created_at, updated_at=v.updated_at,
    )


@router.put("/{violation_id}", response_model=ViolationResponse)
async def update_violation(violation_id: int, data: ViolationUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update a violation. Admin or Inspector only."""
    if current_user.role not in ["admin", "inspector"]:
        raise HTTPException(status_code=403, detail="Only admin or inspector can update violations")
    v = db.query(Violation).filter(Violation.id == violation_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Violation not found")

    old_status = v.status
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(v, key, value)

    db.commit()
    recalculate_mine(db, v.mine_id)
    db.commit()
    db.refresh(v)
    mine = db.query(Mine).filter(Mine.id == v.mine_id).first()
    return ViolationResponse(
        id=v.id, violation_code=v.violation_code, mine_id=v.mine_id,
        mine_name=mine.name if mine else "",
        category=v.category, severity=v.severity, title=v.title,
        description=v.description, reported_by_name=v.reported_by_name,
        assigned_to_name=v.assigned_to_name, detected_date=v.detected_date,
        deadline=v.deadline, status=v.status, resolution_notes=v.resolution_notes,
        evidence_url=v.evidence_url, is_recurring=v.is_recurring,
        recurrence_count=v.recurrence_count,
        created_at=v.created_at, updated_at=v.updated_at,
    )


@router.get("/recurring/list")
async def get_recurring_violations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get recurring violations across mines."""
    recurring = db.query(Violation).filter(Violation.is_recurring == 1).order_by(Violation.recurrence_count.desc()).all()
    result = []
    for v in recurring:
        mine = db.query(Mine).filter(Mine.id == v.mine_id).first()
        result.append({
            "id": v.id, "violation_code": v.violation_code,
            "category": v.category, "title": v.title,
            "mine_name": mine.name if mine else "",
            "recurrence_count": v.recurrence_count,
            "severity": v.severity, "status": v.status,
            "detected_date": v.detected_date.isoformat() if v.detected_date else "",
            "ai_insight": f"Repeated {v.category} violations indicate a persistent compliance weakness at {mine.name if mine else 'this mine'}. Recommend targeted training, enhanced monitoring, and root-cause analysis."
        })

    if not result:
        return []
    return result

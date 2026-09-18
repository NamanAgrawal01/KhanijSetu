from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.inspection import Inspection, InspectionItem
from app.auth.jwt_handler import get_current_user
from app.schemas.inspection import (
    InspectionCreate, InspectionUpdate, InspectionItemCreate,
    InspectionResponse, InspectionItemResponse, InspectionListResponse
)
from typing import Optional
from datetime import date, timedelta
from app.models.violation import Violation
from app.models.corrective_action import CorrectiveAction
from app.models.audit import AuditLog
from app.services.scoring import recalculate_mine

router = APIRouter(prefix="/inspections", tags=["Inspections"])


@router.get("", response_model=InspectionListResponse)
async def get_inspections(
    mine_id: Optional[int] = None,
    status: Optional[str] = None,
    inspector_id: Optional[int] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Inspection)
    if current_user.role == "inspector":
        query = query.filter(Inspection.inspector_id == current_user.id)
    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(Inspection.mine_id == current_user.mine_id)
    if mine_id:
        query = query.filter(Inspection.mine_id == mine_id)
    if status:
        query = query.filter(Inspection.status == status)
    if inspector_id:
        query = query.filter(Inspection.inspector_id == inspector_id)

    total = query.count()
    inspections = query.order_by(Inspection.scheduled_date.desc()).offset(skip).limit(limit).all()

    scheduled = db.query(Inspection).filter(Inspection.status == "scheduled").count()
    in_progress = db.query(Inspection).filter(Inspection.status == "in_progress").count()
    completed = db.query(Inspection).filter(Inspection.status == "completed").count()
    overdue = db.query(Inspection).filter(Inspection.status == "overdue").count()

    result = []
    for insp in inspections:
        mine = db.query(Mine).filter(Mine.id == insp.mine_id).first()
        inspector = db.query(User).filter(User.id == insp.inspector_id).first()
        items = db.query(InspectionItem).filter(InspectionItem.inspection_id == insp.id).all()
        item_responses = [InspectionItemResponse.model_validate(item) for item in items]

        result.append(InspectionResponse(
            id=insp.id, mine_id=insp.mine_id,
            mine_name=mine.name if mine else "",
            inspector_id=insp.inspector_id,
            inspector_name=inspector.name if inspector else "",
            inspection_type=insp.inspection_type,
            scheduled_date=insp.scheduled_date,
            completed_date=insp.completed_date,
            status=insp.status, priority=insp.priority,
            overall_rating=insp.overall_rating,
            findings_summary=insp.findings_summary,
            recommendations=insp.recommendations,
            gps_latitude=insp.gps_latitude,
            gps_longitude=insp.gps_longitude,
            items=item_responses,
            created_at=insp.created_at,
        ))

    return InspectionListResponse(
        inspections=result, total=total,
        scheduled=scheduled, in_progress=in_progress,
        completed=completed, overdue=overdue,
    )


@router.get("/{inspection_id}", response_model=InspectionResponse)
async def get_inspection(inspection_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    mine = db.query(Mine).filter(Mine.id == insp.mine_id).first()
    inspector = db.query(User).filter(User.id == insp.inspector_id).first()
    items = db.query(InspectionItem).filter(InspectionItem.inspection_id == insp.id).all()

    return InspectionResponse(
        id=insp.id, mine_id=insp.mine_id,
        mine_name=mine.name if mine else "",
        inspector_id=insp.inspector_id,
        inspector_name=inspector.name if inspector else "",
        inspection_type=insp.inspection_type,
        scheduled_date=insp.scheduled_date,
        completed_date=insp.completed_date,
        status=insp.status, priority=insp.priority,
        overall_rating=insp.overall_rating,
        findings_summary=insp.findings_summary,
        recommendations=insp.recommendations,
        gps_latitude=insp.gps_latitude, gps_longitude=insp.gps_longitude,
        items=[InspectionItemResponse.model_validate(i) for i in items],
        created_at=insp.created_at,
    )


@router.post("", response_model=InspectionResponse)
async def create_inspection(data: InspectionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    insp = Inspection(
        mine_id=data.mine_id,
        inspector_id=data.inspector_id or current_user.id,
        inspection_type=data.inspection_type,
        scheduled_date=data.scheduled_date,
        priority=data.priority,
    )
    db.add(insp)
    db.commit()
    db.refresh(insp)

    # Add default checklist items
    default_items = [
        ("PPE", "Personal Protective Equipment compliance"),
        ("PPE", "Safety helmets condition"),
        ("Emergency", "Emergency exit accessibility"),
        ("Emergency", "Fire extinguisher status"),
        ("Emergency", "Emergency evacuation plan display"),
        ("Equipment", "Equipment maintenance logs"),
        ("Equipment", "Heavy machinery safety certification"),
        ("Safety", "Worker safety briefing records"),
        ("Safety", "First aid kit availability"),
        ("Environment", "Dust suppression systems"),
        ("Environment", "Ventilation systems"),
        ("Documentation", "Safety register updated"),
        ("Documentation", "Compliance certificates current"),
    ]
    for cat, name in default_items:
        item = InspectionItem(inspection_id=insp.id, category=cat, item_name=name)
        db.add(item)
    db.commit()

    mine = db.query(Mine).filter(Mine.id == insp.mine_id).first()
    inspector = db.query(User).filter(User.id == insp.inspector_id).first()
    items = db.query(InspectionItem).filter(InspectionItem.inspection_id == insp.id).all()

    return InspectionResponse(
        id=insp.id, mine_id=insp.mine_id,
        mine_name=mine.name if mine else "",
        inspector_id=insp.inspector_id,
        inspector_name=inspector.name if inspector else "",
        inspection_type=insp.inspection_type,
        scheduled_date=insp.scheduled_date,
        status=insp.status, priority=insp.priority,
        items=[InspectionItemResponse.model_validate(i) for i in items],
        created_at=insp.created_at,
    )


@router.put("/{inspection_id}", response_model=InspectionResponse)
async def update_inspection(inspection_id: int, data: InspectionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(insp, key, value)

    if data.status == "completed":
        insp.completed_date = insp.completed_date or date.today()
        mine = db.query(Mine).filter(Mine.id == insp.mine_id).first()
        if mine:
            mine.last_inspection_date = insp.completed_date

    db.commit()
    db.refresh(insp)

    mine = db.query(Mine).filter(Mine.id == insp.mine_id).first()
    inspector = db.query(User).filter(User.id == insp.inspector_id).first()
    items = db.query(InspectionItem).filter(InspectionItem.inspection_id == insp.id).all()

    return InspectionResponse(
        id=insp.id, mine_id=insp.mine_id,
        mine_name=mine.name if mine else "",
        inspector_id=insp.inspector_id,
        inspector_name=inspector.name if inspector else "",
        inspection_type=insp.inspection_type,
        scheduled_date=insp.scheduled_date,
        completed_date=insp.completed_date,
        status=insp.status, priority=insp.priority,
        overall_rating=insp.overall_rating,
        findings_summary=insp.findings_summary,
        recommendations=insp.recommendations,
        gps_latitude=insp.gps_latitude, gps_longitude=insp.gps_longitude,
        items=[InspectionItemResponse.model_validate(i) for i in items],
        created_at=insp.created_at,
    )


@router.put("/{inspection_id}/items/{item_id}")
async def update_inspection_item(
    inspection_id: int, item_id: int,
    data: InspectionItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    item = db.query(InspectionItem).filter(
        InspectionItem.id == item_id, InspectionItem.inspection_id == inspection_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inspection item not found")

    item.status = data.status
    item.severity = data.severity
    item.notes = data.notes
    item.photo_url = data.photo_url
    db.commit()
    db.refresh(item)
    return InspectionItemResponse.model_validate(item)


@router.post("/{inspection_id}/start")
async def start_inspection(
    inspection_id: int,
    gps_latitude: Optional[float] = None,
    gps_longitude: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")
    insp.status = "in_progress"
    if gps_latitude is not None:
        insp.gps_latitude = gps_latitude
    if gps_longitude is not None:
        insp.gps_longitude = gps_longitude
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name, user_role=current_user.role,
        action="updated", module="inspections", entity="inspection", entity_id=insp.id,
        details=f"Started inspection #{insp.id}", status="success",
    ))
    db.commit()
    return {"status": "success", "id": insp.id, "inspection_status": insp.status}


@router.post("/{inspection_id}/submit")
async def submit_inspection(
    inspection_id: int,
    findings_summary: Optional[str] = None,
    recommendations: Optional[str] = None,
    gps_latitude: Optional[float] = None,
    gps_longitude: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete inspection: create violations/CAs for failed items, audit, recalc risk."""
    insp = db.query(Inspection).filter(Inspection.id == inspection_id).first()
    if not insp:
        raise HTTPException(status_code=404, detail="Inspection not found")

    items = db.query(InspectionItem).filter(InspectionItem.inspection_id == insp.id).all()
    failed = [i for i in items if i.status == "fail"]
    created_violations = []
    for item in failed:
        count = db.query(Violation).count()
        v = Violation(
            violation_code=f"VIO-2026-{count + 1:04d}",
            mine_id=insp.mine_id,
            category=(item.category or "safety").lower() if (item.category or "").lower() in
            ("safety", "environment", "equipment", "labour", "documentation") else "safety",
            severity=item.severity or "medium",
            title=f"Inspection finding: {item.item_name}",
            description=item.notes or f"Failed checklist item during inspection #{insp.id}",
            reported_by=current_user.id,
            reported_by_name=current_user.name,
            detected_date=date.today(),
            inspection_id=insp.id,
            status="detected",
        )
        db.add(v)
        db.flush()
        ca = CorrectiveAction(
            action_code=f"CA-2026-{db.query(CorrectiveAction).count() + 1:04d}",
            violation_id=v.id,
            mine_id=insp.mine_id,
            title=f"Correct: {item.item_name}",
            description=item.notes or "Address failed inspection item and submit evidence.",
            assigned_to_name=None,
            deadline=date.today() + timedelta(days=14),
            priority=item.severity or "medium",
            status="pending",
        )
        db.add(ca)
        created_violations.append(v.violation_code)

    insp.status = "completed"
    insp.completed_date = date.today()
    if findings_summary:
        insp.findings_summary = findings_summary
    else:
        insp.findings_summary = (
            f"Inspection completed with {len(failed)} failed item(s) of {len(items)} checklist items."
        )
    if recommendations:
        insp.recommendations = recommendations
    if gps_latitude is not None:
        insp.gps_latitude = gps_latitude
    if gps_longitude is not None:
        insp.gps_longitude = gps_longitude
    fails = len(failed)
    insp.overall_rating = "critical" if fails >= 4 else ("unsatisfactory" if fails >= 2 else ("needs_improvement" if fails else "satisfactory"))

    mine = db.query(Mine).filter(Mine.id == insp.mine_id).first()
    if mine:
        mine.last_inspection_date = insp.completed_date

    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name, user_role=current_user.role,
        action="submitted", module="inspections", entity="inspection", entity_id=insp.id,
        details=f"Submitted inspection #{insp.id}; created violations {', '.join(created_violations) or 'none'}",
        status="success",
    ))
    db.commit()
    recalculate_mine(db, insp.mine_id)
    db.commit()
    return {
        "status": "success",
        "inspection_id": insp.id,
        "failed_items": len(failed),
        "violations_created": created_violations,
        "rating": insp.overall_rating,
    }

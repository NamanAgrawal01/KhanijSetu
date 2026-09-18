from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.compliance import ComplianceRequirement, ComplianceRecord
from app.auth.jwt_handler import get_current_user
from app.schemas.compliance import (
    ComplianceRecordCreate, ComplianceRecordUpdate, ComplianceRecordResponse,
    ComplianceListResponse, ComplianceRequirementResponse
)
from typing import Optional
from datetime import date
from pydantic import BaseModel

router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.get("", response_model=ComplianceListResponse)
async def get_compliance_records(
    mine_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get compliance records with filtering."""
    query = db.query(ComplianceRecord)

    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(ComplianceRecord.mine_id == current_user.mine_id)
    if mine_id:
        query = query.filter(ComplianceRecord.mine_id == mine_id)
    if status:
        query = query.filter(ComplianceRecord.status == status)
    if category:
        query = query.join(ComplianceRequirement).filter(ComplianceRequirement.category == category)

    total = query.count()
    records = query.order_by(ComplianceRecord.due_date.asc()).offset(skip).limit(limit).all()

    result = []
    for rec in records:
        req = db.query(ComplianceRequirement).filter(ComplianceRequirement.id == rec.requirement_id).first()
        mine = db.query(Mine).filter(Mine.id == rec.mine_id).first()
        result.append(ComplianceRecordResponse(
            id=rec.id, requirement_id=rec.requirement_id, mine_id=rec.mine_id,
            status=rec.status, due_date=rec.due_date, completed_date=rec.completed_date,
            evidence_url=rec.evidence_url, notes=rec.notes,
            responsible_officer=rec.responsible_officer, risk_level=rec.risk_level,
            requirement_title=req.title if req else "",
            requirement_category=req.category if req else "",
            mine_name=mine.name if mine else "",
            created_at=rec.created_at, updated_at=rec.updated_at,
        ))

    requirements = db.query(ComplianceRequirement).filter(ComplianceRequirement.is_active == 1).all()
    req_list = [ComplianceRequirementResponse.model_validate(r) for r in requirements]

    return ComplianceListResponse(records=result, total=total, requirements=req_list)


@router.post("", response_model=ComplianceRecordResponse)
async def create_compliance_record(
    data: ComplianceRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a compliance record."""
    record = ComplianceRecord(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    req = db.query(ComplianceRequirement).filter(ComplianceRequirement.id == record.requirement_id).first()
    mine = db.query(Mine).filter(Mine.id == record.mine_id).first()
    return ComplianceRecordResponse(
        id=record.id, requirement_id=record.requirement_id, mine_id=record.mine_id,
        status=record.status, due_date=record.due_date,
        responsible_officer=record.responsible_officer, notes=record.notes,
        risk_level=record.risk_level,
        requirement_title=req.title if req else "",
        requirement_category=req.category if req else "",
        mine_name=mine.name if mine else "",
        created_at=record.created_at, updated_at=record.updated_at,
    )


@router.put("/{record_id}", response_model=ComplianceRecordResponse)
async def update_compliance_record(
    record_id: int,
    data: ComplianceRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a compliance record (status, evidence, etc)."""
    record = db.query(ComplianceRecord).filter(ComplianceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Compliance record not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(record, key, value)

    # If marking complete, update mine compliance score
    if data.status == "completed":
        record.completed_date = record.completed_date or date.today()
        mine = db.query(Mine).filter(Mine.id == record.mine_id).first()
        if mine:
            total_records = db.query(ComplianceRecord).filter(ComplianceRecord.mine_id == mine.id).count()
            completed = db.query(ComplianceRecord).filter(
                ComplianceRecord.mine_id == mine.id, ComplianceRecord.status == "completed"
            ).count()
            if total_records > 0:
                mine.compliance_score = round((completed / total_records) * 100, 1)
                # Recalculate risk score
                base_risk = 100 - mine.compliance_score
                mine.risk_score = max(10, min(95, int(base_risk * 0.6 + mine.open_violations * 3)))

    db.commit()
    db.refresh(record)

    req = db.query(ComplianceRequirement).filter(ComplianceRequirement.id == record.requirement_id).first()
    mine = db.query(Mine).filter(Mine.id == record.mine_id).first()
    return ComplianceRecordResponse(
        id=record.id, requirement_id=record.requirement_id, mine_id=record.mine_id,
        status=record.status, due_date=record.due_date, completed_date=record.completed_date,
        evidence_url=record.evidence_url, notes=record.notes,
        responsible_officer=record.responsible_officer, risk_level=record.risk_level,
        requirement_title=req.title if req else "",
        requirement_category=req.category if req else "",
        mine_name=mine.name if mine else "",
        created_at=record.created_at, updated_at=record.updated_at,
    )


@router.get("/requirements", response_model=list[ComplianceRequirementResponse])
async def get_requirements(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all compliance requirements."""
    reqs = db.query(ComplianceRequirement).filter(ComplianceRequirement.is_active == 1).all()
    return [ComplianceRequirementResponse.model_validate(r) for r in reqs]


class RequirementCreate(BaseModel):
    title: str
    category: str
    description: Optional[str] = None
    frequency: str = "monthly"
    authority: Optional[str] = None
    regulation_ref: Optional[str] = None
    source_url: Optional[str] = None
    is_illustrative: int = 1


@router.post("/requirements")
async def create_requirement(data: RequirementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    req = ComplianceRequirement(
        title=data.title,
        category=data.category,
        description=(data.description or "") + (" [Demo Requirement — Verify before production use]" if data.is_illustrative else ""),
        frequency=data.frequency,
        authority=data.authority,
        regulation_ref=data.regulation_ref,
        source_url=data.source_url or "",
        is_illustrative=data.is_illustrative,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return ComplianceRequirementResponse.model_validate(req)

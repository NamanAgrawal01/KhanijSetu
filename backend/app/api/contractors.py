from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.contractor import Contractor, Worker, Attendance
from app.auth.jwt_handler import get_current_user
from app.schemas.common import ContractorCreate, ContractorResponse, ContractorListResponse
from typing import Optional
from datetime import date, timedelta

router = APIRouter(prefix="/contractors", tags=["Contractors"])


@router.get("", response_model=ContractorListResponse)
async def get_contractors(
    mine_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Contractor)
    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(Contractor.mine_id == current_user.mine_id)
    if mine_id:
        query = query.filter(Contractor.mine_id == mine_id)
    if status:
        query = query.filter(Contractor.status == status)

    total = query.count()
    contractors = query.offset(skip).limit(limit).all()
    active = db.query(Contractor).filter(Contractor.status == "active").count()

    today = date.today()
    soon_threshold = today + timedelta(days=30)
    expiring_soon = db.query(Contractor).filter(
        Contractor.contract_end != None,
        Contractor.contract_end <= soon_threshold,
        Contractor.contract_end >= today,
    ).count()
    non_compliant = db.query(Contractor).filter(Contractor.compliance_status == "non_compliant").count()

    result = []
    for c in contractors:
        mine = db.query(Mine).filter(Mine.id == c.mine_id).first()
        result.append(ContractorResponse(
            id=c.id, name=c.name, company=c.company,
            mine_id=c.mine_id, mine_name=mine.name if mine else "",
            contract_type=c.contract_type,
            contract_start=c.contract_start, contract_end=c.contract_end,
            num_workers=c.num_workers, safety_score=c.safety_score,
            violation_count=c.violation_count,
            compliance_status=c.compliance_status,
            performance_rating=c.performance_rating,
            status=c.status, created_at=c.created_at,
        ))

    return ContractorListResponse(
        contractors=result, total=total,
        active=active, expiring_soon=expiring_soon, non_compliant=non_compliant,
    )


@router.post("", response_model=ContractorResponse)
async def create_contractor(data: ContractorCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contractor = Contractor(**data.model_dump())
    db.add(contractor)
    db.commit()
    db.refresh(contractor)
    mine = db.query(Mine).filter(Mine.id == contractor.mine_id).first()
    return ContractorResponse(
        id=contractor.id, name=contractor.name, company=contractor.company,
        mine_id=contractor.mine_id, mine_name=mine.name if mine else "",
        contract_type=contractor.contract_type,
        contract_start=contractor.contract_start, contract_end=contractor.contract_end,
        num_workers=contractor.num_workers, safety_score=contractor.safety_score,
        status=contractor.status, created_at=contractor.created_at,
    )


@router.get("/workers")
async def get_workers(mine_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Worker)
    if mine_id:
        query = query.filter(Worker.mine_id == mine_id)
    workers = query.all()
    total = len(workers)
    present = db.query(Attendance).filter(Attendance.date == date.today(), Attendance.status == "present").count()
    absent = total - present if total > present else 0
    contract_workers = sum(1 for w in workers if w.is_contract)

    return {
        "total_workers": total, "present": present,
        "absent": absent, "contract_workers": contract_workers,
        "workers": [{"id": w.id, "employee_id": w.employee_id, "name": w.name,
                      "role": w.role, "department": w.department,
                      "is_contract": w.is_contract, "status": w.status} for w in workers[:50]]
    }


@router.get("/attendance")
async def get_attendance(mine_id: Optional[int] = None, target_date: Optional[str] = None,
                         db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Attendance)
    if mine_id:
        query = query.filter(Attendance.mine_id == mine_id)
    if target_date:
        query = query.filter(Attendance.date == target_date)
    else:
        query = query.filter(Attendance.date == date.today())

    records = query.all()
    return {
        "date": target_date or date.today().isoformat(),
        "total": len(records),
        "present": sum(1 for r in records if r.status == "present"),
        "absent": sum(1 for r in records if r.status == "absent"),
        "records": [{"worker_id": r.worker_id, "status": r.status,
                      "method": r.method, "check_in": r.check_in.isoformat() if r.check_in else None}
                     for r in records[:100]]
    }


@router.put("/{contractor_id}")
async def update_contractor(contractor_id: int, data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    c = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contractor not found")
    allowed = {"name", "company", "contract_type", "num_workers", "safety_score", "status",
               "compliance_status", "performance_rating", "contact_phone", "contact_email"}
    for k, v in data.items():
        if k in allowed:
            setattr(c, k, v)
    db.commit()
    db.refresh(c)
    mine = db.query(Mine).filter(Mine.id == c.mine_id).first()
    return ContractorResponse(
        id=c.id, name=c.name, company=c.company, mine_id=c.mine_id,
        mine_name=mine.name if mine else "", contract_type=c.contract_type,
        contract_start=c.contract_start, contract_end=c.contract_end,
        num_workers=c.num_workers, safety_score=c.safety_score,
        violation_count=c.violation_count, compliance_status=c.compliance_status,
        performance_rating=c.performance_rating, status=c.status, created_at=c.created_at,
    )

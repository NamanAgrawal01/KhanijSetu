"""Workers and attendance CRUD."""
from datetime import date, datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.jwt_handler import get_current_user
from app.database import get_db
from app.models.audit import AuditLog
from app.models.contractor import Worker, Attendance, Contractor
from app.models.mine import Mine
from app.models.user import User

router = APIRouter(prefix="/workforce", tags=["Workforce"])


class WorkerCreate(BaseModel):
    name: str
    mine_id: int
    role: Optional[str] = "Miner"
    department: Optional[str] = "Mining"
    contractor_id: Optional[int] = None
    is_contract: int = 0
    training_status: str = "current"
    employee_id: Optional[str] = None


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    training_status: Optional[str] = None
    status: Optional[str] = None
    contractor_id: Optional[int] = None


class AttendanceCreate(BaseModel):
    worker_id: int
    mine_id: int
    status: str = "present"
    method: str = "manual"
    target_date: Optional[date] = None


def _scope_mine(query, current_user: User, model):
    if current_user.role == "mine_operator" and current_user.mine_id:
        return query.filter(model.mine_id == current_user.mine_id)
    return query


@router.get("/workers")
async def list_workers(
    mine_id: Optional[int] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_mine(db.query(Worker), current_user, Worker)
    if mine_id:
        query = query.filter(Worker.mine_id == mine_id)
    if search:
        query = query.filter(Worker.name.ilike(f"%{search}%") | Worker.employee_id.ilike(f"%{search}%"))
    total = query.count()
    workers = query.order_by(Worker.id).offset(skip).limit(limit).all()
    mine_map = {m.id: m.name for m in db.query(Mine).all()}
    contractor_map = {c.id: c.name for c in db.query(Contractor).all()}
    today = date.today()
    present_ids = {
        r.worker_id for r in db.query(Attendance).filter(Attendance.date == today, Attendance.status == "present").all()
    }
    return {
        "total": total,
        "present_today": len(present_ids),
        "contract_workers": db.query(Worker).filter(Worker.is_contract == 1).count(),
        "workers": [{
            "id": w.id,
            "employee_id": w.employee_id,
            "name": w.name,
            "role": w.role,
            "department": w.department,
            "mine_id": w.mine_id,
            "mine_name": mine_map.get(w.mine_id, ""),
            "contractor_id": w.contractor_id,
            "contractor_name": contractor_map.get(w.contractor_id) if w.contractor_id else "Direct",
            "is_contract": bool(w.is_contract),
            "training_status": w.training_status,
            "status": w.status,
            "present_today": w.id in present_ids,
        } for w in workers],
    }


@router.post("/workers")
async def create_worker(data: WorkerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role == "analyst":
        raise HTTPException(status_code=403, detail="Read-only role")
    count = db.query(Worker).count()
    w = Worker(
        employee_id=data.employee_id or f"EMP-{count + 1:04d}",
        name=data.name,
        mine_id=data.mine_id,
        role=data.role,
        department=data.department,
        contractor_id=data.contractor_id,
        is_contract=data.is_contract,
        training_status=data.training_status,
    )
    db.add(w)
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name, user_role=current_user.role,
        action="created", module="workers", entity="worker", details=f"Created worker {data.name}", status="success",
    ))
    db.commit()
    db.refresh(w)
    return {"id": w.id, "employee_id": w.employee_id, "name": w.name}


@router.put("/workers/{worker_id}")
async def update_worker(worker_id: int, data: WorkerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    w = db.query(Worker).filter(Worker.id == worker_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="Worker not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(w, k, v)
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name, user_role=current_user.role,
        action="updated", module="workers", entity="worker", entity_id=worker_id,
        details=f"Updated worker {w.name}", status="success",
    ))
    db.commit()
    return {"id": w.id, "name": w.name, "status": w.status}


@router.get("/attendance")
async def list_attendance(
    mine_id: Optional[int] = None,
    target_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    d = target_date or date.today()
    query = _scope_mine(db.query(Attendance), current_user, Attendance).filter(Attendance.date == d)
    if mine_id:
        query = query.filter(Attendance.mine_id == mine_id)
    records = query.all()
    workers = {w.id: w for w in db.query(Worker).all()}
    present = sum(1 for r in records if r.status == "present")
    absent = sum(1 for r in records if r.status == "absent")
    leave = sum(1 for r in records if r.status == "leave")
    return {
        "date": d.isoformat(),
        "total": len(records),
        "present": present,
        "absent": absent,
        "leave": leave,
        "records": [{
            "id": r.id,
            "worker_id": r.worker_id,
            "worker_name": workers.get(r.worker_id).name if workers.get(r.worker_id) else "",
            "employee_id": workers.get(r.worker_id).employee_id if workers.get(r.worker_id) else "",
            "mine_id": r.mine_id,
            "status": r.status,
            "method": r.method,
            "check_in": r.check_in.isoformat() if r.check_in else None,
        } for r in records[:300]],
    }


@router.post("/attendance")
async def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    d = data.target_date or date.today()
    existing = db.query(Attendance).filter(Attendance.worker_id == data.worker_id, Attendance.date == d).first()
    if existing:
        existing.status = data.status
        existing.method = data.method
        rec = existing
    else:
        rec = Attendance(
            worker_id=data.worker_id,
            mine_id=data.mine_id,
            date=d,
            status=data.status,
            method=data.method,
            check_in=datetime.now(timezone.utc) if data.status == "present" else None,
        )
        db.add(rec)
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name, user_role=current_user.role,
        action="updated", module="attendance", entity="attendance",
        details=f"Marked worker {data.worker_id} {data.status} via {data.method}", status="success",
    ))
    db.commit()
    db.refresh(rec)
    return {"id": rec.id, "status": rec.status, "date": d.isoformat()}

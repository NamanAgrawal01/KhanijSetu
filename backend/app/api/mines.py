from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.user import Subsidiary
from app.models.audit import AuditLog
from app.auth.jwt_handler import get_current_user
from app.schemas.mine import MineCreate, MineUpdate, MineResponse, MineListResponse
from typing import Optional

router = APIRouter(prefix="/mines", tags=["Mines"])


def _mine_response(mine, sub):
    return MineResponse(
        id=mine.id, name=mine.name, code=mine.code,
        subsidiary_id=mine.subsidiary_id,
        subsidiary_name=sub.name if sub else "",
        location=mine.location, district=mine.district, state=mine.state,
        latitude=mine.latitude, longitude=mine.longitude,
        mine_type=mine.mine_type, manager_name=mine.manager_name,
        capacity_mtpa=mine.capacity_mtpa, num_workers=mine.num_workers,
        status=mine.status, compliance_score=mine.compliance_score,
        risk_score=mine.risk_score, safety_score=mine.safety_score,
        environment_score=mine.environment_score,
        labour_score=mine.labour_score, production_score=mine.production_score,
        open_violations=mine.open_violations,
        last_inspection_date=mine.last_inspection_date,
        data_classification=getattr(mine, "data_classification", None) or "demo_illustrative",
        source_name=getattr(mine, "source_name", None) or "",
        source_url=getattr(mine, "source_url", None) or "",
        retrieved_date=getattr(mine, "retrieved_date", None) or "",
        created_at=mine.created_at,
    )


@router.get("", response_model=MineListResponse)
async def get_mines(
    search: Optional[str] = None,
    subsidiary_id: Optional[int] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    mine_type: Optional[str] = None,
    sort_by: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all mines with filtering, sorting, and pagination."""
    query = db.query(Mine)

    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(Mine.id == current_user.mine_id)

    if search:
        query = query.filter(
            Mine.name.ilike(f"%{search}%") | Mine.code.ilike(f"%{search}%") | Mine.location.ilike(f"%{search}%")
        )
    if subsidiary_id:
        query = query.filter(Mine.subsidiary_id == subsidiary_id)
    if status:
        query = query.filter(Mine.status == status)
    if state:
        query = query.filter(Mine.state == state)
    if district:
        query = query.filter(Mine.district == district)
    if mine_type:
        query = query.filter(Mine.mine_type == mine_type)
    if risk_level:
        if risk_level == "critical":
            query = query.filter(Mine.risk_score >= 75)
        elif risk_level == "high":
            query = query.filter(Mine.risk_score >= 50, Mine.risk_score < 75)
        elif risk_level == "medium":
            query = query.filter(Mine.risk_score >= 25, Mine.risk_score < 50)
        elif risk_level == "low":
            query = query.filter(Mine.risk_score < 25)

    # Sorting
    if sort_by == "risk_desc":
        query = query.order_by(Mine.risk_score.desc())
    elif sort_by == "risk_asc":
        query = query.order_by(Mine.risk_score.asc())
    elif sort_by == "compliance_desc":
        query = query.order_by(Mine.compliance_score.desc())
    elif sort_by == "compliance_asc":
        query = query.order_by(Mine.compliance_score.asc())
    elif sort_by == "name_asc":
        query = query.order_by(Mine.name.asc())
    elif sort_by == "name_desc":
        query = query.order_by(Mine.name.desc())
    elif sort_by == "violations_desc":
        query = query.order_by(Mine.open_violations.desc())
    else:
        query = query.order_by(Mine.id.asc())

    total = query.count()
    mines = query.offset(skip).limit(limit).all()

    result = []
    sub_cache = {}
    for mine in mines:
        if mine.subsidiary_id not in sub_cache:
            sub_cache[mine.subsidiary_id] = db.query(Subsidiary).filter(Subsidiary.id == mine.subsidiary_id).first()
        sub = sub_cache[mine.subsidiary_id]
        result.append(_mine_response(mine, sub))

    return MineListResponse(mines=result, total=total)


@router.get("/{mine_id}", response_model=MineResponse)
async def get_mine(mine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get mine by ID."""
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    sub = db.query(Subsidiary).filter(Subsidiary.id == mine.subsidiary_id).first()
    return _mine_response(mine, sub)


@router.post("", response_model=MineResponse)
async def create_mine(data: MineCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new mine. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create mines")
    mine = Mine(**data.model_dump())
    if not mine.code:
        mine.code = f"MINE-{db.query(Mine).count() + 1:03d}"
    db.add(mine)
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name,
        user_role=current_user.role, action="created", module="mines",
        entity="mine", details=f"Created mine: {mine.name} ({mine.code})",
        status="success",
    ))
    db.commit()
    db.refresh(mine)
    sub = db.query(Subsidiary).filter(Subsidiary.id == mine.subsidiary_id).first()
    return _mine_response(mine, sub)


@router.put("/{mine_id}", response_model=MineResponse)
async def update_mine(mine_id: int, data: MineUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update mine details. Admin or assigned mine_operator only."""
    if current_user.role not in ["admin", "mine_operator"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    # Mine operators can only update their own mine
    if current_user.role == "mine_operator" and current_user.mine_id != mine_id:
        raise HTTPException(status_code=403, detail="You can only update your assigned mine")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(mine, key, value)

    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name,
        user_role=current_user.role, action="updated", module="mines",
        entity="mine", entity_id=mine_id,
        details=f"Updated mine: {mine.name} — fields: {', '.join(update_data.keys())}",
        status="success",
    ))
    db.commit()
    db.refresh(mine)
    sub = db.query(Subsidiary).filter(Subsidiary.id == mine.subsidiary_id).first()
    return _mine_response(mine, sub)


@router.patch("/{mine_id}/archive")
async def archive_mine(mine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Archive a mine (set status to archived)."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can archive mines")
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    mine.status = "archived"
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name,
        user_role=current_user.role, action="archived", module="mines",
        entity="mine", entity_id=mine_id,
        details=f"Archived mine: {mine.name}",
        status="success",
    ))
    db.commit()
    return {"status": "success", "message": f"Mine '{mine.name}' archived"}


@router.patch("/{mine_id}/restore")
async def restore_mine(mine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Restore an archived mine."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can restore mines")
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    mine.status = "operational"
    db.add(AuditLog(
        user_id=current_user.id, user_name=current_user.name,
        user_role=current_user.role, action="restored", module="mines",
        entity="mine", entity_id=mine_id,
        details=f"Restored mine: {mine.name}",
        status="success",
    ))
    db.commit()
    return {"status": "success", "message": f"Mine '{mine.name}' restored"}

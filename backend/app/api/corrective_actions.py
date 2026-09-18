from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.violation import Violation
from app.models.corrective_action import CorrectiveAction
from app.auth.jwt_handler import get_current_user
from app.schemas.corrective_action import (
    CorrectiveActionCreate, CorrectiveActionUpdate,
    CorrectiveActionResponse, CorrectiveActionListResponse
)
from typing import Optional
from datetime import date

router = APIRouter(prefix="/corrective-actions", tags=["Corrective Actions"])


@router.get("", response_model=CorrectiveActionListResponse)
async def get_corrective_actions(
    mine_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(CorrectiveAction)
    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(CorrectiveAction.mine_id == current_user.mine_id)
    if mine_id:
        query = query.filter(CorrectiveAction.mine_id == mine_id)
    if status:
        query = query.filter(CorrectiveAction.status == status)

    total = query.count()
    actions = query.order_by(CorrectiveAction.deadline.asc()).offset(skip).limit(limit).all()

    pending = db.query(CorrectiveAction).filter(CorrectiveAction.status == "pending").count()
    in_progress = db.query(CorrectiveAction).filter(CorrectiveAction.status == "in_progress").count()
    overdue = db.query(CorrectiveAction).filter(CorrectiveAction.status == "overdue").count()
    submitted = db.query(CorrectiveAction).filter(CorrectiveAction.status == "submitted").count()
    verified = db.query(CorrectiveAction).filter(CorrectiveAction.status == "verified").count()
    closed = db.query(CorrectiveAction).filter(CorrectiveAction.status == "closed").count()

    result = []
    for a in actions:
        mine = db.query(Mine).filter(Mine.id == a.mine_id).first()
        violation = db.query(Violation).filter(Violation.id == a.violation_id).first()
        result.append(CorrectiveActionResponse(
            id=a.id, action_code=a.action_code, violation_id=a.violation_id,
            mine_id=a.mine_id, mine_name=mine.name if mine else "",
            title=a.title, description=a.description,
            assigned_to_name=a.assigned_to_name, deadline=a.deadline,
            priority=a.priority, status=a.status,
            evidence_url=a.evidence_url, evidence_notes=a.evidence_notes,
            verified_by_name=a.verified_by_name, verified_date=a.verified_date,
            verification_notes=a.verification_notes,
            violation_title=violation.title if violation else "",
            created_at=a.created_at, updated_at=a.updated_at,
        ))

    return CorrectiveActionListResponse(
        actions=result, total=total,
        pending=pending, in_progress=in_progress, overdue=overdue,
        submitted=submitted, verified=verified, closed=closed,
    )


@router.post("", response_model=CorrectiveActionResponse)
async def create_corrective_action(data: CorrectiveActionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = db.query(CorrectiveAction).count()
    action = CorrectiveAction(
        action_code=f"CA-2026-{count + 1:04d}",
        violation_id=data.violation_id, mine_id=data.mine_id,
        title=data.title, description=data.description,
        assigned_to_name=data.assigned_to_name, deadline=data.deadline,
        priority=data.priority,
    )
    db.add(action)

    # Update violation status
    violation = db.query(Violation).filter(Violation.id == data.violation_id).first()
    if violation and violation.status in ["detected", "assigned"]:
        violation.status = "assigned"

    db.commit()
    db.refresh(action)

    mine = db.query(Mine).filter(Mine.id == action.mine_id).first()
    return CorrectiveActionResponse(
        id=action.id, action_code=action.action_code,
        violation_id=action.violation_id, mine_id=action.mine_id,
        mine_name=mine.name if mine else "",
        title=action.title, description=action.description,
        assigned_to_name=action.assigned_to_name, deadline=action.deadline,
        priority=action.priority, status=action.status,
        violation_title=violation.title if violation else "",
        created_at=action.created_at, updated_at=action.updated_at,
    )


@router.put("/{action_id}", response_model=CorrectiveActionResponse)
async def update_corrective_action(action_id: int, data: CorrectiveActionUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    action = db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Corrective action not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(action, key, value)

    # Handle workflow transitions
    if data.status == "submitted":
        action.evidence_url = data.evidence_url
        action.evidence_notes = data.evidence_notes

    if data.status == "verified":
        action.verified_by_name = data.verified_by_name or current_user.name
        action.verified_date = date.today()
        action.verification_notes = data.verification_notes
        # Update associated violation
        violation = db.query(Violation).filter(Violation.id == action.violation_id).first()
        if violation:
            violation.status = "verified"

    if data.status == "closed":
        violation = db.query(Violation).filter(Violation.id == action.violation_id).first()
        if violation:
            violation.status = "closed"
        # Improve mine scores
        mine = db.query(Mine).filter(Mine.id == action.mine_id).first()
        if mine:
            mine.open_violations = max(0, (mine.open_violations or 0) - 1)
            mine.compliance_score = min(100, mine.compliance_score + 3)
            mine.risk_score = max(10, mine.risk_score - 5)

    db.commit()
    db.refresh(action)

    mine = db.query(Mine).filter(Mine.id == action.mine_id).first()
    violation = db.query(Violation).filter(Violation.id == action.violation_id).first()
    return CorrectiveActionResponse(
        id=action.id, action_code=action.action_code,
        violation_id=action.violation_id, mine_id=action.mine_id,
        mine_name=mine.name if mine else "",
        title=action.title, description=action.description,
        assigned_to_name=action.assigned_to_name, deadline=action.deadline,
        priority=action.priority, status=action.status,
        evidence_url=action.evidence_url, evidence_notes=action.evidence_notes,
        verified_by_name=action.verified_by_name, verified_date=action.verified_date,
        verification_notes=action.verification_notes,
        violation_title=violation.title if violation else "",
        created_at=action.created_at, updated_at=action.updated_at,
    )

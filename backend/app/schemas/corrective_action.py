from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class CorrectiveActionCreate(BaseModel):
    violation_id: int
    mine_id: int
    title: str
    description: Optional[str] = None
    assigned_to_name: Optional[str] = None
    deadline: date
    priority: str = "medium"

class CorrectiveActionUpdate(BaseModel):
    status: Optional[str] = None
    evidence_url: Optional[str] = None
    evidence_notes: Optional[str] = None
    verified_by_name: Optional[str] = None
    verification_notes: Optional[str] = None

class CorrectiveActionResponse(BaseModel):
    id: int
    action_code: str
    violation_id: int
    mine_id: int
    mine_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    assigned_to_name: Optional[str] = None
    deadline: date
    priority: str
    status: str
    evidence_url: Optional[str] = None
    evidence_notes: Optional[str] = None
    verified_by_name: Optional[str] = None
    verified_date: Optional[date] = None
    verification_notes: Optional[str] = None
    violation_title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class CorrectiveActionListResponse(BaseModel):
    actions: list[CorrectiveActionResponse]
    total: int
    pending: int = 0
    in_progress: int = 0
    overdue: int = 0
    submitted: int = 0
    verified: int = 0
    closed: int = 0

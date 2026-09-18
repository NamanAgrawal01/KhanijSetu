from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ViolationCreate(BaseModel):
    mine_id: int
    category: str
    severity: str = "medium"
    title: str
    description: Optional[str] = None
    reported_by_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    detected_date: date
    deadline: Optional[date] = None
    inspection_id: Optional[int] = None

class ViolationUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_to_name: Optional[str] = None
    deadline: Optional[date] = None
    resolution_notes: Optional[str] = None
    evidence_url: Optional[str] = None

class ViolationResponse(BaseModel):
    id: int
    violation_code: str
    mine_id: int
    mine_name: Optional[str] = None
    category: str
    severity: str
    title: str
    description: Optional[str] = None
    reported_by_name: Optional[str] = None
    assigned_to_name: Optional[str] = None
    detected_date: date
    deadline: Optional[date] = None
    status: str
    resolution_notes: Optional[str] = None
    evidence_url: Optional[str] = None
    is_recurring: int = 0
    recurrence_count: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ViolationListResponse(BaseModel):
    violations: list[ViolationResponse]
    total: int

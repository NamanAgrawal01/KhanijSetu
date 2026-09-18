from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class ComplianceRequirementResponse(BaseModel):
    id: int
    title: str
    category: str
    description: Optional[str] = None
    frequency: str = "monthly"
    authority: Optional[str] = None
    regulation_ref: Optional[str] = None
    class Config:
        from_attributes = True

class ComplianceRecordBase(BaseModel):
    requirement_id: int
    mine_id: int
    status: Optional[str] = "pending"
    due_date: date
    responsible_officer: Optional[str] = None
    notes: Optional[str] = None

class ComplianceRecordCreate(ComplianceRecordBase):
    pass

class ComplianceRecordUpdate(BaseModel):
    status: Optional[str] = None
    completed_date: Optional[date] = None
    evidence_url: Optional[str] = None
    notes: Optional[str] = None
    risk_level: Optional[str] = None

class ComplianceRecordResponse(ComplianceRecordBase):
    id: int
    completed_date: Optional[date] = None
    evidence_url: Optional[str] = None
    risk_level: str = "low"
    requirement_title: Optional[str] = None
    requirement_category: Optional[str] = None
    mine_name: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ComplianceListResponse(BaseModel):
    records: list[ComplianceRecordResponse]
    total: int
    requirements: list[ComplianceRequirementResponse] = []

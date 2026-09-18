from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class InspectionCreate(BaseModel):
    mine_id: int
    inspector_id: Optional[int] = None
    inspection_type: str = "routine"
    scheduled_date: date
    priority: str = "normal"

class InspectionUpdate(BaseModel):
    status: Optional[str] = None
    completed_date: Optional[date] = None
    overall_rating: Optional[str] = None
    findings_summary: Optional[str] = None
    recommendations: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None

class InspectionItemCreate(BaseModel):
    category: str
    item_name: str
    status: str = "pending"
    severity: Optional[str] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None

class InspectionItemResponse(BaseModel):
    id: int
    category: str
    item_name: str
    status: str
    severity: Optional[str] = None
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    class Config:
        from_attributes = True

class InspectionResponse(BaseModel):
    id: int
    mine_id: int
    mine_name: Optional[str] = None
    inspector_id: int
    inspector_name: Optional[str] = None
    inspection_type: str
    scheduled_date: date
    completed_date: Optional[date] = None
    status: str
    priority: str
    overall_rating: Optional[str] = None
    findings_summary: Optional[str] = None
    recommendations: Optional[str] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    items: list[InspectionItemResponse] = []
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class InspectionListResponse(BaseModel):
    inspections: list[InspectionResponse]
    total: int
    scheduled: int = 0
    in_progress: int = 0
    completed: int = 0
    overdue: int = 0

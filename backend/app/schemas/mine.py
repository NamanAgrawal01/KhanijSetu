from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MineBase(BaseModel):
    name: str
    code: Optional[str] = None
    subsidiary_id: int
    location: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = "Jharkhand"
    latitude: Optional[float] = 23.7957
    longitude: Optional[float] = 86.4304
    mine_type: Optional[str] = "Underground"
    manager_name: Optional[str] = None
    capacity_mtpa: Optional[float] = 1.0
    num_workers: Optional[int] = 0
    status: Optional[str] = "operational"

class MineCreate(MineBase):
    pass

class MineUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    manager_name: Optional[str] = None
    compliance_score: Optional[float] = None
    risk_score: Optional[int] = None

class MineResponse(MineBase):
    id: int
    compliance_score: float = 75.0
    risk_score: int = 50
    safety_score: float = 70.0
    environment_score: float = 75.0
    labour_score: float = 80.0
    production_score: float = 70.0
    open_violations: int = 0
    last_inspection_date: Optional[datetime] = None
    subsidiary_name: Optional[str] = None
    data_classification: Optional[str] = "demo_illustrative"
    source_name: Optional[str] = ""
    source_url: Optional[str] = ""
    retrieved_date: Optional[str] = ""
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MineListResponse(BaseModel):
    mines: list[MineResponse]
    total: int

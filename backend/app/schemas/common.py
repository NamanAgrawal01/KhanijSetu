from pydantic import BaseModel
from typing import Optional, Any
from datetime import date, datetime


class ContractorCreate(BaseModel):
    name: str
    company: Optional[str] = None
    mine_id: int
    contract_type: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    num_workers: int = 0
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

class ContractorResponse(BaseModel):
    id: int
    name: str
    company: Optional[str] = None
    mine_id: int
    mine_name: Optional[str] = None
    contract_type: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    num_workers: int = 0
    safety_score: float = 75.0
    violation_count: int = 0
    compliance_status: str = "compliant"
    performance_rating: str = "good"
    status: str = "active"
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class ContractorListResponse(BaseModel):
    contractors: list[ContractorResponse]
    total: int
    active: int = 0
    expiring_soon: int = 0
    non_compliant: int = 0

class ProductionRecordResponse(BaseModel):
    id: int
    mine_id: int
    mine_name: Optional[str] = None
    date: date
    shift: str = "day"
    target_tonnes: float = 0
    actual_tonnes: float = 0
    overburden_removed: float = 0
    equipment_hours: float = 0
    downtime_hours: float = 0
    downtime_reason: Optional[str] = None
    safety_incidents: int = 0
    class Config:
        from_attributes = True

class ProductionListResponse(BaseModel):
    records: list[ProductionRecordResponse]
    total: int
    daily_avg_target: float = 0
    daily_avg_actual: float = 0
    total_downtime: float = 0

class FieldReportCreate(BaseModel):
    mine_id: int
    observation_type: str
    severity: str = "medium"
    title: Optional[str] = None
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_label: Optional[str] = None
    photo_url: Optional[str] = None

class FieldReportResponse(BaseModel):
    id: int
    report_code: str
    mine_id: int
    mine_name: Optional[str] = None
    reporter_id: int
    reporter_name: Optional[str] = None
    observation_type: str
    severity: str
    title: Optional[str] = None
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_label: Optional[str] = None
    photo_url: Optional[str] = None
    status: str
    sync_status: str = "synced"
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class FieldReportListResponse(BaseModel):
    reports: list[FieldReportResponse]
    total: int

class AlertResponse(BaseModel):
    id: int
    mine_id: Optional[int] = None
    mine_name: Optional[str] = None
    type: str
    severity: str
    title: str
    message: Optional[str] = None
    status: str
    escalation_level: int = 0
    source: Optional[str] = None
    link: Optional[str] = None
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    critical: int = 0
    high: int = 0
    warning: int = 0
    info: int = 0

class AuditLogResponse(BaseModel):
    id: int
    user_name: Optional[str] = None
    user_role: Optional[str] = None
    action: str
    module: str
    entity: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    status: str = "success"
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    total: int

class DashboardResponse(BaseModel):
    total_mines: int = 0
    overall_compliance: float = 0
    high_risk_mines: int = 0
    critical_issues: int = 0
    open_violations: int = 0
    pending_actions: int = 0
    compliance_trend: list[dict] = []
    compliance_by_category: list[dict] = []
    risk_distribution: list[dict] = []
    violations_by_category: list[dict] = []
    high_risk_mine_list: list[dict] = []
    recent_activity: list[dict] = []
    active_mines: int = 0
    critical_mines: int = 0
    overdue_actions: int = 0
    upcoming_inspections: int = 0

class RiskResponse(BaseModel):
    mine_id: int
    mine_name: str
    risk_score: int
    risk_level: str
    factors: list[dict] = []
    explanation: str = ""
    trend: list[dict] = []
    recommendations: list[str] = []

class AIQueryRequest(BaseModel):
    query: str
    context: Optional[dict] = None

class AIQueryResponse(BaseModel):
    answer: str
    data: Optional[Any] = None
    entities: list[dict] = []
    recommendations: list[str] = []
    confidence: float = 0.85

class ReportRequest(BaseModel):
    report_type: str
    mine_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class ReportResponse(BaseModel):
    id: str
    report_type: str
    title: str
    generated_at: datetime
    data: Any = None
    summary: str = ""

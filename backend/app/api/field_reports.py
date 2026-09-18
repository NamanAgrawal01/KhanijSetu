from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.field_report import FieldReport
from app.auth.jwt_handler import get_current_user
from app.schemas.common import FieldReportCreate, FieldReportResponse, FieldReportListResponse
from typing import Optional

router = APIRouter(prefix="/field-reports", tags=["Field Reports"])


@router.get("", response_model=FieldReportListResponse)
async def get_field_reports(
    mine_id: Optional[int] = None,
    severity: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FieldReport)
    if current_user.role == "inspector":
        query = query.filter(FieldReport.reporter_id == current_user.id)
    if mine_id:
        query = query.filter(FieldReport.mine_id == mine_id)
    if severity:
        query = query.filter(FieldReport.severity == severity)

    total = query.count()
    reports = query.order_by(FieldReport.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for r in reports:
        mine = db.query(Mine).filter(Mine.id == r.mine_id).first()
        result.append(FieldReportResponse(
            id=r.id, report_code=r.report_code, mine_id=r.mine_id,
            mine_name=mine.name if mine else "",
            reporter_id=r.reporter_id, reporter_name=r.reporter_name,
            observation_type=r.observation_type, severity=r.severity,
            title=r.title, description=r.description,
            latitude=r.latitude, longitude=r.longitude,
            location_label=r.location_label, photo_url=r.photo_url,
            status=r.status, sync_status=r.sync_status,
            created_at=r.created_at,
        ))
    return FieldReportListResponse(reports=result, total=total)


@router.post("", response_model=FieldReportResponse)
async def create_field_report(data: FieldReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = db.query(FieldReport).count()
    report = FieldReport(
        report_code=f"FR-2026-{count + 1:04d}",
        mine_id=data.mine_id,
        reporter_id=current_user.id,
        reporter_name=current_user.name,
        observation_type=data.observation_type,
        severity=data.severity,
        title=data.title,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        location_label=data.location_label or ("Demo Location" if not data.latitude else "GPS Captured"),
        photo_url=data.photo_url,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    mine = db.query(Mine).filter(Mine.id == report.mine_id).first()
    return FieldReportResponse(
        id=report.id, report_code=report.report_code, mine_id=report.mine_id,
        mine_name=mine.name if mine else "",
        reporter_id=report.reporter_id, reporter_name=report.reporter_name,
        observation_type=report.observation_type, severity=report.severity,
        title=report.title, description=report.description,
        latitude=report.latitude, longitude=report.longitude,
        location_label=report.location_label, photo_url=report.photo_url,
        status=report.status, sync_status=report.sync_status,
        created_at=report.created_at,
    )

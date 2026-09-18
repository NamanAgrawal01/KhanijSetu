"""
KhanijSetu Export API — CSV / XLSX export for all modules.
"""
import csv
import io
from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, Subsidiary
from app.models.mine import Mine
from app.models.compliance import ComplianceRequirement, ComplianceRecord
from app.models.inspection import Inspection
from app.models.violation import Violation
from app.models.corrective_action import CorrectiveAction
from app.models.contractor import Contractor, Worker, Attendance
from app.models.production import ProductionRecord
from app.models.field_report import FieldReport
from app.models.alert import Alert
from app.models.audit import AuditLog
from app.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/export", tags=["Export"])


def _to_csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    if not rows:
        rows = [{"message": "No records found"}]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _to_xlsx_response(rows: list[dict], filename: str) -> StreamingResponse:
    try:
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        if not rows:
            rows = [{"message": "No records found"}]
        headers = list(rows[0].keys())
        ws.append(headers)
        for row in rows:
            ws.append([str(v) if v is not None else "" for v in row.values()])
        # Auto-width
        for col_idx, header in enumerate(headers, 1):
            ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = max(len(header) + 4, 15)
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ImportError:
        return _to_csv_response(rows, filename.replace(".xlsx", ".csv"))


def _serialize(val):
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return val


@router.get("/mines")
async def export_mines(
    format: str = "csv",
    state: Optional[str] = None,
    subsidiary_id: Optional[int] = None,
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Mine)
    # Scope: mine_operators only see their own mine
    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(Mine.id == current_user.mine_id)
    if state:
        query = query.filter(Mine.state == state)
    if subsidiary_id:
        query = query.filter(Mine.subsidiary_id == subsidiary_id)
    if status:
        query = query.filter(Mine.status == status)
    if risk_level:
        if risk_level == "critical":
            query = query.filter(Mine.risk_score >= 75)
        elif risk_level == "high":
            query = query.filter(Mine.risk_score >= 50, Mine.risk_score < 75)
        elif risk_level == "medium":
            query = query.filter(Mine.risk_score >= 25, Mine.risk_score < 50)
        elif risk_level == "low":
            query = query.filter(Mine.risk_score < 25)

    mines = query.all()
    rows = []
    for m in mines:
        sub = db.query(Subsidiary).filter(Subsidiary.id == m.subsidiary_id).first()
        rows.append({
            "Mine ID": m.id, "Name": m.name, "Code": m.code,
            "Subsidiary": sub.name if sub else "", "State": m.state,
            "District": m.district, "Location": m.location,
            "Type": m.mine_type, "Status": m.status,
            "Manager": m.manager_name, "Workers": m.num_workers,
            "Capacity (MTPA)": m.capacity_mtpa,
            "Compliance Score": m.compliance_score, "Risk Score": m.risk_score,
            "Safety Score": m.safety_score, "Environment Score": m.environment_score,
            "Open Violations": m.open_violations,
            "Last Inspection": _serialize(m.last_inspection_date),
        })
    fn = f"khanijsetu_mines_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/compliance")
async def export_compliance(
    format: str = "csv",
    mine_id: Optional[int] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ComplianceRecord)
    if mine_id:
        query = query.filter(ComplianceRecord.mine_id == mine_id)
    if status:
        query = query.filter(ComplianceRecord.status == status)
    if category:
        query = query.join(ComplianceRequirement).filter(ComplianceRequirement.category == category)
    records = query.all()
    rows = []
    for r in records:
        req = db.query(ComplianceRequirement).filter(ComplianceRequirement.id == r.requirement_id).first()
        mine = db.query(Mine).filter(Mine.id == r.mine_id).first()
        rows.append({
            "ID": r.id, "Requirement": req.title if req else "",
            "Category": req.category if req else "", "Mine": mine.name if mine else "",
            "Status": r.status, "Due Date": _serialize(r.due_date),
            "Completed Date": _serialize(r.completed_date),
            "Responsible Officer": r.responsible_officer, "Risk Level": r.risk_level,
        })
    fn = f"khanijsetu_compliance_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/violations")
async def export_violations(
    format: str = "csv",
    mine_id: Optional[int] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Violation)
    if mine_id:
        query = query.filter(Violation.mine_id == mine_id)
    if category:
        query = query.filter(Violation.category == category)
    if severity:
        query = query.filter(Violation.severity == severity)
    if status:
        query = query.filter(Violation.status == status)
    violations = query.all()
    rows = []
    for v in violations:
        mine = db.query(Mine).filter(Mine.id == v.mine_id).first()
        rows.append({
            "Code": v.violation_code, "Mine": mine.name if mine else "",
            "Category": v.category, "Severity": v.severity,
            "Title": v.title, "Status": v.status,
            "Reported By": v.reported_by_name, "Assigned To": v.assigned_to_name,
            "Detected": _serialize(v.detected_date), "Deadline": _serialize(v.deadline),
            "Recurring": "Yes" if v.is_recurring else "No",
            "Recurrence Count": v.recurrence_count,
        })
    fn = f"khanijsetu_violations_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/inspections")
async def export_inspections(
    format: str = "csv",
    mine_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Inspection)
    if mine_id:
        query = query.filter(Inspection.mine_id == mine_id)
    if status:
        query = query.filter(Inspection.status == status)
    inspections = query.all()
    rows = []
    for i in inspections:
        mine = db.query(Mine).filter(Mine.id == i.mine_id).first()
        inspector = db.query(User).filter(User.id == i.inspector_id).first()
        rows.append({
            "ID": i.id, "Mine": mine.name if mine else "",
            "Inspector": inspector.name if inspector else "",
            "Type": i.inspection_type, "Status": i.status,
            "Priority": i.priority, "Rating": i.overall_rating or "",
            "Scheduled": _serialize(i.scheduled_date),
            "Completed": _serialize(i.completed_date),
            "Findings": i.findings_summary or "",
        })
    fn = f"khanijsetu_inspections_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/corrective-actions")
async def export_corrective_actions(
    format: str = "csv",
    mine_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(CorrectiveAction)
    if mine_id:
        query = query.filter(CorrectiveAction.mine_id == mine_id)
    if status:
        query = query.filter(CorrectiveAction.status == status)
    actions = query.all()
    rows = []
    for a in actions:
        mine = db.query(Mine).filter(Mine.id == a.mine_id).first()
        violation = db.query(Violation).filter(Violation.id == a.violation_id).first()
        rows.append({
            "Code": a.action_code, "Mine": mine.name if mine else "",
            "Violation": violation.title if violation else "",
            "Title": a.title, "Assigned To": a.assigned_to_name,
            "Deadline": _serialize(a.deadline), "Priority": a.priority,
            "Status": a.status, "Verified By": a.verified_by_name or "",
            "Verified Date": _serialize(a.verified_date),
        })
    fn = f"khanijsetu_corrective_actions_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/contractors")
async def export_contractors(
    format: str = "csv",
    mine_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Contractor)
    if mine_id:
        query = query.filter(Contractor.mine_id == mine_id)
    contractors = query.all()
    rows = []
    for c in contractors:
        mine = db.query(Mine).filter(Mine.id == c.mine_id).first()
        rows.append({
            "ID": c.id, "Name": c.name, "Company": c.company,
            "Mine": mine.name if mine else "", "Contract Type": c.contract_type,
            "Start": _serialize(c.contract_start), "End": _serialize(c.contract_end),
            "Workers": c.num_workers, "Safety Score": c.safety_score,
            "Violations": c.violation_count, "Compliance": c.compliance_status,
            "Performance": c.performance_rating, "Status": c.status,
        })
    fn = f"khanijsetu_contractors_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/workers")
async def export_workers(
    format: str = "csv",
    mine_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Worker)
    if mine_id:
        query = query.filter(Worker.mine_id == mine_id)
    workers = query.all()
    rows = []
    for w in workers:
        mine = db.query(Mine).filter(Mine.id == w.mine_id).first()
        contractor = db.query(Contractor).filter(Contractor.id == w.contractor_id).first() if w.contractor_id else None
        rows.append({
            "Employee ID": w.employee_id, "Name": w.name, "Role": w.role,
            "Department": w.department, "Mine": mine.name if mine else "",
            "Contractor": contractor.name if contractor else "Direct",
            "Contract Worker": "Yes" if w.is_contract else "No",
            "Training Status": w.training_status, "Status": w.status,
        })
    fn = f"khanijsetu_workers_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/production")
async def export_production(
    format: str = "csv",
    mine_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ProductionRecord)
    if mine_id:
        query = query.filter(ProductionRecord.mine_id == mine_id)
    records = query.order_by(ProductionRecord.date.desc()).all()
    rows = []
    for r in records:
        mine = db.query(Mine).filter(Mine.id == r.mine_id).first()
        rows.append({
            "Date": _serialize(r.date), "Mine": mine.name if mine else "",
            "Shift": r.shift, "Target (tonnes)": r.target_tonnes,
            "Actual (tonnes)": r.actual_tonnes,
            "Achievement %": round((r.actual_tonnes / r.target_tonnes * 100), 1) if r.target_tonnes > 0 else 0,
            "Downtime (hrs)": r.downtime_hours,
            "Downtime Reason": r.downtime_reason or "",
            "Safety Incidents": r.safety_incidents,
        })
    fn = f"khanijsetu_production_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/alerts")
async def export_alerts(
    format: str = "csv",
    severity: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Alert)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    alerts = query.order_by(Alert.created_at.desc()).all()
    rows = []
    for a in alerts:
        rows.append({
            "ID": a.id, "Mine": a.mine_name or "",
            "Type": a.type, "Severity": a.severity,
            "Title": a.title, "Status": a.status,
            "Escalation Level": a.escalation_level,
            "Source": a.source or "", "Created": _serialize(a.created_at),
        })
    fn = f"khanijsetu_alerts_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")


@router.get("/audit-logs")
async def export_audit_logs(
    format: str = "csv",
    module: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(AuditLog)
    if module:
        query = query.filter(AuditLog.module == module)
    logs = query.order_by(AuditLog.created_at.desc()).limit(500).all()
    rows = []
    for l in logs:
        rows.append({
            "ID": l.id, "User": l.user_name or "",
            "Role": l.user_role or "", "Action": l.action,
            "Module": l.module, "Entity": l.entity or "",
            "Entity ID": l.entity_id, "Details": l.details or "",
            "Status": l.status, "Timestamp": _serialize(l.created_at),
        })
    fn = f"khanijsetu_audit_{date.today().isoformat()}"
    if format == "xlsx":
        return _to_xlsx_response(rows, fn + ".xlsx")
    return _to_csv_response(rows, fn + ".csv")

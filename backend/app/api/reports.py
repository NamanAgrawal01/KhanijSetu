from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.violation import Violation
from app.models.compliance import ComplianceRecord
from app.models.inspection import Inspection
from app.auth.jwt_handler import get_current_user
from app.schemas.common import ReportRequest, ReportResponse
from datetime import datetime, timezone, date
import uuid

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("")
async def get_report_types(current_user: User = Depends(get_current_user)):
    """Get available report types."""
    return {
        "report_types": [
            {"id": "monthly_compliance", "name": "Monthly Compliance Report", "description": "Comprehensive monthly compliance status across all mines"},
            {"id": "mine_inspection", "name": "Mine Inspection Report", "description": "Detailed inspection findings and checklist results"},
            {"id": "risk_assessment", "name": "Risk Assessment Report", "description": "Mine-wise risk scoring with factor analysis"},
            {"id": "violation_report", "name": "Violation Report", "description": "Open and resolved violations with trend analysis"},
            {"id": "contractor_compliance", "name": "Contractor Compliance Report", "description": "Contractor safety performance and contract status"},
            {"id": "environmental_summary", "name": "Environmental Summary", "description": "Environmental monitoring and compliance metrics"},
            {"id": "management_summary", "name": "Management Summary", "description": "Executive overview of governance and operational metrics"},
        ]
    }


@router.post("/generate")
async def generate_report(
    data: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a report based on type and parameters."""
    report_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc)

    mines = db.query(Mine).all()
    total_mines = len(mines)
    avg_compliance = sum(m.compliance_score for m in mines) / total_mines if total_mines else 0
    high_risk = sum(1 for m in mines if m.risk_score >= 70)
    total_violations = db.query(Violation).count()
    open_violations = db.query(Violation).filter(Violation.status.in_(["detected", "assigned", "in_progress"])).count()

    if data.report_type == "monthly_compliance":
        report_data = {
            "period": "September 2026",
            "total_mines": total_mines,
            "overall_compliance": round(avg_compliance, 1),
            "categories": [
                {"name": "Safety", "compliance": 72, "trend": "+3.2%"},
                {"name": "Environment", "compliance": 68, "trend": "-1.5%"},
                {"name": "Labour", "compliance": 84, "trend": "+5.1%"},
                {"name": "Production", "compliance": 76, "trend": "+2.8%"},
                {"name": "Equipment", "compliance": 71, "trend": "+1.2%"},
                {"name": "Documentation", "compliance": 80, "trend": "+4.0%"},
            ],
            "overdue_items": 14,
            "completed_items": 156,
            "high_risk_mines": [{"name": m.name, "compliance": m.compliance_score, "risk": m.risk_score} for m in sorted(mines, key=lambda x: x.risk_score, reverse=True)[:5]],
            "recommendations": [
                "Address 14 overdue compliance items within 7 days",
                "Focus on environmental compliance improvement across ECL subsidiary",
                "Schedule additional safety inspections at high-risk mines",
                "Review contractor compliance documentation",
            ]
        }
        summary = f"Monthly compliance stands at {round(avg_compliance, 1)}% across {total_mines} mines. {high_risk} mines classified as high risk."
        title = "Monthly Compliance Report — September 2026"

    elif data.report_type == "violation_report":
        report_data = {
            "total_violations": total_violations,
            "open": open_violations,
            "resolved_this_month": 15,
            "by_category": [
                {"category": "Safety", "count": 14, "percentage": 37.8},
                {"category": "Environment", "count": 8, "percentage": 21.6},
                {"category": "Equipment", "count": 7, "percentage": 18.9},
                {"category": "Labour", "count": 5, "percentage": 13.5},
                {"category": "Documentation", "count": 3, "percentage": 8.1},
            ],
            "recurring_count": 3,
            "avg_resolution_days": 12,
        }
        summary = f"{total_violations} total violations tracked. {open_violations} currently open. Average resolution time: 12 days."
        title = "Violation Report — September 2026"

    elif data.report_type == "management_summary":
        report_data = {
            "total_mines": total_mines,
            "compliance": round(avg_compliance, 1),
            "high_risk": high_risk,
            "violations": open_violations,
            "inspections_completed": 28,
            "corrective_actions_closed": 18,
            "key_achievements": [
                "Overall compliance improved by 4.2% over last month",
                "15 violations resolved and verified",
                "Inspector report submission rate improved to 94%",
            ],
            "areas_of_concern": [
                f"{high_risk} mines classified as high risk",
                "PPE violations recurring across 3 mines",
                "Environmental compliance declining in ECL subsidiary",
            ],
        }
        summary = f"Management overview: {total_mines} mines, {round(avg_compliance, 1)}% compliance, {high_risk} high-risk mines."
        title = "Management Summary Report — September 2026"

    else:
        report_data = {
            "total_mines": total_mines,
            "compliance": round(avg_compliance, 1),
            "details": "Report generated successfully with current data."
        }
        summary = "Report generated successfully."
        title = f"{data.report_type.replace('_', ' ').title()} — September 2026"

    return ReportResponse(
        id=report_id, report_type=data.report_type,
        title=title, generated_at=now,
        data=report_data, summary=summary,
    )

"""Deterministic risk and compliance scoring from live database records."""
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.orm import Session

from app.models.mine import Mine
from app.models.compliance import ComplianceRecord, ComplianceRequirement
from app.models.violation import Violation
from app.models.corrective_action import CorrectiveAction
from app.models.inspection import Inspection, InspectionItem
from app.models.contractor import Contractor
from app.models.production import ProductionRecord


OPEN_VIOLATION_STATUSES = ("detected", "assigned", "in_progress")
OPEN_CA_STATUSES = ("pending", "in_progress", "overdue", "submitted")


def risk_level(score: int) -> str:
    if score >= 76:
        return "CRITICAL"
    if score >= 51:
        return "HIGH"
    if score >= 26:
        return "MEDIUM"
    return "LOW"


def _category_score(db: Session, mine_id: int, category: str) -> float:
    req_ids = [r.id for r in db.query(ComplianceRequirement).filter(ComplianceRequirement.category == category).all()]
    if not req_ids:
        return 75.0
    q = db.query(ComplianceRecord).filter(
        ComplianceRecord.mine_id == mine_id,
        ComplianceRecord.requirement_id.in_(req_ids),
    )
    total = q.count()
    if total == 0:
        return 75.0
    completed = q.filter(ComplianceRecord.status == "completed").count()
    overdue = q.filter(ComplianceRecord.status == "overdue").count()
    return round(max(0, min(100, (completed / total) * 100 - overdue * 4)), 1)


def explain_mine_risk(db: Session, mine: Mine) -> dict:
    today = date.today()
    open_v = db.query(Violation).filter(
        Violation.mine_id == mine.id, Violation.status.in_(OPEN_VIOLATION_STATUSES)
    ).all()
    overdue_req = db.query(ComplianceRecord).filter(
        ComplianceRecord.mine_id == mine.id, ComplianceRecord.status == "overdue"
    ).count()
    open_ca = db.query(CorrectiveAction).filter(
        CorrectiveAction.mine_id == mine.id, CorrectiveAction.status.in_(OPEN_CA_STATUSES)
    ).count()
    overdue_ca = db.query(CorrectiveAction).filter(
        CorrectiveAction.mine_id == mine.id,
        CorrectiveAction.deadline < today,
        CorrectiveAction.status.in_(("pending", "in_progress", "overdue")),
    ).count()
    critical_v = sum(1 for v in open_v if v.severity == "critical")
    high_v = sum(1 for v in open_v if v.severity == "high")
    safety_v = sum(1 for v in open_v if v.category == "safety")
    env_v = sum(1 for v in open_v if v.category == "environment")
    ppe = sum(1 for v in open_v if "ppe" in (v.title or "").lower() or "ppe" in (v.description or "").lower())
    fail_items = (
        db.query(InspectionItem)
        .join(Inspection, InspectionItem.inspection_id == Inspection.id)
        .filter(Inspection.mine_id == mine.id, InspectionItem.status == "fail")
        .count()
    )
    last_insp = (
        db.query(Inspection)
        .filter(Inspection.mine_id == mine.id, Inspection.status == "completed")
        .order_by(Inspection.completed_date.desc())
        .first()
    )
    next_insp = (
        db.query(Inspection)
        .filter(Inspection.mine_id == mine.id, Inspection.status.in_(("scheduled", "in_progress")))
        .order_by(Inspection.scheduled_date.asc())
        .first()
    )
    contractors = db.query(Contractor).filter(Contractor.mine_id == mine.id).count()

    # Score 0–100 from weighted contributors (not random).
    score = 8
    score += min(28, overdue_req * 6)
    score += min(18, critical_v * 12 + high_v * 5)
    score += min(14, len(open_v) * 2)
    score += min(12, overdue_ca * 5 + open_ca * 1)
    score += min(10, fail_items * 1.5)
    score += min(8, env_v * 3)
    if last_insp and last_insp.completed_date and (today - last_insp.completed_date).days > 45:
        score += 8
    score = int(max(0, min(100, round(score))))

    factors = [
        {"factor": "Overdue compliance", "weight": overdue_req, "detail": f"{overdue_req} overdue requirement(s)"},
        {"factor": "Open violations", "weight": len(open_v), "detail": f"{len(open_v)} open ({critical_v} critical, {high_v} high)"},
        {"factor": "Unresolved corrective actions", "weight": open_ca, "detail": f"{open_ca} open, {overdue_ca} overdue"},
        {"factor": "Failed inspection items", "weight": fail_items, "detail": f"{fail_items} failed checklist items"},
        {"factor": "Safety findings", "weight": safety_v, "detail": f"{safety_v} open safety violations; PPE-related: {ppe}"},
        {"factor": "Environmental findings", "weight": env_v, "detail": f"{env_v} open environmental violations"},
    ]
    explanation = (
        f"{mine.name} is currently classified as {risk_level(score)} RISK because "
        f"{overdue_req} compliance requirement(s) are overdue, {len(open_v)} violation(s) remain open "
        f"({ppe} PPE-related), and {open_ca} corrective action(s) are unresolved. "
        "This is an AI-Assisted Risk Indicator for decision support, not a certified safety determination."
    )
    return {
        "risk_score": score,
        "risk_level": risk_level(score),
        "factors": factors,
        "explanation": explanation,
        "open_violations": len(open_v),
        "overdue_requirements": overdue_req,
        "open_corrective_actions": open_ca,
        "overdue_corrective_actions": overdue_ca,
        "failed_inspection_items": fail_items,
        "ppe_violations": ppe,
        "contractors": contractors,
        "last_inspection": last_insp.completed_date if last_insp else None,
        "next_inspection": next_insp.scheduled_date if next_insp else None,
    }


def recalculate_mine(db: Session, mine_id: int) -> Mine | None:
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        return None
    records = db.query(ComplianceRecord).filter(ComplianceRecord.mine_id == mine_id).all()
    total = len(records)
    completed = sum(1 for r in records if r.status == "completed")
    mine.compliance_score = round((completed / total) * 100, 1) if total else 0.0
    mine.safety_score = _category_score(db, mine_id, "safety")
    mine.environment_score = _category_score(db, mine_id, "environment")
    mine.labour_score = _category_score(db, mine_id, "labour")
    mine.production_score = _category_score(db, mine_id, "production")
    explained = explain_mine_risk(db, mine)
    mine.risk_score = explained["risk_score"]
    mine.open_violations = explained["open_violations"]
    mine.num_workers = mine.num_workers or 0
    last = explained["last_inspection"]
    if last:
        mine.last_inspection_date = datetime.combine(last, datetime.min.time()).replace(tzinfo=timezone.utc)
    db.add(mine)
    return mine


def recalculate_all(db: Session) -> None:
    for mine in db.query(Mine).all():
        recalculate_mine(db, mine.id)


def production_anomaly(db: Session, mine_id: int) -> dict | None:
    rows = (
        db.query(ProductionRecord)
        .filter(ProductionRecord.mine_id == mine_id)
        .order_by(ProductionRecord.date.desc())
        .limit(14)
        .all()
    )
    if len(rows) < 5:
        return None
    recent = rows[0]
    baseline = sum(r.actual_tonnes for r in rows[1:]) / max(1, len(rows) - 1)
    if baseline <= 0:
        return None
    deviation = ((recent.actual_tonnes - baseline) / baseline) * 100
    if deviation > -15:
        return None
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    incidents = sum(r.safety_incidents for r in rows)
    downtime = sum(r.downtime_hours for r in rows)
    return {
        "mine_id": mine_id,
        "mine_name": mine.name if mine else "",
        "label": "OPERATIONAL ANOMALY",
        "message": f"Production is {abs(round(deviation))}% below the recent 14-day baseline.",
        "deviation_pct": round(deviation, 1),
        "potential_contributing_factors": [
            f"Equipment downtime totaling {round(downtime, 1)} hours in the sample window" if downtime else "No significant downtime recorded",
            f"{incidents} reported safety incident(s) in the sample window" if incidents else "No safety incidents in the sample window",
            "Attendance and maintenance records should be reviewed by authorized personnel",
        ],
        "disclaimer": "Potential contributing factors only. Not a causal determination.",
    }

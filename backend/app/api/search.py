"""
KhanijSetu Global Search API — search across all modules.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.violation import Violation
from app.models.inspection import Inspection
from app.models.compliance import ComplianceRequirement, ComplianceRecord
from app.models.contractor import Contractor
from app.models.document import Document
from app.models.field_report import FieldReport
from app.auth.jwt_handler import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
async def global_search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Global search across all modules. Returns grouped results."""
    term = f"%{q}%"
    results = {}

    # Mines
    mines = db.query(Mine).filter(
        Mine.name.ilike(term) | Mine.code.ilike(term) | Mine.location.ilike(term) | Mine.district.ilike(term)
    ).limit(5).all()
    if mines:
        results["mines"] = [{
            "id": m.id, "name": m.name, "code": m.code,
            "location": m.location or "", "risk_score": m.risk_score,
            "link": f"/app/mines/{m.id}",
        } for m in mines]

    # Violations
    violations = db.query(Violation).filter(
        Violation.violation_code.ilike(term) | Violation.title.ilike(term) | Violation.description.ilike(term)
    ).limit(5).all()
    if violations:
        mine_map = {m.id: m.name for m in db.query(Mine).all()}
        results["violations"] = [{
            "id": v.id, "code": v.violation_code, "title": v.title,
            "mine_name": mine_map.get(v.mine_id, ""), "severity": v.severity,
            "link": f"/app/violations",
        } for v in violations]

    # Inspections
    inspections = db.query(Inspection).filter(
        Inspection.findings_summary.ilike(term) | Inspection.inspection_type.ilike(term)
    ).limit(5).all()
    if inspections:
        mine_map = mine_map if 'mine_map' in dir() else {m.id: m.name for m in db.query(Mine).all()}
        results["inspections"] = [{
            "id": i.id, "type": i.inspection_type, "status": i.status,
            "mine_name": mine_map.get(i.mine_id, ""),
            "link": f"/app/inspections",
        } for i in inspections]

    # Documents
    documents = db.query(Document).filter(
        Document.name.ilike(term) | Document.document_type.ilike(term)
    ).limit(5).all()
    if documents:
        if 'mine_map' not in dir():
            mine_map = {m.id: m.name for m in db.query(Mine).all()}
        results["documents"] = [{
            "id": d.id, "name": d.name, "type": d.document_type,
            "mine_name": mine_map.get(d.mine_id, ""),
            "link": f"/app/documents",
        } for d in documents]

    # Contractors
    contractors = db.query(Contractor).filter(
        Contractor.name.ilike(term) | Contractor.company.ilike(term)
    ).limit(5).all()
    if contractors:
        if 'mine_map' not in dir():
            mine_map = {m.id: m.name for m in db.query(Mine).all()}
        results["contractors"] = [{
            "id": c.id, "name": c.name, "company": c.company,
            "mine_name": mine_map.get(c.mine_id, ""),
            "link": f"/app/contractors",
        } for c in contractors]

    # Compliance Requirements
    requirements = db.query(ComplianceRequirement).filter(
        ComplianceRequirement.title.ilike(term) | ComplianceRequirement.description.ilike(term)
    ).limit(5).all()
    if requirements:
        results["compliance"] = [{
            "id": r.id, "title": r.title, "category": r.category,
            "link": f"/app/compliance",
        } for r in requirements]

    total = sum(len(v) for v in results.values())
    return {"query": q, "total": total, "results": results}

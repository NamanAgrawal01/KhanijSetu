from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.auth.jwt_handler import get_current_user
from app.services.scoring import explain_mine_risk, recalculate_mine, production_anomaly
from app.schemas.common import RiskResponse
from typing import Optional

router = APIRouter(prefix="/risk", tags=["Risk Analytics"])


@router.get("")
async def get_risk_overview(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get risk overview for all mines using the live scoring engine."""
    mines = db.query(Mine).all()
    result = []
    for mine in mines:
        recalculate_mine(db, mine.id)
        mine = db.query(Mine).filter(Mine.id == mine.id).first()
        risk_data = explain_mine_risk(db, mine)
        result.append({
            "mine_id": mine.id, "mine_name": mine.name,
            "risk_score": mine.risk_score,
            "risk_level": risk_data["risk_level"],
            "compliance_score": mine.compliance_score,
            "open_violations": mine.open_violations,
            "explanation": risk_data["explanation"],
            "factors": risk_data["factors"],
        })
    db.commit()
    result.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"mines": result, "total": len(result)}


@router.get("/recurring-violations")
async def recurring_patterns(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from collections import defaultdict
    from app.models.violation import Violation
    rows = db.query(Violation).all()
    buckets = defaultdict(lambda: {"count": 0, "mines": set(), "timeline": []})
    for v in rows:
        key = (v.category or "other").lower()
        if "ppe" in (v.title or "").lower() or "ppe" in (v.description or "").lower():
            key = "ppe"
        buckets[key]["count"] += 1
        buckets[key]["mines"].add(v.mine_id)
        buckets[key]["timeline"].append(v.detected_date.isoformat() if v.detected_date else "")
    mine_map = {m.id: m.name for m in db.query(Mine).all()}
    out = []
    for cat, data in sorted(buckets.items(), key=lambda x: x[1]["count"], reverse=True):
        mines = [mine_map.get(i, str(i)) for i in data["mines"]]
        out.append({
            "category": cat,
            "frequency": data["count"],
            "affected_mines": mines,
            "timeline": [t for t in data["timeline"] if t][:12],
            "ai_insight": f"{data['count']} occurrence(s) in category '{cat}' across {len(mines)} mine(s). Repeated patterns warrant targeted training and inspection focus.",
        })
    return {"patterns": out, "disclaimer": "AI-assisted pattern detection from recorded violations. Not a legal finding."}


@router.get("/{mine_id}")
async def get_mine_risk(mine_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get detailed risk analysis for a specific mine."""
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    if not mine:
        raise HTTPException(status_code=404, detail="Mine not found")
    recalculate_mine(db, mine_id)
    db.commit()
    mine = db.query(Mine).filter(Mine.id == mine_id).first()
    risk_data = explain_mine_risk(db, mine)
    anomaly = production_anomaly(db, mine_id)
    return {
        "mine_id": mine.id,
        "mine_name": mine.name,
        "risk_score": mine.risk_score,
        "risk_level": risk_data["risk_level"],
        "factors": risk_data["factors"],
        "explanation": risk_data["explanation"],
        "trend": [],
        "recommendations": [
            "Verify overdue compliance items with authorized officers.",
            "Close or evidence-submit open corrective actions.",
            "Schedule targeted inspection for highest-weight factors.",
        ],
        "disclaimer": "AI-Assisted Risk Indicator. Not a certified safety determination.",
        "production_anomaly": anomaly,
        "compliance_score": mine.compliance_score,
        "open_violations": mine.open_violations,
    }

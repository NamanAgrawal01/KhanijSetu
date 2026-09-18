from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.violation import Violation
from app.models.compliance import ComplianceRecord
from app.models.inspection import Inspection
from app.models.corrective_action import CorrectiveAction
from app.models.alert import Alert
from app.auth.jwt_handler import get_current_user
from app.ai import ai_service
from app.schemas.common import AIQueryRequest, AIQueryResponse

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/query", response_model=AIQueryResponse)
async def ai_query(
    data: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process natural-language governance query with database context."""
    # Build real database context for the AI
    mines = db.query(Mine).all()
    open_violations = db.query(Violation).filter(
        Violation.status.in_(["detected", "assigned", "in_progress"])
    ).count()
    critical_alerts = db.query(Alert).filter(
        Alert.severity == "critical", Alert.status == "active"
    ).count()
    overdue_compliance = db.query(ComplianceRecord).filter(
        ComplianceRecord.status == "overdue"
    ).count()
    pending_inspections = db.query(Inspection).filter(
        Inspection.status.in_(["scheduled", "in_progress"])
    ).count()
    pending_actions = db.query(CorrectiveAction).filter(
        CorrectiveAction.status.in_(["pending", "in_progress", "overdue"])
    ).count()

    db_context = {
        "total_mines": len(mines),
        "mines": [{
            "id": m.id, "name": m.name, "risk_score": m.risk_score,
            "compliance_score": m.compliance_score, "open_violations": m.open_violations,
            "status": m.status, "mine_type": m.mine_type,
        } for m in mines],
        "open_violations": open_violations,
        "critical_alerts": critical_alerts,
        "overdue_compliance": overdue_compliance,
        "pending_inspections": pending_inspections,
        "pending_actions": pending_actions,
        "high_risk_mines": [m.name for m in mines if m.risk_score >= 70],
    }

    # Merge user context with database context
    context = {**(data.context or {}), **db_context}
    result = await ai_service.answer_query(data.query, context)
    return AIQueryResponse(
        answer=result.get("answer", ""),
        data=result.get("data"),
        entities=result.get("entities", []),
        recommendations=result.get("recommendations", []),
        confidence=result.get("confidence", 0.70),
    )

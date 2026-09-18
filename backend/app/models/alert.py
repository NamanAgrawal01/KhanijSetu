from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=True)
    mine_name = Column(String(255))
    type = Column(String(100), nullable=False)  # compliance, safety, environmental, equipment, escalation
    severity = Column(String(50), default="warning")  # critical, high, warning, info
    title = Column(String(500), nullable=False)
    message = Column(Text)
    status = Column(String(50), default="active")  # active, acknowledged, resolved, dismissed
    escalation_level = Column(Integer, default=0)
    escalation_history = Column(Text)  # JSON string
    source = Column(String(100))  # system, ai, inspector, manager
    link = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    mine = relationship("Mine", back_populates="alerts")

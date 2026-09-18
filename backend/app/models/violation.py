from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    violation_code = Column(String(50), unique=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    category = Column(String(100), nullable=False)  # safety, environment, equipment, labour, documentation
    severity = Column(String(50), default="medium")  # low, medium, high, critical
    title = Column(String(500), nullable=False)
    description = Column(Text)
    reported_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    reported_by_name = Column(String(255))
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to_name = Column(String(255))
    detected_date = Column(Date, nullable=False)
    deadline = Column(Date, nullable=True)
    status = Column(String(50), default="detected")  # detected, assigned, in_progress, resolved, verified, closed
    resolution_notes = Column(Text)
    evidence_url = Column(String(500))
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=True)
    is_recurring = Column(Integer, default=0)
    recurrence_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    mine = relationship("Mine", back_populates="violations")
    corrective_actions = relationship("CorrectiveAction", back_populates="violation")

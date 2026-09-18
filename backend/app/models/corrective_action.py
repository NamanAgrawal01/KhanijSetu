from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id = Column(Integer, primary_key=True, index=True)
    action_code = Column(String(50), unique=True)
    violation_id = Column(Integer, ForeignKey("violations.id"), nullable=False)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_to_name = Column(String(255))
    deadline = Column(Date, nullable=False)
    priority = Column(String(50), default="medium")  # low, medium, high, critical
    status = Column(String(50), default="pending")  # pending, in_progress, overdue, submitted, verified, closed
    evidence_url = Column(String(500))
    evidence_notes = Column(Text)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by_name = Column(String(255))
    verified_date = Column(Date, nullable=True)
    verification_notes = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    violation = relationship("Violation", back_populates="corrective_actions")
    mine = relationship("Mine", back_populates="corrective_actions")

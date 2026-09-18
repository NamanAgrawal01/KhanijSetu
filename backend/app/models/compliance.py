from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class ComplianceRequirement(Base):
    __tablename__ = "compliance_requirements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    category = Column(String(100), nullable=False)  # safety, environment, production, labour, equipment, documentation
    description = Column(Text)
    frequency = Column(String(50), default="monthly")  # daily, weekly, monthly, quarterly, annual
    authority = Column(String(255))
    regulation_ref = Column(String(255))
    source_url = Column(String(500), default="")
    last_verified = Column(String(50), default="")
    is_illustrative = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    records = relationship("ComplianceRecord", back_populates="requirement")


class ComplianceRecord(Base):
    __tablename__ = "compliance_records"

    id = Column(Integer, primary_key=True, index=True)
    requirement_id = Column(Integer, ForeignKey("compliance_requirements.id"), nullable=False)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    status = Column(String(50), default="pending")  # completed, pending, due_soon, overdue
    due_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    evidence_url = Column(String(500))
    notes = Column(Text)
    responsible_officer = Column(String(255))
    risk_level = Column(String(50), default="low")  # low, medium, high, critical
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    requirement = relationship("ComplianceRequirement", back_populates="records")
    mine = relationship("Mine", back_populates="compliance_records")

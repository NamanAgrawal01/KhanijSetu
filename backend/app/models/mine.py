from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Mine(Base):
    __tablename__ = "mines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True)
    subsidiary_id = Column(Integer, ForeignKey("subsidiaries.id"), nullable=False)
    location = Column(String(255))
    district = Column(String(255))
    state = Column(String(255), default="Jharkhand")
    latitude = Column(Float, default=23.7957)
    longitude = Column(Float, default=86.4304)
    mine_type = Column(String(100), default="Underground")
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    manager_name = Column(String(255))
    capacity_mtpa = Column(Float, default=1.0)
    num_workers = Column(Integer, default=0)
    status = Column(String(50), default="operational")
    compliance_score = Column(Float, default=75.0)
    risk_score = Column(Integer, default=50)
    safety_score = Column(Float, default=70.0)
    environment_score = Column(Float, default=75.0)
    labour_score = Column(Float, default=80.0)
    production_score = Column(Float, default=70.0)
    open_violations = Column(Integer, default=0)
    last_inspection_date = Column(DateTime, nullable=True)
    data_classification = Column(String(50), default="demo_illustrative")  # official_public | demo_illustrative
    source_name = Column(String(255), default="")
    source_url = Column(String(500), default="")
    retrieved_date = Column(String(50), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    subsidiary = relationship("Subsidiary", back_populates="mines")
    compliance_records = relationship("ComplianceRecord", back_populates="mine")
    inspections = relationship("Inspection", back_populates="mine")
    violations = relationship("Violation", back_populates="mine")
    corrective_actions = relationship("CorrectiveAction", back_populates="mine")
    documents = relationship("Document", back_populates="mine")
    contractors = relationship("Contractor", back_populates="mine")
    production_records = relationship("ProductionRecord", back_populates="mine")
    field_reports = relationship("FieldReport", back_populates="mine")
    alerts = relationship("Alert", back_populates="mine")
    workers = relationship("Worker", back_populates="mine")
    attendance_records = relationship("Attendance", back_populates="mine")

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    company = Column(String(255))
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    contract_type = Column(String(100))
    contract_start = Column(Date)
    contract_end = Column(Date)
    num_workers = Column(Integer, default=0)
    safety_score = Column(Float, default=75.0)
    violation_count = Column(Integer, default=0)
    compliance_status = Column(String(50), default="compliant")  # compliant, non_compliant, expiring, expired
    performance_rating = Column(String(50), default="good")  # excellent, good, average, poor
    contact_phone = Column(String(20))
    contact_email = Column(String(255))
    status = Column(String(50), default="active")  # active, inactive, suspended
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    mine = relationship("Mine", back_populates="contractors")
    workers = relationship("Worker", back_populates="contractor")


class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True)
    name = Column(String(255), nullable=False)
    contractor_id = Column(Integer, ForeignKey("contractors.id"), nullable=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    role = Column(String(100))
    department = Column(String(100))
    is_contract = Column(Integer, default=0)
    training_status = Column(String(50), default="completed")  # completed, pending, overdue
    status = Column(String(50), default="active")  # active, inactive
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    contractor = relationship("Contractor", back_populates="workers")
    mine = relationship("Mine", back_populates="workers")
    attendance_records = relationship("Attendance", back_populates="worker")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    date = Column(Date, nullable=False)
    status = Column(String(20), default="present")  # present, absent, leave, half_day
    check_in = Column(DateTime, nullable=True)
    check_out = Column(DateTime, nullable=True)
    method = Column(String(50), default="manual")  # manual, qr, biometric
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    worker = relationship("Worker", back_populates="attendance_records")
    mine = relationship("Mine", back_populates="attendance_records")

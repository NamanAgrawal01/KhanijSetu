from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Inspection(Base):
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    inspection_type = Column(String(100), default="routine")  # routine, safety, environmental, special, follow_up
    scheduled_date = Column(Date, nullable=False)
    completed_date = Column(Date, nullable=True)
    status = Column(String(50), default="scheduled")  # scheduled, in_progress, completed, overdue, cancelled
    priority = Column(String(50), default="normal")  # low, normal, high, urgent
    overall_rating = Column(String(50))  # satisfactory, needs_improvement, unsatisfactory, critical
    findings_summary = Column(Text)
    recommendations = Column(Text)
    gps_latitude = Column(Float, nullable=True)
    gps_longitude = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    mine = relationship("Mine", back_populates="inspections")
    inspector = relationship("User", back_populates="inspections", foreign_keys=[inspector_id])
    items = relationship("InspectionItem", back_populates="inspection", cascade="all, delete-orphan")


class InspectionItem(Base):
    __tablename__ = "inspection_items"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, ForeignKey("inspections.id"), nullable=False)
    category = Column(String(100), nullable=False)
    item_name = Column(String(500), nullable=False)
    status = Column(String(20), default="pending")  # pass, fail, na, pending
    severity = Column(String(50), nullable=True)  # low, medium, high, critical
    notes = Column(Text)
    photo_url = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    inspection = relationship("Inspection", back_populates="items")

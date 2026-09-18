from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class FieldReport(Base):
    __tablename__ = "field_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(50), unique=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reporter_name = Column(String(255))
    observation_type = Column(String(100), nullable=False)  # safety, environment, equipment, general
    severity = Column(String(50), default="medium")  # low, medium, high, critical
    title = Column(String(500))
    description = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    location_label = Column(String(255))
    photo_url = Column(String(500))
    status = Column(String(50), default="submitted")  # submitted, reviewed, acknowledged, resolved
    sync_status = Column(String(50), default="synced")  # pending, synced
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    mine = relationship("Mine", back_populates="field_reports")
    reporter = relationship("User", back_populates="field_reports")

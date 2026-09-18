from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class ProductionRecord(Base):
    __tablename__ = "production_records"

    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    date = Column(Date, nullable=False)
    shift = Column(String(20), default="day")  # day, night, general
    target_tonnes = Column(Float, default=0)
    actual_tonnes = Column(Float, default=0)
    overburden_removed = Column(Float, default=0)
    equipment_hours = Column(Float, default=0)
    downtime_hours = Column(Float, default=0)
    downtime_reason = Column(String(255))
    safety_incidents = Column(Integer, default=0)
    notes = Column(Text)
    recorded_by = Column(String(255))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    mine = relationship("Mine", back_populates="production_records")

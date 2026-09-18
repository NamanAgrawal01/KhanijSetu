from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user_name = Column(String(255))
    user_role = Column(String(50))
    action = Column(String(100), nullable=False)  # created, updated, deleted, viewed, uploaded, verified, login, etc
    module = Column(String(100), nullable=False)
    entity = Column(String(100))
    entity_id = Column(Integer, nullable=True)
    details = Column(Text)
    ip_address = Column(String(50))
    status = Column(String(50), default="success")  # success, failed, error
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

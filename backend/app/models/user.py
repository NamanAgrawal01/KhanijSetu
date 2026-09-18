from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    INSPECTOR = "inspector"
    MINE_OPERATOR = "mine_operator"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.INSPECTOR.value)
    designation = Column(String(255), default="")
    phone = Column(String(20), default="")
    subsidiary_id = Column(Integer, ForeignKey("subsidiaries.id"), nullable=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    subsidiary = relationship("Subsidiary", back_populates="users")
    inspections = relationship("Inspection", back_populates="inspector", foreign_keys="Inspection.inspector_id")
    field_reports = relationship("FieldReport", back_populates="reporter")
    notifications = relationship("Notification", back_populates="user")


class Subsidiary(Base):
    __tablename__ = "subsidiaries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True)
    region = Column(String(255))
    head_name = Column(String(255))
    head_email = Column(String(255))
    address = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    mines = relationship("Mine", back_populates="subsidiary")
    users = relationship("User", back_populates="subsidiary")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    status = Column(String(50), default="unread")
    link = Column(String(500))
    type = Column(String(50), default="info")
    severity = Column(String(50), default="info")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="notifications")

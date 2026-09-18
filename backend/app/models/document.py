from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False)
    document_type = Column(String(100))  # inspection_report, safety_certificate, environmental_clearance, compliance_report, etc
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    file_path = Column(String(500))
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100))
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    uploaded_by_name = Column(String(255))
    processing_status = Column(String(50), default="pending")  # uploaded, processing, verified, rejected, expired, completed, failed
    category = Column(String(100), default="regulatory")
    expiry_date = Column(String(50), default="")
    version = Column(Integer, default=1)
    verification_status = Column(String(50), default="uploaded")
    ocr_text = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    mine = relationship("Mine", back_populates="documents")
    analysis = relationship("DocumentAnalysis", back_populates="document", uselist=False, cascade="all, delete-orphan")


class DocumentAnalysis(Base):
    __tablename__ = "document_analysis"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, unique=True)
    summary = Column(Text)
    document_category = Column(String(100))
    extracted_mine = Column(String(255))
    extracted_date = Column(String(100))
    extracted_inspector = Column(String(255))
    extracted_expiry = Column(String(100))
    key_findings = Column(Text)  # JSON string
    issues_high = Column(Integer, default=0)
    issues_medium = Column(Integer, default=0)
    issues_low = Column(Integer, default=0)
    issues_details = Column(Text)  # JSON string
    recommendations = Column(Text)  # JSON string
    compliance_status = Column(String(50))
    risk_indicators = Column(Text)  # JSON string
    confidence_score = Column(Float, default=0.85)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="analysis")

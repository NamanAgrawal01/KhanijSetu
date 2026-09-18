from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    id: int
    name: str
    document_type: Optional[str] = None
    mine_id: int
    processing_status: str
    created_at: Optional[datetime] = None
    class Config:
        from_attributes = True

class DocumentAnalysisResponse(BaseModel):
    id: int
    document_id: int
    summary: Optional[str] = None
    document_category: Optional[str] = None
    extracted_mine: Optional[str] = None
    extracted_date: Optional[str] = None
    extracted_inspector: Optional[str] = None
    extracted_expiry: Optional[str] = None
    key_findings: Optional[Any] = None
    issues_high: int = 0
    issues_medium: int = 0
    issues_low: int = 0
    issues_details: Optional[Any] = None
    recommendations: Optional[Any] = None
    compliance_status: Optional[str] = None
    risk_indicators: Optional[Any] = None
    confidence_score: float = 0.85
    class Config:
        from_attributes = True

class DocumentResponse(BaseModel):
    id: int
    name: str
    document_type: Optional[str] = None
    mine_id: int
    mine_name: Optional[str] = None
    file_path: Optional[str] = None
    file_size: int = 0
    uploaded_by_name: Optional[str] = None
    processing_status: str
    created_at: Optional[datetime] = None
    analysis: Optional[DocumentAnalysisResponse] = None
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]
    total: int

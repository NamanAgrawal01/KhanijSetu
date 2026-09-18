import os
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.mine import Mine
from app.models.document import Document, DocumentAnalysis
from app.auth.jwt_handler import get_current_user
from app.schemas.document import DocumentResponse, DocumentAnalysisResponse, DocumentListResponse
from app.ai import ai_service
from app.ai.ocr_service import extract_text_from_file
from app.config import settings
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/documents", tags=["Documents"])

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".doc", ".tiff"}


@router.get("", response_model=DocumentListResponse)
async def get_documents(
    mine_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0, limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Document)
    if current_user.role == "mine_operator" and current_user.mine_id:
        query = query.filter(Document.mine_id == current_user.mine_id)
    if mine_id:
        query = query.filter(Document.mine_id == mine_id)
    if status:
        query = query.filter(Document.processing_status == status)

    total = query.count()
    docs = query.order_by(Document.created_at.desc()).offset(skip).limit(limit).all()

    result = []
    for doc in docs:
        mine = db.query(Mine).filter(Mine.id == doc.mine_id).first()
        analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.document_id == doc.id).first()
        analysis_resp = None
        if analysis:
            analysis_resp = DocumentAnalysisResponse(
                id=analysis.id, document_id=analysis.document_id,
                summary=analysis.summary, document_category=analysis.document_category,
                extracted_mine=analysis.extracted_mine, extracted_date=analysis.extracted_date,
                extracted_inspector=analysis.extracted_inspector,
                extracted_expiry=analysis.extracted_expiry,
                key_findings=json.loads(analysis.key_findings) if analysis.key_findings else [],
                issues_high=analysis.issues_high, issues_medium=analysis.issues_medium,
                issues_low=analysis.issues_low,
                issues_details=json.loads(analysis.issues_details) if analysis.issues_details else [],
                recommendations=json.loads(analysis.recommendations) if analysis.recommendations else [],
                compliance_status=analysis.compliance_status,
                risk_indicators=json.loads(analysis.risk_indicators) if analysis.risk_indicators else [],
                confidence_score=analysis.confidence_score,
            )
        result.append(DocumentResponse(
            id=doc.id, name=doc.name, document_type=doc.document_type,
            mine_id=doc.mine_id, mine_name=mine.name if mine else "",
            file_path=doc.file_path, file_size=doc.file_size,
            uploaded_by_name=doc.uploaded_by_name,
            processing_status=doc.processing_status,
            created_at=doc.created_at, analysis=analysis_resp,
        ))

    return DocumentListResponse(documents=result, total=total)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    mine_id: int = Form(...),
    document_type: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload and process a document."""
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not allowed. Allowed: {ALLOWED_EXTENSIONS}")

    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum 10MB allowed.")

    # Save file
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{Document.__tablename__}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    mine = db.query(Mine).filter(Mine.id == mine_id).first()

    doc = Document(
        name=file.filename,
        document_type=document_type or "general",
        mine_id=mine_id,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type,
        uploaded_by=current_user.id,
        uploaded_by_name=current_user.name,
        processing_status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # OCR / text extraction
    try:
        text = extract_text_from_file(file_path)
        doc.ocr_text = text
    except Exception:
        text = ""

    # AI analysis
    try:
        analysis_result = await ai_service.analyze_document(
            text, file.filename, mine.name if mine else ""
        )
        da = DocumentAnalysis(
            document_id=doc.id,
            summary=analysis_result.get("summary", ""),
            document_category=analysis_result.get("document_category", ""),
            extracted_mine=analysis_result.get("extracted_mine", ""),
            extracted_date=analysis_result.get("extracted_date", ""),
            extracted_inspector=analysis_result.get("extracted_inspector", ""),
            extracted_expiry=analysis_result.get("extracted_expiry", ""),
            key_findings=json.dumps(analysis_result.get("key_findings", [])),
            issues_high=analysis_result.get("issues_high", 0),
            issues_medium=analysis_result.get("issues_medium", 0),
            issues_low=analysis_result.get("issues_low", 0),
            issues_details=json.dumps(analysis_result.get("issues_details", [])),
            recommendations=json.dumps(analysis_result.get("recommendations", [])),
            compliance_status=analysis_result.get("compliance_status", ""),
            risk_indicators=json.dumps(analysis_result.get("risk_indicators", [])),
            confidence_score=analysis_result.get("confidence_score", 0.85),
        )
        db.add(da)
        doc.processing_status = "completed"
    except Exception as e:
        doc.processing_status = "failed"

    db.commit()
    db.refresh(doc)

    analysis = db.query(DocumentAnalysis).filter(DocumentAnalysis.document_id == doc.id).first()
    analysis_resp = None
    if analysis:
        analysis_resp = DocumentAnalysisResponse(
            id=analysis.id, document_id=analysis.document_id,
            summary=analysis.summary, document_category=analysis.document_category,
            extracted_mine=analysis.extracted_mine, extracted_date=analysis.extracted_date,
            extracted_inspector=analysis.extracted_inspector,
            extracted_expiry=analysis.extracted_expiry,
            key_findings=json.loads(analysis.key_findings) if analysis.key_findings else [],
            issues_high=analysis.issues_high, issues_medium=analysis.issues_medium,
            issues_low=analysis.issues_low,
            issues_details=json.loads(analysis.issues_details) if analysis.issues_details else [],
            recommendations=json.loads(analysis.recommendations) if analysis.recommendations else [],
            compliance_status=analysis.compliance_status,
            risk_indicators=json.loads(analysis.risk_indicators) if analysis.risk_indicators else [],
            confidence_score=analysis.confidence_score,
        )

    return DocumentResponse(
        id=doc.id, name=doc.name, document_type=doc.document_type,
        mine_id=doc.mine_id, mine_name=mine.name if mine else "",
        file_path=doc.file_path, file_size=doc.file_size,
        uploaded_by_name=doc.uploaded_by_name,
        processing_status=doc.processing_status,
        created_at=doc.created_at, analysis=analysis_resp,
    )


@router.post("/analyze/{document_id}")
async def analyze_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Re-analyze an existing document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    text = doc.ocr_text or ""
    mine = db.query(Mine).filter(Mine.id == doc.mine_id).first()
    analysis_result = await ai_service.analyze_document(text, doc.name, mine.name if mine else "")

    # Update or create analysis
    existing = db.query(DocumentAnalysis).filter(DocumentAnalysis.document_id == doc.id).first()
    if existing:
        existing.summary = analysis_result.get("summary", "")
        existing.issues_high = analysis_result.get("issues_high", 0)
        existing.issues_medium = analysis_result.get("issues_medium", 0)
        existing.issues_low = analysis_result.get("issues_low", 0)
        existing.issues_details = json.dumps(analysis_result.get("issues_details", []))
        existing.recommendations = json.dumps(analysis_result.get("recommendations", []))
    else:
        da = DocumentAnalysis(
            document_id=doc.id,
            summary=analysis_result.get("summary", ""),
            document_category=analysis_result.get("document_category", ""),
            issues_high=analysis_result.get("issues_high", 0),
            issues_medium=analysis_result.get("issues_medium", 0),
            issues_low=analysis_result.get("issues_low", 0),
            issues_details=json.dumps(analysis_result.get("issues_details", [])),
            recommendations=json.dumps(analysis_result.get("recommendations", [])),
            compliance_status=analysis_result.get("compliance_status", ""),
            confidence_score=analysis_result.get("confidence_score", 0.85),
        )
        db.add(da)

    doc.processing_status = "completed"
    db.commit()
    return {"status": "success", "analysis": analysis_result}


class AnalyzeBody(BaseModel):
    document_id: int


@router.post("/analyze")
async def analyze_document_body(data: AnalyzeBody, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await analyze_document(data.document_id, db, current_user)

"""
KhanijSetu OCR Service

Attempts Tesseract OCR first, falls back to PyMuPDF text extraction,
then provides demo text if both are unavailable.
"""
import os
from typing import Optional
from app.config import settings


def extract_text_from_file(file_path: str) -> str:
    """Extract text from a file using available methods."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text = _extract_from_pdf(file_path)
        if text and text.strip():
            return text

    if ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        text = _extract_from_image(file_path)
        if text and text.strip():
            return text

    return _get_demo_text(file_path)


def _extract_from_pdf(file_path: str) -> Optional[str]:
    """Extract text from PDF using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text if text.strip() else None
    except Exception:
        return None


def _extract_from_image(file_path: str) -> Optional[str]:
    """Extract text from image using Tesseract OCR."""
    try:
        import pytesseract
        from PIL import Image
        if settings.TESSERACT_PATH:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text if text.strip() else None
    except Exception:
        return None


def _get_demo_text(file_path: str) -> str:
    """Return realistic demo text for demonstration purposes."""
    filename = os.path.basename(file_path).lower()

    if "inspection" in filename or "safety" in filename:
        return """
MINES SAFETY INSPECTION REPORT
Directorate General of Mines Safety (DGMS)

Mine: Rajmahal Coal Mine
Subsidiary: Eastern Coalfields Limited (ECL)
Inspection Date: 15 August 2026
Inspector: Shri R.K. Sharma, Inspector of Mines

FINDINGS:

1. SAFETY EQUIPMENT
- Fire extinguishers in Section B found expired (Last serviced: Jan 2026)
- Emergency exit signage in Shaft 3 not illuminated
- First aid kits in underground sections incomplete

2. PPE COMPLIANCE
- 12 out of 45 workers observed without proper PPE in active mining zone
- Safety helmets worn by all workers but 3 helmets damaged
- Respiratory protection not used in dusty Section C

3. VENTILATION
- Ventilation system operating within acceptable parameters
- CO2 levels within permissible limits
- Methane detection systems functional

4. STRUCTURAL INTEGRITY
- Roof support in Gallery 7 needs reinforcement
- Water seepage observed in lower level access tunnel
- Ground subsidence monitoring readings require review

5. DOCUMENTATION
- Safety register up to date
- Emergency evacuation plan last updated March 2026 (overdue for review)
- Fire safety certificate expires 30 September 2026

OVERALL ASSESSMENT: NEEDS IMPROVEMENT
Corrective actions required within 30 days.

Signed: R.K. Sharma
Inspector of Mines, DGMS
"""

    if "environment" in filename:
        return """
ENVIRONMENTAL MONITORING REPORT
Mine: Rajmahal Coal Mine
Period: Q2 2026 (April - June)

AIR QUALITY:
- PM10 levels: 142 µg/m³ (Limit: 150 µg/m³) - Within limits
- PM2.5 levels: 68 µg/m³ (Limit: 60 µg/m³) - EXCEEDS LIMIT
- SO2 levels: 32 µg/m³ (Limit: 80 µg/m³) - Within limits
- NOx levels: 45 µg/m³ (Limit: 80 µg/m³) - Within limits

WATER QUALITY:
- Mine water discharge pH: 6.8 (Limit: 6.0-8.5) - Within limits
- TSS in discharge: 120 mg/L (Limit: 100 mg/L) - EXCEEDS LIMIT
- BOD: 15 mg/L (Limit: 30 mg/L) - Within limits

NOISE LEVELS:
- Day: 72 dB (Limit: 75 dB) - Within limits
- Night: 58 dB (Limit: 70 dB) - Within limits

OBSERVATIONS:
- PM2.5 and TSS levels exceed prescribed limits
- Dust suppression system needs maintenance in Section A
- Water treatment plant operating at reduced capacity

STATUS: NON-COMPLIANT (2 parameters exceeding limits)
"""

    return """
COMPLIANCE DOCUMENT
Mine: Rajmahal Coal Mine
Document Type: General Compliance Report
Date: September 2026

This document contains compliance-related information for the coal mining operation.
Regular monitoring of safety, environmental, and operational parameters is ongoing.

Key observations:
- Safety inspections are being conducted as per schedule
- Some compliance requirements need immediate attention
- Worker training programs are in progress
- Equipment maintenance logs require updating
- Fire safety certification is approaching expiry

Overall compliance status: Under Review
Next assessment date: October 2026
"""

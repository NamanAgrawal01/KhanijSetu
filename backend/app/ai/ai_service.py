"""
KhanijSetu AI Service Layer

Provides an abstracted AI interface. Attempts external AI API first,
falls back to rule-based demo AI when no API is configured.
"""
import json
import httpx
from typing import Optional, Any
from app.config import settings
from app.ai.fallback_ai import FallbackAI

fallback = FallbackAI()


async def analyze_document(text: str, filename: str = "", mine_name: str = "") -> dict:
    """Analyze a document using AI or fallback logic."""
    if settings.ai_available:
        try:
            return await _call_external_ai("analyze_document", {
                "text": text, "filename": filename, "mine_name": mine_name
            })
        except Exception:
            pass
    return fallback.analyze_document(text, filename, mine_name)


async def explain_risk(mine_data: dict) -> dict:
    """Generate explainable risk analysis for a mine."""
    if settings.ai_available:
        try:
            return await _call_external_ai("explain_risk", mine_data)
        except Exception:
            pass
    return fallback.explain_risk(mine_data)


async def detect_anomalies(data: dict) -> dict:
    """Detect operational anomalies in production/safety data."""
    if settings.ai_available:
        try:
            return await _call_external_ai("detect_anomalies", data)
        except Exception:
            pass
    return fallback.detect_anomalies(data)


async def answer_query(query: str, context: dict = None) -> dict:
    """Answer a natural-language governance query."""
    if settings.ai_available:
        try:
            return await _call_external_ai("query", {"query": query, "context": context})
        except Exception:
            pass
    return fallback.answer_query(query, context)


async def suggest_corrective_actions(violation_data: dict) -> list[str]:
    """Suggest corrective actions for a violation."""
    if settings.ai_available:
        try:
            result = await _call_external_ai("suggest_actions", violation_data)
            return result.get("suggestions", [])
        except Exception:
            pass
    return fallback.suggest_corrective_actions(violation_data)


async def summarize_compliance(records: list[dict]) -> str:
    """Summarize compliance status."""
    if settings.ai_available:
        try:
            result = await _call_external_ai("summarize", {"records": records})
            return result.get("summary", "")
        except Exception:
            pass
    return fallback.summarize_compliance(records)


async def _call_external_ai(endpoint: str, data: dict) -> dict:
    """Call external AI API."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{settings.AI_API_URL}/{endpoint}",
            json=data,
            headers={"Authorization": f"Bearer {settings.AI_API_KEY}"}
        )
        response.raise_for_status()
        return response.json()

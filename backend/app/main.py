import os
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import init_db
from app.api import (
    auth, dashboard, mines, compliance, inspections, violations,
    corrective_actions, documents, risk, field_reports, contractors,
    production, alerts, reports, ai_assistant, audit, export, search,
    users, notifications, workforce, import_data,
    settings as settings_api,
)

app = FastAPI(
    title="KhanijSetu API",
    description="AI-Powered Smart Governance & Compliance Platform for Coal Mines",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS — in production allow all origins (Railway frontend URL set via env var)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API routes
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(mines.router, prefix="/api")
app.include_router(compliance.router, prefix="/api")
app.include_router(inspections.router, prefix="/api")
app.include_router(violations.router, prefix="/api")
app.include_router(corrective_actions.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(risk.router, prefix="/api")
app.include_router(field_reports.router, prefix="/api")
app.include_router(contractors.router, prefix="/api")
app.include_router(production.router, prefix="/api")
app.include_router(alerts.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(ai_assistant.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(export.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(workforce.router, prefix="/api")
app.include_router(import_data.router, prefix="/api")
app.include_router(settings_api.router, prefix="/api")

# Static files for uploads
upload_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/", include_in_schema=False)
async def root():
    """Root redirect → API docs."""
    return RedirectResponse(url="/api/docs")


@app.get("/api/health")
async def health_check():
    """Health check that verifies database connectivity."""
    db_status = "connected"
    db_type = "sqlite"
    try:
        from app.database import SessionLocal
        db = SessionLocal()
        db.execute(__import__('sqlalchemy').text("SELECT 1"))
        db.close()
        if "postgresql" in settings.DATABASE_URL:
            db_type = "postgresql"
        elif "mysql" in settings.DATABASE_URL:
            db_type = "mysql"
    except Exception:
        db_status = "error"
    return {
        "status": "operational" if db_status == "connected" else "degraded",
        "service": "KhanijSetu API",
        "version": "1.0.0",
        "database": db_type,
        "db_status": db_status,
        "environment": settings.ENVIRONMENT,
    }


@app.post("/api/seed")
async def seed_database(secret: str = ""):
    """One-time seed endpoint — populates database with demo data."""
    expected = os.environ.get("SEED_SECRET", "khanijsetu-seed-2026")
    if secret != expected:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Invalid seed secret")
    try:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
        from seed_data import seed
        seed()
        return {"status": "success", "message": "Database seeded with demo data"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

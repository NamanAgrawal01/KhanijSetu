# KhanijSetu — AI-Enabled Smart Governance & Compliance Monitoring for Coal Mines

An integrated digital governance platform for compliance monitoring, safety intelligence, field operations, and risk management across coal mining operations in India.

## Architecture

```
Frontend (React 19 + Vite + TypeScript + TailwindCSS 4)
    │
    ▼ HTTPS / API calls
Backend (FastAPI + SQLAlchemy + Pydantic)
    │
    ▼
Database (SQLite dev / PostgreSQL production)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite 8, TypeScript, TailwindCSS 4, Recharts, Leaflet |
| Backend | FastAPI, SQLAlchemy, Pydantic, python-jose (JWT), bcrypt |
| Database | SQLite (development), PostgreSQL/MySQL (production-ready) |
| Migrations | Alembic |
| Auth | JWT tokens with bcrypt password hashing |

## Roles

| Role | Access |
|------|--------|
| **Admin** | Full system management |
| **Inspector** | Inspections, violations, compliance recording |
| **Mine Operator** | Manage assigned mine operations |
| **Analyst** | Analytics, reports, read-only across modules |
| **Viewer** | Read-only access to authorized data |

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # Edit with your settings
python seed_data.py          # Seed database
python -m uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`. API docs at `/api/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

### Quick Access Accounts (Development)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@khanijsetu.gov.in | demo123 |
| Mine Operator | operator@khanijsetu.gov.in | demo123 |
| Inspector | inspector@khanijsetu.gov.in | demo123 |
| Analyst | analyst@khanijsetu.gov.in | demo123 |
| Viewer | viewer@khanijsetu.gov.in | demo123 |

## Environment Variables

See `backend/.env.example` for all required variables.

**Critical for production:**
- `SECRET_KEY` — JWT signing secret (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- `DATABASE_URL` — Production database connection string
- `ENVIRONMENT` — Set to `production`
- `CORS_ORIGINS` — Production frontend URL only

## Database

### Development
Uses SQLite (`khanijsetu.db`) — zero configuration.

### Production
Set `DATABASE_URL` to PostgreSQL/MySQL. The codebase uses SQLAlchemy, so switching is seamless:
```
DATABASE_URL=postgresql://user:password@host:5432/khanijsetu
```

### Migrations
```bash
cd backend
python -m alembic upgrade head        # Apply migrations
python -m alembic revision --autogenerate -m "description"  # Create new
```

## API Modules

| Module | Endpoint | Description |
|--------|----------|-------------|
| Auth | `/api/auth/*` | Login, register, demo-login |
| Dashboard | `/api/dashboard/*` | KPIs, charts (all from DB) |
| Mines | `/api/mines/*` | CRUD, search, filter, sort |
| Compliance | `/api/compliance/*` | Records, requirements |
| Inspections | `/api/inspections/*` | Create, submit, checklist |
| Violations | `/api/violations/*` | Track, resolve |
| Export | `/api/export/*` | CSV/XLSX for all modules |
| Import | `/api/import/*` | CSV/Excel with validation |
| Audit | `/api/audit/*` | Full audit trail |
| Health | `/api/health` | System status + DB check |

## Import / Export

### Import
- Formats: CSV, XLSX
- Flow: Upload → Validate → Preview → Confirm → Database insertion
- Security: File size limit (10MB), extension whitelist, CSV injection protection

### Export
- Formats: CSV, XLSX
- Respects current filters and user permissions
- Mine operators only export their own mine data

## Data Classification

All seed data is **SYNTHETIC / ILLUSTRATIVE**, based on publicly known Coal India Limited subsidiary structures. It is clearly labelled and NOT official government data.

Verified data can be imported through the import system and will carry appropriate source citations.

## Security

- JWT authentication with bcrypt password hashing
- RBAC enforced on all API endpoints (backend, not just frontend)
- CORS restricted to configured origins
- File upload validation (size, extension)
- CSV injection protection on imports
- Audit logging on all mutations
- No secrets in frontend code
- Environment-based configuration

## Deployment

1. Set up production database (PostgreSQL recommended)
2. Configure `backend/.env` with production values
3. Run `alembic upgrade head` for migrations
4. Run `seed_data.py` for initial data (optional)
5. Deploy backend with `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Build frontend: `cd frontend && npm run build`
7. Deploy `frontend/dist/` to static hosting
8. Configure CORS, SSL, and domain

## License

Smart India Hackathon 2024 project.

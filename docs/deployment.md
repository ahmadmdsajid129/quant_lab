# QuantLab Deployment & Operational Guide

**Document Version:** 1.0.0  
**Status:** Approved for Implementation  
**Classification:** DevOps & Systems Administration  

---

## 1. Runtime Modes & Prerequisites

QuantLab supports two primary operating environments:
1. **Native Local Development (Zero Docker Requirement)**:
   - Optimized for Windows PowerShell and macOS/Linux developers.
   - Requirements: Python 3.11+ (Anaconda or standard Python), Node.js v20+ / v26+, npm 10+.
   - Database: Embedded SQLite (`quantlab.db`) with zero external service requirements.
   - Time Series: Local filesystem Parquet storage (`./data/parquet/`).
2. **Containerized Production (Docker & Docker Compose)**:
   - Next.js frontend container, FastAPI backend container, PostgreSQL database container.

---

## 2. Native Local Startup (Quickstart)

### Step 1: Backend Setup
```bash
# From workspace root:
cd backend

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run database migrations
python -m alembic upgrade head

# Start backend development server (Port 8000)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Frontend Setup
```bash
# In a separate terminal, from workspace root:
cd frontend

# Install dependencies
npm install

# Start Next.js development server (Port 3000)
npm run dev
```

The application workstation will be accessible at `http://localhost:3000`. Backend API documentation (Swagger/OpenAPI) is available at `http://localhost:8000/docs`.

---

## 3. Environment Variables Specification

The root and backend directories include `.env.example` templates with safe defaults:

```ini
# Application Core
ENVIRONMENT=development
LOG_LEVEL=INFO
SECRET_KEY=quantlab-insecure-dev-key-change-in-production-1234567890
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
DATABASE_URL=sqlite:///./quantlab.db
# For PostgreSQL: postgresql+psycopg2://quant:password@localhost:5432/quantlab

# Storage & Parquet
PARQUET_STORAGE_PATH=./data/parquet
SAMPLE_DATA_PATH=./data/sample

# External Providers (Optional)
ALPHA_VANTAGE_API_KEY=
TIINGO_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# Execution Limits
MAX_PARALLEL_BACKTESTS=4
JOB_TIMEOUT_SECONDS=600
```

---

## 4. Docker Compose Setup (Production / Staging)

When Docker is available:
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: quant
      POSTGRES_PASSWORD: quantpassword
      POSTGRES_DB: quantlab
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql+psycopg2://quant:quantpassword@db:5432/quantlab
      - PARQUET_STORAGE_PATH=/app/data/parquet
    volumes:
      - parquet_data:/app/data/parquet
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend

volumes:
  pgdata:
  parquet_data:
```

---

## 5. Health Checks & Observability

- **API Health Endpoint**: `GET /api/v1/health`
  - Returns: `{ "status": "healthy", "database": "connected", "workers_active": 2, "timestamp": "2026-10-13T19:50:00Z" }`
- **Background Worker Status**: `GET /api/v1/jobs/status`
  - Returns queued, running, and completed job telemetry.

from datetime import datetime, timezone
from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health():
    """Health check endpoint providing service telemetry."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected",
        "storage": {
            "parquet_path": settings.PARQUET_STORAGE_PATH,
            "sample_path": settings.SAMPLE_DATA_PATH
        }
    }

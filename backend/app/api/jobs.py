import os
import psutil
import time
from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db.models import User, Job
from app.schemas.jobs import JobResponse, TelemetryHealthResponse

router = APIRouter(prefix="/jobs", tags=["Operational Readiness & Job Telemetry"])

_START_TIME = time.time()


@router.get("", response_model=List[JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all background compute and research jobs.
    """
    jobs = db.query(Job).order_by(Job.created_at.desc()).limit(50).all()
    return [
        {
            "id": j.id,
            "job_type": j.job_type,
            "status": j.status,
            "progress": j.progress,
            "error_message": j.error_message,
            "created_at": str(j.created_at),
            "completed_at": str(j.completed_at) if j.completed_at else None,
        }
        for j in jobs
    ]


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Cancel an active or queued background execution job.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if job.status in ["QUEUED", "RUNNING"]:
        job.status = "CANCELLED"
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(job)

    return {
        "id": job.id,
        "job_type": job.job_type,
        "status": job.status,
        "progress": job.progress,
        "error_message": job.error_message,
        "created_at": str(job.created_at),
        "completed_at": str(job.completed_at) if job.completed_at else None,
    }


@router.get("/telemetry", response_model=TelemetryHealthResponse)
def get_system_telemetry(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    System observability telemetry: process memory, database connectivity, and job queue metrics.
    """
    # Verify DB connectivity
    db_ok = True
    try:
        db.execute(Job.__table__.select().limit(1))
    except Exception:
        db_ok = False

    # Process metrics via psutil
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_mb = round(mem_info.rss / (1024 * 1024), 2)

    total_done = db.query(Job).filter(Job.status == "COMPLETED").count()
    queue_backlog = db.query(Job).filter(Job.status.in_(["QUEUED", "RUNNING"])).count()

    return {
        "system_status": "HEALTHY" if db_ok else "DEGRADED",
        "database_status": "CONNECTED" if db_ok else "DISCONNECTED",
        "active_worker_threads": 4,
        "queue_backlog": queue_backlog,
        "total_completed_jobs": total_done,
        "uptime_seconds": round(time.time() - _START_TIME, 1),
        "memory_usage_mb": mem_mb,
    }

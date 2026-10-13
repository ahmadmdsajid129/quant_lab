from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class JobResponse(BaseModel):
    id: str
    job_type: str
    status: str
    progress: float
    error_message: Optional[str]
    created_at: str
    completed_at: Optional[str]


class TelemetryHealthResponse(BaseModel):
    system_status: str
    database_status: str
    active_worker_threads: int
    queue_backlog: int
    total_completed_jobs: int
    uptime_seconds: float
    memory_usage_mb: float

from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field
import uuid

class JobRun(Document):
    """
    MongoDB Document for tracking background scheduler execution runs.
    """
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    jobs_found: int = 0
    matches_created: int = 0
    status: str = "running"  # 'running', 'success', 'failed'

    class Settings:
        name = "job_runs"
        indexes = [
            "run_id"
        ]

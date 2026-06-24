from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class JobRunResponse(BaseModel):
    """
    Response schema for JobRun status.
    """
    id: str
    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    jobs_found: int
    matches_created: int
    status: str

    model_config = ConfigDict(from_attributes=True)

class AgentStatusResponse(BaseModel):
    """
    Response schema for the background scheduler agent status.
    """
    scheduler_running: bool
    next_run_time: Optional[datetime] = None
    last_run: Optional[JobRunResponse] = None

class RunNowResponse(BaseModel):
    """
    Response schema for manually triggering a run.
    """
    message: str
    run_id: str
    status: str

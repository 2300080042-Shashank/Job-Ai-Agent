from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    """
    Schema for validating input when creating a job.
    """
    company: str
    role: str
    location: Optional[str] = None
    salary: Optional[str] = None
    deadline: Optional[str] = None
    apply_link: Optional[str] = None
    source: str
    job_description: Optional[str] = None

class JobResponse(BaseModel):
    """
    Schema for responding with job details.
    """
    id: str
    company: str
    role: str
    location: Optional[str] = None
    salary: Optional[str] = None
    deadline: Optional[str] = None
    apply_link: Optional[str] = None
    source: str
    job_description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

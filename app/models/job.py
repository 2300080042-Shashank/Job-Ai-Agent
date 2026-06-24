from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import Field

class Job(Document):
    """
    MongoDB Document for discovered job listings.
    """
    company: str
    role: str
    location: Optional[str] = None
    salary: Optional[str] = None
    deadline: Optional[str] = None
    apply_link: Optional[str] = None
    source: str  # e.g., 'wellfound', 'internshala', 'unstop'
    job_description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "jobs"

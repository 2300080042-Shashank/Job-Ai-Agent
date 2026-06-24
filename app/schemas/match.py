from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime
from app.schemas.job import JobResponse

class MatchResponse(BaseModel):
    """
    Schema representing match details between a resume and a job, 
    including nested details about the matched job.
    """
    id: str
    resume_id: str
    job_id: str
    skill_match_score: float
    keyword_match_score: float
    overall_match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    created_at: datetime
    job: JobResponse

    model_config = ConfigDict(from_attributes=True)

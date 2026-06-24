from datetime import datetime
from typing import List
from beanie import Document, PydanticObjectId
from pydantic import Field

class Match(Document):
    """
    MongoDB Document representing a match between a Resume and a Job.
    """
    resume_id: PydanticObjectId
    job_id: PydanticObjectId
    skill_match_score: float
    keyword_match_score: float
    overall_match_score: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "matches"
        # Optional: Add index for queries by resume_id
        indexes = [
            "resume_id"
        ]

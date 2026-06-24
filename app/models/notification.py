from datetime import datetime
from beanie import Document, PydanticObjectId
from pydantic import Field

class Notification(Document):
    """
    MongoDB Document representing a sent or logged notification.
    """
    job_id: PydanticObjectId
    match_id: PydanticObjectId
    resume_id: PydanticObjectId
    notification_type: str  # e.g., 'telegram'
    recipient: str  # e.g., chat_id
    message: str
    match_score: float
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str  # 'sent', 'failed'

    class Settings:
        name = "notifications"
        indexes = [
            "resume_id",
            "job_id",
            # Combined index to prevent duplicate notifications
            [("resume_id", 1), ("job_id", 1)]
        ]

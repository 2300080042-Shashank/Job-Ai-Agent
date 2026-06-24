from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    """
    Response schema for structured notification details.
    """
    id: str
    job_id: str
    match_id: str
    resume_id: str
    notification_type: str
    recipient: str
    message: str
    match_score: float
    sent_at: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)

class TestNotificationResponse(BaseModel):
    """
    Response schema for a manually triggered test notification.
    """
    success: bool
    message: str
    status: str

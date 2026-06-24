from fastapi import APIRouter, status, HTTPException
from typing import List
from datetime import datetime

from app.schemas.notification import NotificationResponse, TestNotificationResponse
from app.models.notification import Notification
from app.core.config import settings
from app.services.notification_service import send_telegram_message

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
async def list_notifications():
    """
    Retrieve all notification logs stored in the database.
    """
    notifications = await Notification.find().sort("-sent_at").to_list()
    return [
        NotificationResponse(
            id=str(n.id),
            job_id=str(n.job_id),
            match_id=str(n.match_id),
            resume_id=str(n.resume_id),
            notification_type=n.notification_type,
            recipient=n.recipient,
            message=n.message,
            match_score=n.match_score,
            sent_at=n.sent_at,
            status=n.status
        )
        for n in notifications
    ]

@router.get("/history", response_model=List[NotificationResponse], status_code=status.HTTP_200_OK)
async def get_notification_history():
    """
    Retrieve successfully dispatched/logged notifications.
    """
    notifications = await Notification.find(Notification.status == "sent").sort("-sent_at").to_list()
    return [
        NotificationResponse(
            id=str(n.id),
            job_id=str(n.job_id),
            match_id=str(n.match_id),
            resume_id=str(n.resume_id),
            notification_type=n.notification_type,
            recipient=n.recipient,
            message=n.message,
            match_score=n.match_score,
            sent_at=n.sent_at,
            status=n.status
        )
        for n in notifications
    ]

@router.post("/test", response_model=TestNotificationResponse, status_code=status.HTTP_200_OK)
async def send_test_notification():
    """
    Trigger a manual connection test to the Telegram endpoint.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    test_msg = "🚀 AI Job Agent Notification Test Successful"
    
    is_simulated = (
        not token or 
        not chat_id or 
        "your_" in token.lower() or 
        "your_" in chat_id.lower()
    )
    
    if is_simulated:
        return TestNotificationResponse(
            success=True,
            message="Telegram connection test simulated successfully (keys not set or placeholders).",
            status="simulated"
        )
        
    success = await send_telegram_message(token, chat_id, test_msg)
    if success:
        return TestNotificationResponse(
            success=True,
            message="Telegram connection test succeeded. Message dispatched.",
            status="sent"
        )
    else:
        return TestNotificationResponse(
            success=False,
            message="Telegram message delivery failed. Check bot credentials or network.",
            status="failed"
        )

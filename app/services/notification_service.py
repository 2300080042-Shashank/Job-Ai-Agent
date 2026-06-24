import logging
import httpx
from datetime import datetime
from typing import Optional, List, Tuple
from beanie import PydanticObjectId

from app.core.config import settings
from app.models.notification import Notification
from app.models.resume import Resume
from app.models.job import Job
from app.models.match import Match

logger = logging.getLogger(__name__)

def get_match_category(score: float) -> str:
    """
    Categorize match scores based on requirements.
    """
    if score >= 0.90:
        return "Excellent Match"
    elif score >= 0.75:
        return "Strong Match"
    elif score >= 0.50:
        return "Potential Match"
    else:
        return "Ignore"

def format_telegram_message(
    company: str,
    role: str,
    location: str,
    score: float,
    category: str,
    matched_skills: List[str],
    missing_skills: List[str],
    apply_link: str
) -> str:
    """
    Format standard job match notification alert.
    """
    matched = ", ".join(matched_skills) if matched_skills else "None"
    missing = ", ".join(missing_skills) if missing_skills else "None"
    link = apply_link or "Not provided"
    
    return (
        f"🔥 New Job Match\n\n"
        f"Company: {company}\n"
        f"Role: {role}\n"
        f"Location: {location}\n\n"
        f"Match Score: {score}\n\n"
        f"Match Category: {category}\n\n"
        f"Matched Skills:\n{matched}\n\n"
        f"Missing Skills:\n{missing}\n\n"
        f"Apply:\n{link}"
    )

async def send_telegram_message(token: str, chat_id: str, text: str) -> bool:
    """
    Query the Telegram Bot sendMessage endpoint.
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=10.0)
            if resp.status_code == 200:
                logger.info("Telegram message sent successfully.")
                return True
            else:
                logger.error(f"Telegram API responded with status {resp.status_code}: {resp.text}")
                return False
    except Exception as e:
        logger.error(f"Failed to connect to Telegram API: {e}")
        return False

async def process_match_notifications(match_doc: Match, resume_doc: Resume, job_doc: Job) -> Optional[Notification]:
    """
    Evaluates a match result, checks for duplicate alerts, formats, 
    and sends a Telegram notification if match score >= 0.50.
    """
    score = match_doc.overall_match_score
    if score < 0.50:
        logger.debug(f"Match score {score} is below threshold. Skipping notification.")
        return None
        
    # Prevent duplicate notifications for the same job-resume pair
    existing = await Notification.find_one(
        Notification.resume_id == resume_doc.id,
        Notification.job_id == job_doc.id
    )
    if existing:
        logger.debug(f"Notification already exists for resume {resume_doc.id} and job {job_doc.id}. Skipping.")
        return existing
        
    category = get_match_category(score)
    message_text = format_telegram_message(
        company=job_doc.company,
        role=job_doc.role,
        location=job_doc.location or "Not specified",
        score=score,
        category=category,
        matched_skills=match_doc.matched_skills,
        missing_skills=match_doc.missing_skills,
        apply_link=job_doc.apply_link
    )
    
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    # Check if Telegram keys are configured or use test simulation
    is_simulated = (
        not token or 
        not chat_id or 
        "your_" in token.lower() or 
        "your_" in chat_id.lower()
    )
    
    if is_simulated:
        logger.info(f"[TELEGRAM SIMULATION] Dispatching to Chat ID {chat_id or 'No-ID'}:\n{message_text}")
        status = "sent"
    else:
        logger.info(f"Dispatching match notification alert to chat {chat_id}...")
        success = await send_telegram_message(token, chat_id, message_text)
        status = "sent" if success else "failed"
        
    notification_doc = Notification(
        job_id=job_doc.id,
        match_id=match_doc.id,
        resume_id=resume_doc.id,
        notification_type="telegram",
        recipient=chat_id or "SimulatedChatID",
        message=message_text,
        match_score=score,
        status=status
    )
    await notification_doc.insert()
    return notification_doc

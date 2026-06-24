import logging
from datetime import datetime
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError

from app.models.resume import Resume
from app.models.job import Job
from app.models.match import Match
from app.models.job_run import JobRun
from app.services.job_service import search_and_discover_jobs
from app.services.match_service import get_or_create_matches
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize APScheduler AsyncIOScheduler
scheduler = AsyncIOScheduler()

async def run_agent_cycle() -> JobRun:
    """
    Background worker cycle:
    1. Search and discover jobs based on candidate skills.
    2. Run matching engine for all resumes.
    3. Persist run results in JobRun collection.
    4. Avoid duplicate notifications by tracking newly discovered matches.
    """
    logger.info("Starting background autonomous job discovery cycle...")
    
    # 1. Create a new JobRun record
    job_run = JobRun(
        started_at=datetime.utcnow(),
        status="running"
    )
    await job_run.insert()
    
    try:
        # 2. Gather unique skills from all candidate resumes
        resumes = await Resume.find_all().to_list()
        keywords = set()
        for res in resumes:
            for skill in (res.skills or []):
                if skill and len(skill.strip()) > 1:
                    keywords.add(skill.strip())
                    
        # Fallback to default keywords if no resumes or skills are present
        if not keywords:
            keywords = {"Python", "FastAPI", "Developer"}
            
        logger.info(f"Gathered search keywords for discovery: {keywords}")
        
        # 3. Discover and store jobs for each keyword
        jobs_before = await Job.count()
        
        for kw in keywords:
            try:
                # search_and_discover_jobs already filters duplicates and saves to DB
                await search_and_discover_jobs(keyword=kw, location=None)
            except Exception as e:
                logger.error(f"Error during job discovery for keyword '{kw}': {e}")
                
        jobs_after = await Job.count()
        new_jobs_found = max(0, jobs_after - jobs_before)
        logger.info(f"Discovery complete. New jobs found: {new_jobs_found}")
        
        # 4. Run matching engine for all resumes
        new_matches_count = 0
        
        # Track existing match IDs before running the matching engine to avoid duplicate notifications
        existing_matches = await Match.find_all().to_list()
        existing_match_keys = {(m.resume_id, m.job_id) for m in existing_matches}
        
        for res in resumes:
            try:
                # get_or_create_matches calculates and stores matches for all stored jobs
                matches = await get_or_create_matches(res.id)
                
                # Check for newly created matches for notification tracking
                for match_doc, job_doc in matches:
                    key = (match_doc.resume_id, match_doc.job_id)
                    if key not in existing_match_keys:
                        new_matches_count += 1
                        # Trigger autonomous notification dispatch for newly found match
                        from app.services.notification_service import process_match_notifications
                        await process_match_notifications(match_doc, res, job_doc)
            except Exception as e:
                logger.error(f"Error calculating matches for resume '{res.id}': {e}")
                
        # 5. Update JobRun record with success status
        job_run.completed_at = datetime.utcnow()
        job_run.jobs_found = new_jobs_found
        job_run.matches_created = new_matches_count
        job_run.status = "success"
        await job_run.save()
        logger.info(f"Background cycle completed successfully. Run ID: {job_run.run_id}")
        return job_run
        
    except Exception as e:
        logger.error(f"Autonomous background agent run failed: {e}")
        job_run.completed_at = datetime.utcnow()
        job_run.status = "failed"
        await job_run.save()
        raise e

def start_scheduler():
    """
    Starts the background scheduler.
    """
    if not scheduler.running:
        # Run cycle every 10 minutes
        scheduler.add_job(
            run_agent_cycle,
            "interval",
            minutes=10,
            id="autonomous_job_discovery_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info("APScheduler background agent started successfully (interval: 10 minutes).")

def shutdown_scheduler():
    """
    Shuts down the background scheduler.
    """
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler background agent shut down.")

def get_scheduler_next_run() -> Optional[datetime]:
    """
    Returns the next execution time of the background job.
    """
    try:
        job = scheduler.get_job("autonomous_job_discovery_job")
        if job:
            return job.next_run_time
    except Exception:
        pass
    return None

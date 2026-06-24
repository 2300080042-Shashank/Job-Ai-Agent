import asyncio
import logging
from typing import List

from app.models.job import Job
from app.services.adapters.wellfound import WellfoundSource
from app.services.adapters.internshala import InternshalaSource
from app.services.adapters.unstop import UnstopSource

logger = logging.getLogger(__name__)

async def search_and_discover_jobs(keyword: str, location: str) -> List[Job]:
    """
    Query all source adapters concurrently for jobs, filter duplicates,
    save new listings to MongoDB, and return the combined list.
    """
    logger.info(f"Triggering job discovery for keyword='{keyword}', location='{location}'")
    
    # Initialize adapters
    adapters = [
        WellfoundSource(),
        InternshalaSource(),
        UnstopSource()
    ]
    
    # Concurrently gather job listings
    tasks = [adapter.fetch_jobs(keyword, location) for adapter in adapters]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    discovered_jobs = []
    for idx, res in enumerate(results):
        if isinstance(res, Exception):
            logger.error(f"Adapter {adapters[idx].__class__.__name__} failed: {res}")
        elif isinstance(res, list):
            discovered_jobs.extend(res)
            
    saved_jobs = []
    # Prevent duplicate records and insert into MongoDB
    for job_data in discovered_jobs:
        try:
            existing = await Job.find_one(
                Job.company == job_data.company,
                Job.role == job_data.role,
                Job.source == job_data.source
            )
            if not existing:
                # Beanie insert generates the ObjectId
                await job_data.insert()
                saved_jobs.append(job_data)
                logger.info(f"Saved new job: {job_data.role} at {job_data.company} ({job_data.source})")
            else:
                saved_jobs.append(existing)
                logger.debug(f"Job already exists in database: {job_data.role} at {job_data.company}")
        except Exception as e:
            logger.error(f"Failed to process/save discovered job: {e}")
            
    return saved_jobs

async def get_stored_jobs() -> List[Job]:
    """
    Retrieve all jobs stored in MongoDB.
    """
    return await Job.find_all().to_list()

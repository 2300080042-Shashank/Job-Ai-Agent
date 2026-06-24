from fastapi import APIRouter, Query, status
from typing import List, Optional

from app.schemas.job import JobResponse
from app.services.job_service import search_and_discover_jobs, get_stored_jobs

router = APIRouter()

@router.get("/search", response_model=List[JobResponse], status_code=status.HTTP_200_OK)
async def search_jobs(
    keyword: str = Query(..., description="Keyword to search for jobs (e.g. Python, Developer)"),
    location: Optional[str] = Query(None, description="Optional location filter")
):
    """
    Search and discover jobs from multiple adapters (Wellfound, Internshala, Unstop) concurrently,
    save new results to MongoDB, and return the combined listings.
    """
    jobs = await search_and_discover_jobs(keyword, location)
    
    return [
        JobResponse(
            id=str(job.id),
            company=job.company,
            role=job.role,
            location=job.location,
            salary=job.salary,
            deadline=job.deadline,
            apply_link=job.apply_link,
            source=job.source,
            job_description=job.job_description,
            created_at=job.created_at
        )
        for job in jobs
    ]

@router.get("/", response_model=List[JobResponse], status_code=status.HTTP_200_OK)
async def list_stored_jobs():
    """
    Retrieve all jobs stored in the database.
    """
    jobs = await get_stored_jobs()
    
    return [
        JobResponse(
            id=str(job.id),
            company=job.company,
            role=job.role,
            location=job.location,
            salary=job.salary,
            deadline=job.deadline,
            apply_link=job.apply_link,
            source=job.source,
            job_description=job.job_description,
            created_at=job.created_at
        )
        for job in jobs
    ]

import logging
from typing import List
from app.services.adapters.base import BaseJobSource
from app.models.job import Job

logger = logging.getLogger(__name__)

class WellfoundSource(BaseJobSource):
    """
    Adapter for Wellfound (formerly AngelList) job listings.
    """
    async def fetch_jobs(self, keyword: str, location: str) -> List[Job]:
        logger.info(f"Fetching Wellfound jobs for keyword='{keyword}', location='{location}'")
        jobs = []
        
        # Simulated programmatic discovery for Wellfound
        k_lower = keyword.lower()
        if any(term in k_lower for term in ["python", "fastapi", "django", "backend", "software", "developer", "engineer"]):
            jobs.append(
                Job(
                    company="AlphaTech",
                    role=f"Senior {keyword.capitalize()} Engineer",
                    location=location or "Remote",
                    salary="$80,000 - $110,000",
                    deadline="2026-08-30",
                    apply_link="https://wellfound.com/jobs/alphatech-senior-engineer",
                    source="wellfound",
                    job_description=f"Join AlphaTech to work on cutting-edge solutions using {keyword}."
                )
            )
            jobs.append(
                Job(
                    company="NextGen AI",
                    role=f"{keyword.capitalize()} Developer",
                    location=location or "San Francisco, CA",
                    salary="$95,000 - $130,000",
                    deadline="2026-09-15",
                    apply_link="https://wellfound.com/jobs/nextgen-developer",
                    source="wellfound",
                    job_description=f"Looking for a passionate {keyword} developer to build AI agents."
                )
            )
        else:
            jobs.append(
                Job(
                    company="StartupHub",
                    role=f"General {keyword.capitalize()} Specialist",
                    location=location or "Remote",
                    salary="$60,000 - $80,000",
                    deadline="2026-07-31",
                    apply_link="https://wellfound.com/jobs/startuphub-specialist",
                    source="wellfound",
                    job_description=f"Seeking a talented professional skilled in {keyword}."
                )
            )
            
        return jobs

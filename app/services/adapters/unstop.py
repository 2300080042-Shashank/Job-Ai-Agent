import logging
from typing import List
from app.services.adapters.base import BaseJobSource
from app.models.job import Job

logger = logging.getLogger(__name__)

class UnstopSource(BaseJobSource):
    """
    Adapter for Unstop competition and hiring listings.
    """
    async def fetch_jobs(self, keyword: str, location: str) -> List[Job]:
        logger.info(f"Fetching Unstop listings for keyword='{keyword}', location='{location}'")
        jobs = []
        
        # Simulated programmatic discovery for Unstop
        k_lower = keyword.lower()
        if any(term in k_lower for term in ["python", "fastapi", "django", "backend", "software", "developer", "engineer"]):
            jobs.append(
                Job(
                    company="BigTech Corp",
                    role=f"{keyword.capitalize()} Developer Hackathon & Hiring",
                    location=location or "Delhi, India",
                    salary="₹6 - ₹10 LPA",
                    deadline="2026-08-10",
                    apply_link="https://unstop.com/competitions/bigtech-hiring-challenge",
                    source="unstop",
                    job_description=f"Participate in the hackathon to secure a full-time job role specializing in {keyword}."
                )
            )
        else:
            jobs.append(
                Job(
                    company="Growth Partners",
                    role=f"{keyword.capitalize()} Consultant Challenge",
                    location=location or "Mumbai",
                    salary="₹5 - ₹8 LPA",
                    deadline="2026-07-25",
                    apply_link="https://unstop.com/competitions/consultant-challenge",
                    source="unstop",
                    job_description=f"Solve real business cases featuring {keyword} expertise."
                )
            )
            
        return jobs

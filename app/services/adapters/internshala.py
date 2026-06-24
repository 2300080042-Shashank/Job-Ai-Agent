import logging
from typing import List
from app.services.adapters.base import BaseJobSource
from app.models.job import Job

logger = logging.getLogger(__name__)

class InternshalaSource(BaseJobSource):
    """
    Adapter for Internshala internship/job listings.
    """
    async def fetch_jobs(self, keyword: str, location: str) -> List[Job]:
        logger.info(f"Fetching Internshala listings for keyword='{keyword}', location='{location}'")
        jobs = []
        
        # Simulated programmatic discovery for Internshala
        k_lower = keyword.lower()
        if any(term in k_lower for term in ["python", "fastapi", "django", "backend", "software", "developer", "engineer"]):
            jobs.append(
                Job(
                    company="SkillUp Solutions",
                    role=f"{keyword.capitalize()} Development Internship",
                    location=location or "Remote",
                    salary="₹15,000 - ₹25,000 /month",
                    deadline="2026-07-20",
                    apply_link="https://internshala.com/internship/detail/python-dev",
                    source="internshala",
                    job_description=f"An exciting opportunity to learn and grow as a {keyword} intern."
                )
            )
            jobs.append(
                Job(
                    company="Innovate Labs",
                    role=f"Backend Web Development ({keyword}) Internship",
                    location=location or "Bangalore",
                    salary="₹20,000 - ₹30,000 /month",
                    deadline="2026-08-05",
                    apply_link="https://internshala.com/internship/detail/backend-intern",
                    source="internshala",
                    job_description=f"Work with our core development team to scale backend services built on {keyword}."
                )
            )
        else:
            jobs.append(
                Job(
                    company="Freshers Tech",
                    role=f"{keyword.capitalize()} Associate Internship",
                    location=location or "Remote",
                    salary="₹10,000 /month",
                    deadline="2026-07-15",
                    apply_link="https://internshala.com/internship/detail/associate-intern",
                    source="internshala",
                    job_description=f"Looking for active learners who have basic experience with {keyword}."
                )
            )
            
        return jobs

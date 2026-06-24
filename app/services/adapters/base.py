from abc import ABC, abstractmethod
from typing import List
from app.models.job import Job

class BaseJobSource(ABC):
    """
    Abstract Base Class for all Job discovery source adapters.
    """
    @abstractmethod
    async def fetch_jobs(self, keyword: str, location: str) -> List[Job]:
        """
        Fetch jobs from the source by query keyword and location.
        """
        pass

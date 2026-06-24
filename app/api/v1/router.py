from fastapi import APIRouter
from app.api.v1.endpoints import resumes, jobs, match, agent, notifications

api_router = APIRouter()

api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
api_router.include_router(match.router, prefix="/match", tags=["matching"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])

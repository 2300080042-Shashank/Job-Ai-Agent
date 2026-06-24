from fastapi import APIRouter
from app.api.v1.endpoints import resumes

api_router = APIRouter()

api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])

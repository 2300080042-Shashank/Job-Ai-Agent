from fastapi import APIRouter, HTTPException, status
from typing import List
from beanie import PydanticObjectId
from bson.errors import InvalidId

from app.schemas.match import MatchResponse
from app.schemas.job import JobResponse
from app.services.match_service import get_or_create_matches, get_top_matches

router = APIRouter()

def serialize_match(match_doc, job_doc) -> MatchResponse:
    """
    Helper to structure DB model objects into schema-valid MatchResponse.
    """
    return MatchResponse(
        id=str(match_doc.id),
        resume_id=str(match_doc.resume_id),
        job_id=str(match_doc.job_id),
        skill_match_score=match_doc.skill_match_score,
        keyword_match_score=match_doc.keyword_match_score,
        overall_match_score=match_doc.overall_match_score,
        matched_skills=match_doc.matched_skills,
        missing_skills=match_doc.missing_skills,
        created_at=match_doc.created_at,
        job=JobResponse(
            id=str(job_doc.id),
            company=job_doc.company,
            role=job_doc.role,
            location=job_doc.location,
            salary=job_doc.salary,
            deadline=job_doc.deadline,
            apply_link=job_doc.apply_link,
            source=job_doc.source,
            job_description=job_doc.job_description,
            created_at=job_doc.created_at
        )
    )

@router.get("/{resume_id}", response_model=List[MatchResponse], status_code=status.HTTP_200_OK)
async def list_matches(resume_id: str):
    """
    Retrieve all job matches for the specified resume ID.
    """
    try:
        res_id = PydanticObjectId(resume_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume ID format")
        
    try:
        matches = await get_or_create_matches(res_id)
        return [serialize_match(match_doc, job_doc) for match_doc, job_doc in matches]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/{resume_id}/top", response_model=List[MatchResponse], status_code=status.HTTP_200_OK)
async def list_top_matches(resume_id: str):
    """
    Retrieve the top 10 job matches sorted by overall_match_score descending.
    """
    try:
        res_id = PydanticObjectId(resume_id)
    except InvalidId:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume ID format")
        
    try:
        matches = await get_top_matches(res_id, limit=10)
        return [serialize_match(match_doc, job_doc) for match_doc, job_doc in matches]
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

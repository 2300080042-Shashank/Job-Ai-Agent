from fastapi import APIRouter, UploadFile, File, HTTPException, status
from typing import List

from app.schemas.resume import ResumeResponse
from app.services.resume_service import process_and_save_resume
from app.models.resume import Resume

router = APIRouter()

@router.post("/upload", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume PDF, parse it, extract structured data using AI, and store it.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are supported.")
    
    try:
        resume_doc = await process_and_save_resume(file)
        
        # Prepare response (converting ObjectId to string is handled by Pydantic's BaseModel config and aliases, 
        # but since we didn't specify alias we can map the `id` field)
        return ResumeResponse(
            id=str(resume_doc.id),
            filename=resume_doc.filename,
            parsed_at=resume_doc.parsed_at,
            name=resume_doc.name,
            email=resume_doc.email,
            phone=resume_doc.phone,
            skills=resume_doc.skills,
            experience=[exp.model_dump() for exp in resume_doc.experience],
            education=[edu.model_dump() for edu in resume_doc.education],
            projects=[proj.model_dump() for proj in resume_doc.projects]
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}")

@router.get("/", response_model=List[ResumeResponse])
async def list_resumes():
    """
    Get a list of all parsed resumes in the database.
    """
    resumes = await Resume.find_all().to_list()
    
    responses = []
    for doc in resumes:
        responses.append(ResumeResponse(
            id=str(doc.id),
            filename=doc.filename,
            parsed_at=doc.parsed_at,
            name=doc.name,
            email=doc.email,
            phone=doc.phone,
            skills=doc.skills,
            experience=[exp.model_dump() for exp in doc.experience],
            education=[edu.model_dump() for edu in doc.education],
            projects=[proj.model_dump() for proj in doc.projects]
        ))
    return responses

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: str):
    """
    Get a specific parsed resume by its ID.
    """
    from beanie import PydanticObjectId
    from beanie.exceptions import InvalidId
    
    try:
        obj_id = PydanticObjectId(resume_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid resume ID format")
        
    doc = await Resume.get(obj_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
        
    return ResumeResponse(
        id=str(doc.id),
        filename=doc.filename,
        parsed_at=doc.parsed_at,
        name=doc.name,
        email=doc.email,
        phone=doc.phone,
        skills=doc.skills,
        experience=[exp.model_dump() for exp in doc.experience],
        education=[edu.model_dump() for edu in doc.education],
        projects=[proj.model_dump() for proj in doc.projects]
    )

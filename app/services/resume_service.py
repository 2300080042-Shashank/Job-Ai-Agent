from fastapi import UploadFile
from typing import Dict, Any

from app.models.resume import Resume
from app.services.pdf_parser import parse_pdf_bytes
from app.services.extraction import extract_resume_data

async def process_and_save_resume(file: UploadFile) -> Resume:
    """
    Process the uploaded resume PDF, extract info, and save to database.
    """
    # 1. Read file bytes
    content = await file.read()
    
    # 2. Parse PDF to text
    text = parse_pdf_bytes(content)
    
    # 3. Extract structured data using AI
    extracted_data = await extract_resume_data(text)
    
    # 4. Extract lists safely (fallback to empty list if None or not a list)
    skills = extracted_data.get("skills")
    experience = extracted_data.get("experience")
    education = extracted_data.get("education")
    projects = extracted_data.get("projects")
    
    # 5. Create and save Beanie document
    resume_doc = Resume(
        filename=file.filename,
        name=extracted_data.get("name"),
        email=extracted_data.get("email"),
        phone=extracted_data.get("phone"),
        skills=skills if isinstance(skills, list) else [],
        experience=experience if isinstance(experience, list) else [],
        education=education if isinstance(education, list) else [],
        projects=projects if isinstance(projects, list) else []
    )
    
    await resume_doc.insert()
    
    return resume_doc

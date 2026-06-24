from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class ExperienceSchema(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None

class EducationSchema(BaseModel):
    institution: Optional[str] = None
    degree: Optional[str] = None
    field_of_study: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class ProjectSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = []
    link: Optional[str] = None

class ResumeResponse(BaseModel):
    id: str
    filename: str
    parsed_at: datetime
    
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience: List[ExperienceSchema] = []
    education: List[EducationSchema] = []
    projects: List[ProjectSchema] = []

    model_config = ConfigDict(from_attributes=True)

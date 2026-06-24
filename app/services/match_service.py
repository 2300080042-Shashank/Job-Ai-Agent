import logging
from typing import List, Tuple
from beanie import PydanticObjectId

from app.models.resume import Resume
from app.models.job import Job
from app.models.match import Match

logger = logging.getLogger(__name__)

# List of common tech skills to detect missing requirements from job descriptions
COMMON_TECHNICAL_SKILLS = [
    "python", "fastapi", "django", "flask", "javascript", "typescript",
    "react", "angular", "vue", "node", "express", "java", "spring",
    "c++", "c#", "go", "rust", "sql", "mysql", "postgresql", "mongodb",
    "redis", "docker", "kubernetes", "aws", "gcp", "azure", "git",
    "html", "css", "machine learning", "deep learning", "ai", "pandas",
    "numpy", "scikit-learn", "tensorflow", "pytorch", "next.js", "nextjs",
    "powerbi", "tableau", "excel", "graphql", "rest api", "restful api",
    "linux", "bash", "spark", "hadoop"
]

def calculate_match_scores(resume: Resume, job: Job) -> Tuple[float, float, float, List[str], List[str]]:
    """
    Perform matching logic:
    Step 1: Compare resume skills against job description.
    Step 2: Compare resume skills against job title (role).
    Step 3: Calculate skill_match_score, keyword_match_score, and overall_match_score.
    """
    resume_skills = resume.skills or []
    if not resume_skills:
        return 0.0, 0.0, 0.0, [], []
        
    desc_lower = (job.job_description or "").lower()
    role_lower = (job.role or "").lower()
    
    # 1. Compare resume skills against job description
    matched_skills = []
    for skill in resume_skills:
        if skill.lower() in desc_lower:
            matched_skills.append(skill)
            
    skill_match_score = len(matched_skills) / len(resume_skills)
    
    # 2. Compare resume skills against job title
    matched_title_skills = []
    for skill in resume_skills:
        if skill.lower() in role_lower:
            matched_title_skills.append(skill)
            
    keyword_match_score = len(matched_title_skills) / len(resume_skills)
    
    # 3. Calculate overall_match_score
    overall_match_score = (skill_match_score * 0.7) + (keyword_match_score * 0.3)
    
    # 4. Identify missing skills
    missing_skills = []
    resume_skills_lower = {s.lower() for s in resume_skills}
    for tech in COMMON_TECHNICAL_SKILLS:
        if tech in desc_lower and tech not in resume_skills_lower:
            # Format nicely
            formatted = tech.upper() if tech in ["sql", "aws", "gcp", "ai", "css", "html"] else tech.capitalize()
            missing_skills.append(formatted)
            
    return round(skill_match_score, 4), round(keyword_match_score, 4), round(overall_match_score, 4), matched_skills, missing_skills

async def get_or_create_matches(resume_id: PydanticObjectId) -> List[Tuple[Match, Job]]:
    """
    Compute and upsert matches for the resume against all stored jobs,
    then return list of matching documents and their associated Job metadata.
    """
    resume = await Resume.get(resume_id)
    if not resume:
        raise ValueError("Resume not found")
        
    jobs = await Job.find_all().to_list()
    results = []
    
    for job in jobs:
        skill_score, kw_score, overall_score, matched, missing = calculate_match_scores(resume, job)
        
        # Check if match already exists
        match_doc = await Match.find_one(
            Match.resume_id == resume.id,
            Match.job_id == job.id
        )
        if not match_doc:
            match_doc = Match(
                resume_id=resume.id,
                job_id=job.id,
                skill_match_score=skill_score,
                keyword_match_score=kw_score,
                overall_match_score=overall_score,
                matched_skills=matched,
                missing_skills=missing
            )
            await match_doc.insert()
        else:
            match_doc.skill_match_score = skill_score
            match_doc.keyword_match_score = kw_score
            match_doc.overall_match_score = overall_score
            match_doc.matched_skills = matched
            match_doc.missing_skills = missing
            await match_doc.save()
            
        results.append((match_doc, job))
        
    return results

async def get_top_matches(resume_id: PydanticObjectId, limit: int = 10) -> List[Tuple[Match, Job]]:
    """
    Retrieve matches for a resume and sort them to return the top N jobs by overall_match_score.
    """
    matches = await get_or_create_matches(resume_id)
    # Sort matches by overall_match_score descending
    matches.sort(key=lambda x: x[0].overall_match_score, reverse=True)
    return matches[:limit]

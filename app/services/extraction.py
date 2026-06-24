import json
import logging
import google.generativeai as genai
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini with the API key from settings
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

async def extract_resume_data(text: str) -> Dict[str, Any]:
    """
    Calls Google Gemini to extract structured data from raw resume text.
    """
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured.")

    prompt = """
You are an expert resume parser. I will provide you with the raw text extracted from a resume PDF.
Your task is to extract the following information and return it STRICTLY as a valid JSON object without any markdown formatting or extra text.

Extract these fields:
- name: string (Candidate's full name, or null)
- email: string (Candidate's email, or null)
- phone: string (Candidate's phone number, or null)
- skills: list of strings (List of technical and soft skills)
- experience: list of objects. Each object should have:
  - company: string or null
  - role: string or null
  - start_date: string or null
  - end_date: string or null
  - description: string or null (Summary of achievements)
  - duration: string or null (e.g. "2 years", "6 months", or null)
- education: list of objects. Each object should have:
  - institution: string or null
  - degree: string or null
  - field_of_study: string or null
  - start_date: string or null
  - end_date: string or null
- projects: list of objects. Each object should have:
  - name: string or null
  - description: string or null
  - technologies: list of strings
  - link: string or null

Resume Text:
---
{text}
---

Remember: Only return valid JSON. Do not wrap it in ```json blocks.
"""

    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = await model.generate_content_async(prompt.format(text=text))
        
        response_text = response.text.strip()
        
        # Sometimes the model might still return markdown blocks despite instructions
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        response_text = response_text.strip()
        
        data = json.loads(response_text)
        return data

    except Exception as e:
        logger.error(f"Failed to extract resume data via Gemini: {e}")
        raise ValueError(f"AI extraction failed: {str(e)}")

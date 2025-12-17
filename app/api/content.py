from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlmodel import Session
from app.db.database import get_session
from app.models.user import User
from app.agents.content_crew import ContentCrew
from app.core.llm import get_llm # <--- NEW IMPORT
import json
from fastapi.responses import StreamingResponse
from app.services.pdf_generator import PDFGenerator

router = APIRouter()

class ChapterRequest(BaseModel):
    user_id: int 
    topic: str
    subtopics: List[str]
    detail_level: str

class ChapterPDFRequest(BaseModel):
    topic: str
    content: str

@router.post("/generate-chapter")
async def generate_chapter(req: ChapterRequest, session: Session = Depends(get_session)):
    try:
        # 1. Fetch User
        user = session.get(User, req.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Personalization Logic (Keep existing)
        style_note = ""
        if user.profile_data:
            p = user.profile_data
            if isinstance(p, str): 
                try: p = json.loads(p)
                except: pass
            if isinstance(p, dict):
                 style_note = f" (User prefers {p.get('learning_style')})"

        # 3. Initialize Dynamic LLM (The Fix)
        try:
            crew_llm = get_llm(user.preferred_model, user.gemini_api_key)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 4. Instantiate Crew with LLM
        content_crew = ContentCrew(llm=crew_llm)
        
        enhanced_level = f"{req.detail_level}{style_note}"
        
        # 5. Kickoff
        result = content_crew.create_chapter(
            topic=req.topic,
            subtopics=req.subtopics,
            detail_level=enhanced_level
        )
        
        # Handle Output
        final_output = result.raw if hasattr(result, 'raw') else str(result)
        
        return {"status": "success", "content": final_output}

    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
             raise HTTPException(status_code=429, detail="Gemini Free Tier Limit Reached. Please wait a minute.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chapter/download-pdf")
async def download_chapter_pdf(req: ChapterPDFRequest):
    pdf_gen = PDFGenerator()
    pdf_buffer = pdf_gen.generate_chapter_pdf(req.topic, req.content)
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=chapter.pdf"}
    )

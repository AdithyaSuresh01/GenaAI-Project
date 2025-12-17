from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from app.db.database import get_session
from app.models.user import User
from app.agents.roadmap_crew import RoadmapCrew
from app.core.llm import get_llm # <--- NEW IMPORT
import json
from fastapi.responses import StreamingResponse
from app.services.pdf_generator import PDFGenerator

router = APIRouter()

class PDFRequest(BaseModel):
    topic: str
    duration: str
    data: dict

class RoadmapRequest(BaseModel):
    user_id: int 
    topic: str
    duration: str
    level: str

@router.post("/generate-roadmap")
async def generate_roadmap(req: RoadmapRequest, session: Session = Depends(get_session)):
    try:
        # 1. Fetch User
        user = session.get(User, req.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Build Personal Context (Keep existing logic)
        personal_context = ""
        if user.profile_data:
            p = user.profile_data
            if isinstance(p, str): 
                try: p = json.loads(p)
                except: pass
            if isinstance(p, dict):
                personal_context = (
                    f" (Context: User has {p.get('daily_time')} daily. "
                    f"Goal: {p.get('career_goal')}. Style: {p.get('learning_style')})"
                )

        # 3. Initialize Dynamic LLM (The Fix)
        try:
            crew_llm = get_llm(user.preferred_model, user.gemini_api_key)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 4. Instantiate Crew with LLM
        roadmap_crew = RoadmapCrew(llm=crew_llm)
        
        # 5. Append context
        enhanced_topic = f"{req.topic}{personal_context}"
        
        # 6. Execute Crew
        result = roadmap_crew.create_roadmap(
            topic=enhanced_topic,
            duration=req.duration,
            level=req.level
        )
        
        # CrewAI returns CrewOutput, handle string conversion
        final_output = result.raw if hasattr(result, 'raw') else str(result)
        
        return {"status": "success", "roadmap": final_output}

    except Exception as e:
        # Handle Rate Limits specifically for better UX
        if "429" in str(e) or "ResourceExhausted" in str(e):
             raise HTTPException(status_code=429, detail="Gemini Free Tier Limit Reached. Please wait a minute and try again.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download-pdf")
async def download_roadmap_pdf(req: PDFRequest):
    pdf_gen = PDFGenerator()
    pdf_buffer = pdf_gen.generate_roadmap_pdf(req.topic, req.duration, req.data)
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=roadmap_{req.topic}.pdf"}
    )

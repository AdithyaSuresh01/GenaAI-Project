from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from app.db.database import get_session
from app.models.user import User
from app.agents.debug_crew import DebugCrew
from app.core.llm import get_llm # <--- NEW IMPORT
import json
from fastapi.responses import StreamingResponse
from app.services.pdf_generator import PDFGenerator

router = APIRouter()

class DebugRequest(BaseModel):
    user_id: int 
    code_snippet: str
    error_message: str

class DebugPDFRequest(BaseModel):
    code: str
    error: str
    solution: str

@router.post("/debug")
async def debug_code(req: DebugRequest, session: Session = Depends(get_session)):
    try:
        # 1. Fetch User
        user = session.get(User, req.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 2. Personalization Logic
        expertise = "Intermediate"
        if user.profile_data:
            p = user.profile_data
            if isinstance(p, str): 
                try: p = json.loads(p)
                except: pass
            if isinstance(p, dict):
                 expertise = p.get('current_skill', 'Intermediate')

        context_msg = f"{req.error_message}\n(Explain solution for a {expertise} level developer)"

        # 3. Initialize Dynamic LLM (The Fix)
        try:
            crew_llm = get_llm(user.preferred_model, user.gemini_api_key)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 4. Instantiate Crew with LLM
        debug_crew = DebugCrew(llm=crew_llm)
        
        # 5. Kickoff
        result = debug_crew.debug_code(
            code_snippet=req.code_snippet,
            error_message=context_msg
        )
        
        # Handle Output
        final_output = result.raw if hasattr(result, 'raw') else str(result)

        return {"status": "success", "solution": final_output}

    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
             raise HTTPException(status_code=429, detail="Gemini Free Tier Limit Reached. Please wait a minute.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/debug/download-pdf")
async def download_debug_pdf(req: DebugPDFRequest):
    pdf_gen = PDFGenerator()
    pdf_buffer = pdf_gen.generate_debug_report(req.code, req.error, req.solution)
    
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=debug_report.pdf"}
    )

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.user import User, Quiz
from app.agents.assessment_crew import AssessmentCrew
from app.core.llm import get_llm
import json
import re
from fastapi.responses import StreamingResponse
from app.services.pdf_generator import PDFGenerator

router = APIRouter()

class AssessmentPDFRequest(BaseModel):
    title: str
    questions: list
    score: int = 0
    total: int = 0
    include_results: bool = False

class SurveyData(BaseModel):
    user_id: int
    learning_style: str
    daily_time: str
    career_goal: str
    current_skill: str

class QuizRequest(BaseModel):
    user_id: int
    topic: str
    type: str 

class ScoreUpdate(BaseModel):
    quiz_id: int
    score: int

@router.post("/save-survey")
def save_survey(data: SurveyData, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == data.user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.profile_data = data.dict()
    session.add(user)
    session.commit()
    return {"status": "success", "message": "Profile personalized!"}

@router.post("/generate-assessment")
def generate_assessment(req: QuizRequest, session: Session = Depends(get_session)):
    try:
        # 1. Fetch User
        statement = select(User).where(User.id == req.user_id)
        user = session.exec(statement).first()
        if not user: raise HTTPException(status_code=404, detail="User not found")
        
        # 2. Get LLM
        try:
            crew_llm = get_llm(user.preferred_model, user.gemini_api_key)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # 3. Context Logic
        profile_context = "General Learner"
        if user and user.profile_data:
            p = user.profile_data
            if isinstance(p, str): 
                try: p = json.loads(p)
                except: pass
            if isinstance(p, dict):
                profile_context = f"Skill Level: {p.get('current_skill')}. Learning Style: {p.get('learning_style')}."

        # 4. Instantiate Crew
        assessment_crew = AssessmentCrew(llm=crew_llm)
        
        # 5. Kickoff
        crew_output = assessment_crew.create_assessment(
            topic=req.topic,
            assessment_type=req.type,
            user_context=profile_context
        )
        
        raw_output = str(crew_output)
        json_match = re.search(r"(\{.*\})", raw_output, re.DOTALL)
        
        if json_match:
            clean_json = json_match.group(1)
        else:
            clean_json = raw_output.replace("```json", "").replace("```", "").strip()

        quiz_data = json.loads(clean_json)
        
        # Save to DB
        new_quiz = Quiz(
            user_id=req.user_id,
            topic=req.topic,
            difficulty="Adaptive",
            questions=quiz_data
        )
        session.add(new_quiz)
        session.commit()
        session.refresh(new_quiz)
        
        return {
            "id": new_quiz.id,
            "title": quiz_data.get('title', f'{req.type.capitalize()} on {req.topic}'),
            "questions": quiz_data.get('questions', [])
        }
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="AI failed to format correctly. Try again.")
    except Exception as e:
        if "429" in str(e) or "ResourceExhausted" in str(e):
             raise HTTPException(status_code=429, detail="Gemini Limit Reached. Wait 60s.")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ... (submit_score, get_user_scores, download_pdf remain SAME as your code) ...
@router.post("/submit-score")
def submit_score(data: ScoreUpdate, session: Session = Depends(get_session)):
    quiz = session.get(Quiz, data.quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    quiz.score = data.score
    session.add(quiz)
    session.commit()
    return {"status": "success"}

@router.get("/user-scores/{user_id}")
def get_user_scores(user_id: int, session: Session = Depends(get_session)):
    statement = select(Quiz).where(Quiz.user_id == user_id, Quiz.score != None).order_by(Quiz.id.desc())
    results = session.exec(statement).all()
    return [{"topic": q.topic, "difficulty": q.difficulty, "score": q.score} for q in results]

@router.post("/assessment/download-pdf")
async def download_assessment_pdf(req: AssessmentPDFRequest):
    pdf_gen = PDFGenerator()
    results = {"score": req.score, "total": req.total} if req.include_results else None
    pdf_buffer = pdf_gen.generate_assessment_pdf(req.title, req.questions, results)
    return StreamingResponse(
        pdf_buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=assessment.pdf"}
    )

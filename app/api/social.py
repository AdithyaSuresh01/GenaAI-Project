from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
from sqlmodel import Session
from app.db.database import get_session
from app.models.user import User
from app.core.llm import get_llm # <--- NEW IMPORT
from app.services.github_manager import push_to_github
from app.services.linkedin_manager import generate_linkedin_post, post_to_linkedin 

router = APIRouter()

BASE_PROJECT_DIR = os.path.join(os.getcwd(), "generated_projects")

class SocialRequest(BaseModel):
    user_id: int # <--- ADDED to fetch API Key
    project_name: str
    description: str
    tech_stack: str
    tone: str

class LinkedInPostRequest(BaseModel):
    token: str
    content: str

class GitHubPushRequest(BaseModel):
    user_id: str
    token: str
    project_name: str
    description: str
    is_private: bool

@router.post("/generate-social")
async def generate_social(request: SocialRequest, session: Session = Depends(get_session)):
    # 1. Fetch User
    user = session.get(User, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 2. Get LLM
    try:
        crew_llm = get_llm(user.preferred_model, user.gemini_api_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3. Generate Content
    try:
        # We pass the LLM object to the service function
        # You need to update app/services/linkedin_manager.py to accept 'llm'
        content = generate_linkedin_post(
            request.project_name, 
            request.description, 
            request.tech_stack, 
            request.tone,
            llm=crew_llm # <--- PASSING LLM
        )
        return {"content": content}
    except Exception as e:
        if "429" in str(e):
             raise HTTPException(status_code=429, detail="Gemini Rate Limit. Wait 60s.")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/linkedin/post")
async def post_linkedin(request: LinkedInPostRequest):
    result = post_to_linkedin(request.token, request.content)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message"))
        
    return result


@router.post("/github/push")
async def github_push(request: GitHubPushRequest):
    user_folder = f"user_{request.user_id}"
    project_path = os.path.join(BASE_PROJECT_DIR, user_folder, request.project_name)
    
    # Handle case sensitivity for folder names
    if not os.path.exists(project_path):
        parent_dir = os.path.join(BASE_PROJECT_DIR, user_folder)
        if os.path.exists(parent_dir):
            found = False
            for d in os.listdir(parent_dir):
                if d.lower() == request.project_name.lower():
                    project_path = os.path.join(parent_dir, d)
                    found = True
                    break
            if not found:
                 return {"status": "error", "message": f"Project folder not found: {request.project_name}"}
        else:
             return {"status": "error", "message": f"User folder not found: {user_folder}"}

    result = push_to_github(
        request.token, 
        request.project_name, 
        request.description, 
        request.is_private, 
        project_path
    )
    return result

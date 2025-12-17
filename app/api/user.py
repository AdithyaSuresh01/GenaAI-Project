from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.db.database import get_session
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class KeyUpdate(BaseModel):
    user_id: int
    github_token: Optional[str] = None
    linkedin_token: Optional[str] = None
    # NEW FIELDS
    gemini_api_key: Optional[str] = None
    preferred_model: Optional[str] = None

@router.post("/user/update-keys")
def update_keys(data: KeyUpdate, session: Session = Depends(get_session)):
    user = session.get(User, data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Social Tokens
    if data.github_token is not None:
        user.github_token = data.github_token
    if data.linkedin_token is not None:
        user.linkedin_token = data.linkedin_token
        
    # AI Config
    if data.gemini_api_key is not None:
        user.gemini_api_key = data.gemini_api_key
    if data.preferred_model is not None:
        user.preferred_model = data.preferred_model
        
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"status": "success", "message": "Configuration updated successfully"}


@router.get("/user/{user_id}/keys")
def get_keys(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "github_token": user.github_token,
        "linkedin_token": user.linkedin_token,
        "gemini_api_key": user.gemini_api_key,
        "preferred_model": user.preferred_model
    }

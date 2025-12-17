from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.db.database import get_session
from app.models.user import User
from app.services.auth import get_password_hash, verify_password
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    # NEW: Optional API Key during signup
    gemini_api_key: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/signup")
def signup(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pwd = get_password_hash(user.password)
    
    # Determine model preference
    # If they provide a key, default to Gemini. Otherwise default to Perplexity (or whatever you prefer)
    pref_model = "gemini" if user.gemini_api_key else "perplexity"

    new_user = User(
        email=user.email, 
        full_name=user.full_name, 
        hashed_password=hashed_pwd,
        # Save the new fields
        gemini_api_key=user.gemini_api_key,
        preferred_model=pref_model
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    return {"status": "success", "user_id": new_user.id, "name": new_user.full_name}


@router.post("/login")
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_data.email)
    user = session.exec(statement).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
        
    return {
        "status": "success", 
        "user_id": user.id, 
        "name": user.full_name, 
        "email": user.email,
        "profile_data": user.profile_data,
        # Helpful to return this so frontend knows if they need to add a key
        "has_api_key": bool(user.gemini_api_key) 
    }

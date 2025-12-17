from typing import Optional, List, Dict, Any
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, JSON
from datetime import datetime

# --- USER MODEL ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    full_name: str
    hashed_password: str
    
    # --- NEW FIELDS (The missing ones causing the error) ---
    gemini_api_key: Optional[str] = None
    preferred_model: str = Field(default="gemini") # Options: "gemini", "perplexity"
    github_token: Optional[str] = None
    linkedin_token: Optional[str] = None
    
    # Profile Data (JSON)
    profile_data: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    roadmaps: List["Roadmap"] = Relationship(back_populates="user")
    quizzes: List["Quiz"] = Relationship(back_populates="user")

# --- ROADMAP MODEL ---
class Roadmap(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    goal_description: str
    status: str = Field(default="active") 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="roadmaps")

# --- QUIZ MODEL ---
class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    topic: str
    difficulty: str
    score: Optional[int] = None
    questions: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="quizzes")

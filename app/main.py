from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.database import init_db
# Ensure these import paths match your actual file structure
from app.api import (
    roadmap, 
    content, # Ensure file is app/api/content.py
    project, 
    social, 
    debug, 
    auth, 
    user, 
    assessment, 
    oauth
)
from dotenv import load_dotenv
import os

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Database on Startup
    init_db()
    print("✅ Database Initialized")
    yield

app = FastAPI(
    title="Student Success GenAI Platform",
    description="AI-powered competition platform for student goals.",
    version="2.0.0", # Updated version
    lifespan=lifespan
)

# --- CRITICAL: CORS CONFIGURATION ---
# Allows Frontend (Streamlit) to talk to Backend (FastAPI)
origins = [
    "http://localhost",
    "http://localhost:8501",  # Streamlit default port
    "http://127.0.0.1:8501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Register Routers ---
# Prefix groups endpoints cleanly (e.g. /api/v1/generate-roadmap)
app.include_router(oauth.router, prefix="/api/oauth", tags=["OAuth Integrations"])
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(user.router, prefix="/api/v1", tags=["User Management"])
app.include_router(roadmap.router, prefix="/api/v1", tags=["Roadmap Generator"])
app.include_router(content.router, prefix="/api/v1", tags=["Content/Chapter"])
app.include_router(project.router, prefix="/api/v1", tags=["Project Execution"])
app.include_router(social.router, prefix="/api/v1", tags=["Social Media"])
app.include_router(debug.router, prefix="/api/v1", tags=["Code Debugger"])
app.include_router(assessment.router, prefix="/api/v1", tags=["Assessment Center"])

@app.get("/")
async def root():
    return {
        "message": "Student GenAI Platform is running 🚀",
        "model_mode": "Dual-Engine (Gemini/Perplexity)",
        "status": "active"
    }

if __name__ == "__main__":
    import uvicorn
    # 'app.main:app' assumes this file is named main.py inside an 'app' folder
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session
from app.db.database import get_session
from app.models.user import User
from app.agents.project_crew import ProjectCrew
from app.core.llm import get_llm # <--- NEW IMPORT
from app.services.file_manager import save_project_files
from app.services.task_manager import update_task, get_task
import json
import os
import re

router = APIRouter()

class ProjectRequest(BaseModel):
    user_id: int
    description: str
    technology: str
    difficulty: str

# --- UPDATED FUNCTION SIGNATURE ---
def generate_and_save(
    user_id: int, 
    description: str, 
    technology: str, 
    difficulty: str, 
    user_context: str,
    api_key: str,      # Passed from route
    model_pref: str    # Passed from route
):
    try:
        # Step 0: Initialize Dynamic LLM
        try:
            crew_llm = get_llm(model_pref, api_key)
        except ValueError as e:
             update_task(user_id, "error", f"❌ Config Error: {str(e)}", 0)
             return

        # Step 1: Architecting
        update_task(user_id, "processing", "🤖 Architect Designing Structure...", 20)
        
        # Instantiate Crew with LLM
        crew = ProjectCrew(llm=crew_llm)
        
        enhanced_desc = f"{description}\n\nUser Context: {user_context}"
        
        # Step 2: Coding
        update_task(user_id, "processing", "👨‍💻 Agents Writing Code...", 50)
        
        # Run Crew
        try:
            crew_result = crew.generate_project(enhanced_desc, technology, difficulty)
        except Exception as e:
            if "429" in str(e):
                update_task(user_id, "error", "❌ Rate Limit Reached. Please try later.", 0)
                return
            raise e
        
        # Handle Output
        if hasattr(crew_result, 'raw'):
            final_code_str = crew_result.raw
        else:
            final_code_str = str(crew_result)

        # Cleanup Markdown
        json_match = re.search(r"(\{.*\})", final_code_str, re.DOTALL)
        if json_match:
            final_code_str = json_match.group(1)
        else:
            final_code_str = final_code_str.replace("``````", "").strip()

        # Step 3: Saving
        update_task(user_id, "processing", "💾 Saving Files...", 80)
        
        project_name = description.split()[0:3]
        project_name = "_".join(project_name).replace(" ", "")
        
        save_project_files(str(user_id), project_name, final_code_str)
        
        # Save Metadata
        base_dir = os.path.join(os.getcwd(), "generated_projects", f"user_{user_id}", project_name)
        metadata = {
            "original_description": description,
            "tech_stack": technology,
            "difficulty": difficulty
        }
        
        if os.path.exists(base_dir):
            with open(os.path.join(base_dir, "project_info.json"), "w") as f:
                json.dump(metadata, f, indent=4)

        update_task(user_id, "completed", "✅ Project Built Successfully!", 100)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        update_task(user_id, "error", f"❌ Error: {str(e)}", 0)


@router.post("/generate-project")
async def generate_project(req: ProjectRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    # 1. Fetch User
    user = session.get(User, req.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_context = ""
    if user.profile_data:
        p = user.profile_data
        if isinstance(p, str): 
            try: p = json.loads(p)
            except: pass
        if isinstance(p, dict):
             user_context = f"User Skill: {p.get('current_skill')}. Style: {p.get('learning_style')}."

    # 2. Extract Key & Pref to pass to background task
    # We pass these as strings so the background thread doesn't need a DB session
    api_key = user.gemini_api_key
    model_pref = user.preferred_model

    # 3. Schedule Task
    background_tasks.add_task(
        generate_and_save, 
        req.user_id, 
        req.description, 
        req.technology, 
        req.difficulty, 
        user_context,
        api_key,     # Pass Key
        model_pref   # Pass Model
    )
    
    return {"status": "started"}


@router.get("/project-status/{user_id}")
def check_status(user_id: int):
    return get_task(user_id)

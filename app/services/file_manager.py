import os
import json
import re

def sanitize_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', name)

def save_project_files(user_id: str, project_name: str, project_data_str: str):
    """
    Saves files into generated_projects/user_{id}/{project_name}/
    """
    try:
        clean_json = project_data_str.replace("``````", "").strip()
        files = json.loads(clean_json)
        
        # Create specific project folder
        safe_project_name = sanitize_filename(project_name).replace(" ", "_")
        base_path = f"generated_projects/user_{user_id}/{safe_project_name}"
        os.makedirs(base_path, exist_ok=True)
        
        saved_paths = []
        
        for filename, content in files.items():
            if isinstance(content, str):
                # Handle subdirectories in filenames if agent provides them (e.g. "src/main.py")
                file_path = os.path.join(base_path, filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                saved_paths.append(file_path)
                
        return {"status": "saved", "path": base_path, "files": saved_paths}

    except Exception as e:
        return {"status": "error", "message": str(e)}

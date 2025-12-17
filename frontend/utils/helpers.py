import json
import re
import os

def extract_json(text_response):
    """
    Robustly extracts JSON from LLM text responses, handling Markdown code blocks.
    """
    if not text_response:
        return None

    # 1. Try to find JSON inside markdown code blocks ``````
    code_block_pattern = r"``````"
    match = re.search(code_block_pattern, text_response, re.DOTALL)
    
    if match:
        json_str = match.group(1)
    else:
        # 2. Fallback: Try to find the first '{' and last '}'
        # This handles cases where the LLM just dumps raw JSON or wraps it in text
        match = re.search(r"\{.*\}", text_response, re.DOTALL)
        if match:
            json_str = match.group(0)
        else:
            return None

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 3. Last resort: simple cleanup (sometimes LLMs add trailing commas)
        try:
            # simple cleanup for trailing commas before closing braces
            cleaned = re.sub(r",\s*([\]}])", r"\1", json_str)
            return json.loads(cleaned)
        except:
            return None

def get_projects(projects_dir, user_id):
    """
    Lists all projects and their files for a specific user.
    """
    # Construct absolute path safely
    if not os.path.isabs(projects_dir):
        base_dir = os.path.abspath(projects_dir)
    else:
        base_dir = projects_dir
        
    user_folder = f"user_{user_id}"
    user_path = os.path.join(base_dir, user_folder)
    
    projects = {}
    
    if os.path.exists(user_path):
        for item in os.listdir(user_path):
            project_path = os.path.join(user_path, item)
            if os.path.isdir(project_path):
                files = []
                for root, _, filenames in os.walk(project_path):
                     for f in filenames:
                         # Store relative path for cleaner UI
                         rel_p = os.path.relpath(os.path.join(root, f), project_path)
                         files.append(rel_p)
                projects[item] = files
    return projects

def read_project_file(projects_dir, user_id, project_name, filename):
    """
    Safely reads a file content from a user's project.
    """
    if not os.path.isabs(projects_dir):
        base_dir = os.path.abspath(projects_dir)
    else:
        base_dir = projects_dir

    # Safe path construction
    base_path = os.path.join(base_dir, f"user_{user_id}", project_name)
    full_path = os.path.join(base_path, filename)
    
    # Security check: prevent path traversal (../)
    # We resolve symlinks and '..' components to check the final path
    try:
        resolved_full = os.path.realpath(full_path)
        resolved_base = os.path.realpath(base_path)
        
        if not resolved_full.startswith(resolved_base):
            return "Error: Access Denied (Path Traversal Detected)"
    except Exception:
         return "Error: Invalid Path"

    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            return "Error: Binary file or invalid encoding."
            
    return "Error: File not found."

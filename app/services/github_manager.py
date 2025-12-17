from github import Github, GithubException
import os

def push_to_github(token: str, project_name: str, description: str, is_private: bool, local_path: str):
    try:
        # 1. Authenticate
        g = Github(token)
        user = g.get_user()
        
        # 2. Get or Create Repo
        try:
            repo = user.get_repo(project_name)
            print(f"Repo '{project_name}' exists. Using it.")
        except GithubException:
            repo = user.create_repo(
                name=project_name,
                description=description,
                private=is_private
            )
            print(f"Repo '{project_name}' created.")
        
        # 3. Upload Files
        files_count = 0
        
        if not os.path.exists(local_path):
             return {"status": "error", "message": f"Local path not found: {local_path}"}

        print(f"Pushing files from: {local_path}")

        for root, dirs, files in os.walk(local_path):
            for filename in files:
                # Skip system/git files
                if filename in ['.DS_Store', 'Thumbs.db'] or '.git' in root:
                    continue
                    
                file_path = os.path.join(root, filename)
                
                # Calculate path relative to project root
                # e.g. local_path=/projects/snake, file=/projects/snake/src/main.py -> rel_path=src/main.py
                rel_path = os.path.relpath(file_path, local_path)
                rel_path = rel_path.replace("\\", "/") # Ensure forward slashes for GitHub
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    
                    # Create or Update file
                    try:
                        contents = repo.get_contents(rel_path)
                        repo.update_file(contents.path, f"Update {filename}", content, contents.sha)
                    except GithubException:
                        repo.create_file(rel_path, f"Init {filename}", content)
                    
                    files_count += 1
                except Exception as file_err:
                    print(f"Skipping {filename}: {file_err}")
                    
        if files_count == 0:
             return {"status": "error", "message": f"No files found in {local_path}"}
                
        return {"status": "success", "url": repo.html_url, "files_uploaded": files_count}

    except Exception as e:
        return {"status": "error", "message": str(e)}

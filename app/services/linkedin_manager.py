import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# --- 1. AI Generator Function ---
def generate_linkedin_post(project_name: str, description: str, tech_stack: str, tone: str, llm=None):
    """
    Generates a LinkedIn post using the provided LLM instance.
    """
    try:
        if not llm:
            return "Error: LLM instance not provided."

        prompt = f"""
        Act as a professional copywriter. Write a LinkedIn post for a student developer.
        Project: {project_name}
        Desc: {description}
        Tech: {tech_stack}
        Tone: {tone}
        Reqs: Hook first line, bullets, hashtags, <200 words. Return ONLY text.
        """
        
        # CrewAI LLM object uses .call() or we can invoke it if it's a LangChain object.
        # Since we are passing a crewai.LLM object (which wraps LiteLLM), let's handle it safely.
        
        try:
             # Try standard LangChain/CrewAI invocation
             response = llm.call([{"role": "user", "content": prompt}])
        except:
             # Fallback if it's a raw ChatGoogleGenerativeAI object (langchain)
             response = llm.invoke(prompt).content

        return response.strip()
    except Exception as e:
        return f"AI Generation Failed: {str(e)}"


# --- 2. Posting Function (No Changes Needed) ---
def post_to_linkedin(access_token: str, content: str):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0'
    }

    try:
        # --- STEP 1: Get User ID ---
        oidc_url = "https://api.linkedin.com/v2/userinfo"
        oidc_resp = requests.get(oidc_url, headers=headers)
        
        user_urn = None
        if oidc_resp.status_code == 200:
            user_data = oidc_resp.json()
            user_id = user_data.get('sub')
            user_urn = f"urn:li:person:{user_id}"
        else:
            # Fallback
            me_url = "https://api.linkedin.com/v2/me"
            me_resp = requests.get(me_url, headers=headers)
            if me_resp.status_code == 200:
                user_id = me_resp.json().get('id')
                user_urn = f"urn:li:person:{user_id}"
            else:
                 return {"status": "error", "message": f"Auth Failed: {oidc_resp.text}"}

        # --- STEP 2: Post Content ---
        post_url = "https://api.linkedin.com/v2/ugcPosts"
        
        post_data = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS" 
            }
        }
        
        post_resp = requests.post(post_url, headers=headers, json=post_data)
        
        if post_resp.status_code in [201, 200]:
            return {
                "status": "success", 
                "message": "Posted!", 
                "id": post_resp.json().get("id")
            }
        else:
            return {
                "status": "error", 
                "message": f"LinkedIn Error {post_resp.status_code}: {post_resp.text}"
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}

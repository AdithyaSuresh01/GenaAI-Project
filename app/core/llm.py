import os
from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

# Admin Keys (Fallback)
ADMIN_PERPLEXITY_KEY = os.getenv("PERPLEXITY_API_KEY")
ADMIN_GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def get_llm(user_preference="gemini", user_api_key=None):
    """
    Returns a crewai.LLM instance based on user preference.
    """
    
    # --- OPTION 1: PERPLEXITY (Your Testing setup) ---
    if user_preference == "perplexity":
        api_key = user_api_key or ADMIN_PERPLEXITY_KEY
        
        if not api_key:
             # Fallback logic if needed, or raise error
            if user_api_key or ADMIN_GEMINI_KEY:
                 return get_llm("gemini", user_api_key)
            raise ValueError("Perplexity API Key missing.")

        return LLM(
            model="sonar-pro", 
            base_url="https://api.perplexity.ai",
            api_key=api_key,
            temperature=0.7
        )

    # --- OPTION 2: GEMINI (Deployment / User Key) ---
    else:
        api_key = user_api_key or ADMIN_GEMINI_KEY
        
        if not api_key:
            raise ValueError("Gemini API Key missing. Please add it in Settings.")

        return LLM(
            # Prefix 'gemini/' tells CrewAI/LiteLLM to use the Google provider
            model="gemini/gemini-2.0-flash-exp", 
            api_key=api_key,
            temperature=0.7
        )

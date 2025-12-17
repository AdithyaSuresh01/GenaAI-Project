import sys
import os
import requests
import streamlit as st

# --- PATH SETUP (Must be first) ---
# Add project root to sys.path so we can import from 'frontend'
current_dir = os.path.dirname(os.path.abspath(__file__)) # /frontend
root_dir = os.path.dirname(current_dir)                # /StudentGenAI
sys.path.append(root_dir)

# --- IMPORTS ---
from frontend.utils.api import API_BASE_URL
from frontend.components.auth import render_auth_page
from frontend.components.sidebar import render_sidebar

# Import Views
# Ensure these files exist in your frontend/views/ folder
from frontend.views.roadmap import render_roadmap_page
from frontend.views.chapter import render_chapter_page
from frontend.views.builder import render_builder_page
from frontend.views.social import render_social_page
from frontend.views.debug import render_debug_page
from frontend.views.settings import render_settings_page
from frontend.views.projects import render_projects_page
from frontend.views.survey import render_survey_page
from frontend.views.assessment import render_assessment_page

# --- PAGE CONFIG ---
st.set_page_config(page_title="Student GenAI Platform", layout="wide", page_icon="🎓")

# --- GLOBAL THEME INJECTION ---
def inject_global_css():
    st.markdown("""
    <style>
        /* 1. FORCE DARK BACKGROUND */
        .stApp {
            background-color: #0f0c29 !important;
            background-image: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
            background-attachment: fixed !important;
            background-size: cover !important;
            color: #ffffff !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* 2. HIDE HEADER & FOOTER */
        header[data-testid="stHeader"] { visibility: hidden !important; }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }

        /* 3. INPUT FIELDS (Dark Glass) */
        div[data-baseweb="input"] {
            background-color: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 8px !important;
        }
        input.stTextInput { color: white !important; }
        
        /* Select & Text Area */
        div[data-baseweb="select"] > div, .stTextArea textarea {
            background-color: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 8px !important;
        }
        
        /* Dropdowns */
        ul[data-testid="stSelectboxVirtualDropdown"] {
            background-color: #0f0c29 !important;
        }
        
        /* 4. BUTTONS */
        button[kind="primary"] {
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: 700 !important;
            transition: transform 0.2s !important;
        }
        button[kind="primary"]:hover {
            transform: scale(1.02) !important;
            box-shadow: 0 4px 15px rgba(37, 117, 252, 0.4) !important;
        }
        button[kind="secondary"] {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #e0e0e0 !important;
        }

        /* 5. CONTAINERS */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: rgba(0, 0, 0, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 16px !important;
            backdrop-filter: blur(10px);
        }
        
        /* 6. SPINNER */
        .stSpinner > div { border-top-color: #6a11cb !important; }
    </style>
    """, unsafe_allow_html=True)

inject_global_css()

# --- SESSION STATE INIT ---
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'navigate_to' not in st.session_state:
    st.session_state['navigate_to'] = "Roadmap Generator"

# --- MAIN APP ---
def main():
    # 1. OAUTH RE-LOGIN / SESSION RESTORATION
    query_params = st.query_params
    
    if 'status' in query_params and 'user_id' in query_params:
        if not st.session_state['user']:
            user_id = query_params['user_id']
            try:
                # [FIX] Fetch ACTUAL profile so we know if they have data
                resp = requests.get(f"{API_BASE_URL}/user/{user_id}")
                
                if resp.status_code == 200:
                    user_data = resp.json()
                    st.session_state['user'] = {
                        "id": int(user_id), 
                        "name": user_data.get("name", "User"), 
                        "email": user_data.get("email", ""),
                        "profile_data": user_data.get("profile_data", {}) # Now accurate
                    }
                    
                    # Redirect logic: If profile empty -> Survey, else -> Roadmap
                    if not user_data.get("profile_data"):
                         st.session_state['navigate_to'] = "Settings" # or Survey
                    else:
                         st.session_state['navigate_to'] = "Roadmap Generator"
                         
            except Exception as e:
                st.error(f"Failed to restore session: {e}")

    # 2. AUTH CHECK
    if not st.session_state['user']:
        render_auth_page()
        return

    # 3. SURVEY CHECK (Force onboarding if profile is empty)
    user_profile = st.session_state['user'].get('profile_data')
    survey_just_finished = st.session_state.get('survey_completed_flag', False)
    
    if not user_profile and not survey_just_finished:
        render_survey_page()
        return 

    # 4. RENDER APP
    render_sidebar()

    page = st.session_state['navigate_to']

    if page == "Roadmap Generator": render_roadmap_page()
    elif page == "Study Chapter": render_chapter_page()
    elif page == "AI Project Builder": render_builder_page()
    elif page == "My Projects": render_projects_page()
    elif page == "Career & Social": render_social_page()
    elif page == "Code Debugger": render_debug_page()
    elif page == "Assessment Center": render_assessment_page()
    elif page == "Settings": render_settings_page()
    else: st.error(f"Page '{page}' not found.")

if __name__ == "__main__":
    main()

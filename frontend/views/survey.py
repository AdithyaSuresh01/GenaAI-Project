import streamlit as st
import requests
from frontend.utils.api import API_BASE_URL

def render_survey_page():
    # --- HEADER STYLE ---
    st.markdown("""
    <style>
        h1 {
            background: linear-gradient(90deg, #FF9966 0%, #FF5E62 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            text-align: center;
        }
        .survey-subtitle {
            text-align: center;
            color: #a0a0a0;
            margin-bottom: 40px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🧠 Personalize Your AI Tutor</h1>", unsafe_allow_html=True)
    st.markdown("<p class='survey-subtitle'>Help us tailor the roadmap, quizzes, and project suggestions to your unique brain.</p>", unsafe_allow_html=True)
    
    # Ensure user exists in state
    if 'user' not in st.session_state or not st.session_state['user']:
        st.error("Please log in first.")
        return

    user = st.session_state['user']
    
    # --- CENTERED GLASS CARD ---
    col_l, col_m, col_r = st.columns([1, 2, 1])
    
    with col_m:
        with st.container(border=True):
            with st.form("survey_form", border=False):
                st.subheader("Your Profile")
                
                col1, col2 = st.columns(2)
                with col1:
                    style = st.selectbox(
                        "Learning Style", 
                        ["Visual (Videos/Diagrams)", "Textual (Documentation)", "Hands-on (Projects)", "Auditory (Lectures)"]
                    )
                    time = st.select_slider("Daily Commitment", options=["30m", "1h", "2h", "4h+"])
                
                with col2:
                    goal = st.text_input("Career Goal", placeholder="e.g. AI Researcher at DeepMind")
                    skill = st.select_slider("Current Skill Level", options=["Novice", "Competent", "Proficient", "Expert"])
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("🚀 Start My Journey", type="primary", use_container_width=True)
                
                if submitted:
                    if not goal:
                         st.warning("Please define a career goal.")
                    else:
                        payload = {
                            "user_id": user['id'],
                            "learning_style": style,
                            "daily_time": time,
                            "career_goal": goal,
                            "current_skill": skill
                        }
                        
                        try:
                            with st.spinner("Calibrating AI..."):
                                resp = requests.post(f"{API_BASE_URL}/save-survey", json=payload)
                            
                            if resp.status_code == 200:
                                st.balloons()
                                st.success("Profile Updated!")
                                
                                # --- CRITICAL FIX: Update Local Session State ---
                                st.session_state['user']['profile_data'] = payload
                                st.session_state['survey_completed_flag'] = True
                                st.session_state['navigate_to'] = "Roadmap Generator"
                                
                                st.rerun()
                            else:
                                st.error(f"Failed to save: {resp.text}")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")

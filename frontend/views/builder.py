import streamlit as st
import requests
import time
from frontend.utils.api import API_BASE_URL

def render_builder_page():
    # --- HEADER ---
    st.markdown("""
    <style>
        h1 {
            background: linear-gradient(90deg, #ff00cc 0%, #333399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)
    st.title("🏗️ Project Architect")
    st.markdown("<p style='color: #a0a0a0;'>Describe your dream app, and our AI agents will build the folder structure and code for you.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # --- USER CONTEXT ---
    user = st.session_state.get('user')
    if not user:
        st.error("Please login to use the Builder.")
        return

    # --- SESSION STATE ---
    if 'build_completed' not in st.session_state:
        st.session_state['build_completed'] = False

    # --- GLASS CARD FORM ---
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            project_name = st.text_input("Project Name", value="My New App", placeholder="e.g. Snake Game", key="input_builder_name")
        with col2:
            difficulty = st.selectbox("Complexity Level", ["Beginner (Script)", "Intermediate (App)", "Advanced (Full Stack)"], index=1, key="input_builder_diff")

        d_prompt = st.session_state.get('builder_prompt', "")
        prompt = st.text_area("What do you want to build?", value=d_prompt, height=150, 
                            placeholder="E.g., A real-time chat application using Python, Streamlit and SQLite...", 
                            key="input_builder_desc")
        
        d_tech = st.session_state.get('builder_tech', "Python, Streamlit")
        tech = st.text_input("Preferred Tech Stack", value=d_tech, key="input_builder_tech", placeholder="e.g. React, Node.js or Python, Flask")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- ACTION BUTTON ---
    if st.button("🚀 Initialize Agents & Build", type="primary"):
        st.session_state['build_completed'] = False
        
        # Validation
        if not prompt or len(prompt) < 10:
            st.warning("Please provide a more detailed description (at least 10 chars).")
        else:
            try:
                # Prepend name to description so backend agents see it easily
                full_desc = f"Project Name: {project_name}. Description: {prompt}"
                
                payload = {
                    "user_id": user['id'],
                    "description": full_desc, 
                    "technology": tech,
                    "difficulty": difficulty
                }
                
                # 1. Trigger Build
                with st.spinner("🤖 Waking up the dev team..."):
                    resp = requests.post(f"{API_BASE_URL}/generate-project", json=payload)
                
                if resp.status_code == 200:
                    # 2. Polling Loop
                    st.success("Agents are working! Watch the progress below.")
                    
                    progress_bar = st.progress(0)
                    status_area = st.empty()
                    log_area = st.empty()
                    
                    # Poll for up to 90 seconds
                    for _ in range(90):
                        try:
                            status_resp = requests.get(f"{API_BASE_URL}/project-status/{user['id']}")
                            if status_resp.status_code == 200:
                                data = status_resp.json()
                                
                                # Update UI
                                progress = data.get('progress', 0)
                                step_name = data.get('step', 'Processing...')
                                status = data.get('status', 'processing')
                                
                                progress_bar.progress(progress)
                                status_area.info(f"⚙️ {step_name}")
                                
                                if status == 'completed':
                                    progress_bar.progress(100)
                                    status_area.success(f"✅ Project '{project_name}' Built Successfully!")
                                    st.balloons()
                                    st.session_state['build_completed'] = True
                                    
                                    # Show link to projects page
                                    st.markdown(f"""
                                    <div style='background: rgba(0,255,0,0.1); padding: 15px; border-radius: 10px; border: 1px solid #00ff00;'>
                                        <h4>🚀 Ready to Deploy!</h4>
                                        <p>Your project files have been generated.</p>
                                    </div>
                                    """, unsafe_allow_html=True)
                                    
                                    if st.button("📂 Go to My Projects"):
                                        st.session_state['navigate_to'] = "My Projects"
                                        st.rerun()
                                    break
                                
                                elif status == 'error':
                                    status_area.error(f"❌ Build Failed: {step_name}")
                                    break
                            
                        except requests.exceptions.ConnectionError:
                            pass # Retry silently
                            
                        time.sleep(1.5) # Wait before next poll
                        
                else:
                    st.error(f"Failed to start build: {resp.text}")
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")

    # --- SUCCESS STATE ---
    if st.session_state.get('build_completed'):
        st.info("💡 Tip: Navigate to the 'My Projects' tab to view code and file structure.")

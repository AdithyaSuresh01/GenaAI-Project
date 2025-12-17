import streamlit as st
import requests
from frontend.utils.helpers import extract_json
from frontend.utils.api import API_BASE_URL

# --- Callbacks ---
def go_to_study(topic, subtopics_list):
    st.session_state['selected_topic'] = topic
    st.session_state['selected_subtopics'] = ", ".join(subtopics_list)
    st.session_state['navigate_to'] = "Study Chapter" 

def go_to_builder(project_desc, tech):
    st.session_state['builder_prompt'] = project_desc
    st.session_state['builder_tech'] = tech
    st.session_state['navigate_to'] = "AI Project Builder"

def go_to_assessment(week_topic):
    st.session_state['assessment_prefill_topic'] = week_topic
    st.session_state['data_quiz'] = None
    st.session_state['navigate_to'] = "Assessment Center"

def render_roadmap_page():
    # --- HEADER STYLE ---
    st.markdown("""
    <style>
        .roadmap-header {
            background: linear-gradient(90deg, #a855f7 0%, #3b82f6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)

    # Safety Init
    if 'generated_roadmap' not in st.session_state:
        st.session_state['generated_roadmap'] = False
    if 'roadmap_data' not in st.session_state:
        st.session_state['roadmap_data'] = None
        
    st.markdown('<h1 class="roadmap-header">🗺️ Personalized Learning Path</h1>', unsafe_allow_html=True)
    st.markdown("<p style='color: #a0a0a0;'>Generate a custom curriculum tailored to your goals and skill level.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- INPUT SECTION (Glass Card) ---
    with st.container(border=True): 
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            topic = st.text_input("I want to master...", "Python for Data Science", key="roadmap_topic_input")
        with col2:
            level = st.selectbox("My Level", ["Beginner", "Intermediate", "Advanced"], key="roadmap_level_input")
        with col3:
            duration = st.selectbox("Timeline", ["2 weeks", "4 weeks", "8 weeks"], key="roadmap_duration_input")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Generate My Roadmap", type="primary", use_container_width=True):
            if not st.session_state.get('user'):
                 st.error("Please login first.")
            else:
                with st.spinner("🤖 Agents are designing your curriculum..."):
                    try:
                        user_id = st.session_state['user']['id']
                        payload = {"user_id": user_id, "topic": topic, "duration": duration, "level": level}
                        
                        # API Call
                        response = requests.post(f"{API_BASE_URL}/generate-roadmap", json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            # Handle both direct JSON or stringified JSON in 'roadmap' field
                            if isinstance(data, dict) and "roadmap" in data:
                                raw_text = data["roadmap"]
                                # If it's already a dict/list, use it. If string, parse it.
                                if isinstance(raw_text, (dict, list)):
                                     roadmap_json = raw_text
                                else:
                                     roadmap_json = extract_json(raw_text)
                            else:
                                roadmap_json = data # Fallback

                            if roadmap_json:
                                st.session_state['roadmap_data'] = roadmap_json 
                                st.session_state['generated_roadmap'] = True
                                st.rerun() 
                            else:
                                st.warning("Parsed output is empty. Try again.")
                        else:
                            st.error(f"Server Error: {response.text}")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

    # --- RENDER WEEKS ---
    if st.session_state['generated_roadmap'] and st.session_state['roadmap_data']:
        # Support both structure types: {"roadmap": [...]} or just [...]
        r_data = st.session_state['roadmap_data']
        weeks = r_data.get("roadmap", []) if isinstance(r_data, dict) else r_data
        
        if not weeks:
             st.info("No roadmap data found.")
        else:
            st.markdown("<br>", unsafe_allow_html=True)
            
            for i, week in enumerate(weeks):
                # Handle variations in LLM output keys
                title = week.get('title', f'Week {i+1}')
                desc = week.get('description', '')
                topics = week.get('topics', [])
                project = week.get('project', 'No project assigned.')
                week_num = week.get('week', i+1)

                with st.expander(f"📆 Week {week_num}: {title}", expanded=True):
                    st.markdown(f"_{desc}_")
                    st.markdown("---")
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        st.markdown("#### 📖 Key Topics")
                        for t in topics:
                            st.markdown(f"• {t}")
                            
                    with c2:
                        st.markdown("#### 🛠️ Mini-Project")
                        project_text = project.replace("\n", "  \n")
                        st.info(project_text)
                        
                    st.markdown("---")
                    
                    # --- ACTION BUTTONS ---
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.button(f"📚 Study", key=f"learn_{i}", 
                                 on_click=go_to_study, args=(title, topics), use_container_width=True)
                    with col_b:
                        st.button(f"🏗️ Build", key=f"build_{i}", 
                                 on_click=go_to_builder, args=(project, topic), use_container_width=True)
                    with col_c:
                        st.button(f"📝 Quiz", key=f"test_{i}", 
                                 on_click=go_to_assessment, args=(title,), use_container_width=True)

            # --- DOWNLOAD SECTION ---
            st.markdown("<br><hr>", unsafe_allow_html=True)
            col_dl, col_sp = st.columns([1, 2])
            with col_dl:
                if st.button("📥 Download Roadmap PDF", type="secondary", use_container_width=True):
                    with st.spinner("Generating PDF..."):
                        payload = {
                            "topic": topic,
                            "duration": duration,
                            "data": st.session_state['roadmap_data']
                        }
                        try:
                            # Try specific route first, then generic
                            resp = requests.post(f"{API_BASE_URL}/roadmap/download-pdf", json=payload)
                            
                            if resp.status_code == 404:
                                 resp = requests.post(f"{API_BASE_URL}/download-pdf", json=payload)

                            if resp.status_code == 200:
                                st.download_button(
                                    label="📄 Click to Save PDF",
                                    data=resp.content,
                                    file_name=f"Roadmap_{topic}.pdf",
                                    mime="application/pdf",
                                    use_container_width=True,
                                    type="primary"
                                )
                            else:
                                st.error(f"Failed to generate PDF: {resp.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")

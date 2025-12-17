import streamlit as st
import requests
from frontend.utils.api import API_BASE_URL

def render_chapter_page():
    # --- HEADER STYLE ---
    st.markdown("""
    <style>
        h1 {
            background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)

    st.title("📚 AI Study Tutor")
    st.markdown("<p style='color: #a0a0a0;'>Generate deep-dive study materials and explanations for any topic.</p>", unsafe_allow_html=True)
    
    # --- CHECK LOGIN ---
    user = st.session_state.get('user')
    if not user:
        st.error("Please login to use the Tutor.")
        return

    # --- SESSION STATE INIT ---
    if 'generated_chapter' not in st.session_state:
        st.session_state['generated_chapter'] = ""
    if 'chapter_topic' not in st.session_state:
        st.session_state['chapter_topic'] = ""
    
    # --- CONTEXT FROM ROADMAP ---
    pre_topic = st.session_state.get('selected_topic', "Python Generators")
    pre_subtopics = st.session_state.get('selected_subtopics', "")
    
    # --- INPUT SECTION (Glass Card) ---
    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            topic = st.text_input("Main Topic", value=pre_topic, placeholder="e.g. Neural Networks", key="chapter_topic_input")
        with col2:
            detail_level = st.selectbox("Depth", ["Beginner", "Intermediate", "Advanced", "Research Paper"], index=1, key="chapter_detail_input")
            
        subtopics_str = st.text_area("Specific Concepts (Optional)", value=pre_subtopics, height=100, 
                                   placeholder="e.g. Backpropagation, Activation Functions, Loss Landscapes", key="chapter_subs_input")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- GENERATE BUTTON ---
    if st.button("🎓 Generate Lesson", type="primary", use_container_width=True):
        with st.spinner("🤖 The Professor is writing your study material..."):
            try:
                # Prepare subtopics list
                subtopics_list = [s.strip() for s in subtopics_str.split(',') if s.strip()]
                
                payload = {
                    "user_id": user['id'],
                    "topic": topic,
                    "subtopics": subtopics_list,
                    "detail_level": detail_level
                }
                
                # API Call
                resp = requests.post(f"{API_BASE_URL}/generate-chapter", json=payload)
                
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state['generated_chapter'] = data.get('content', '')
                    st.session_state['chapter_topic'] = topic
                elif resp.status_code == 429:
                    st.error("⏳ Rate Limit Reached. Please wait a minute.")
                else:
                    st.error(f"Error: {resp.text}")
                    
            except Exception as e:
                st.error(f"Connection Error: {e}")

    # --- DISPLAY CONTENT ---
    if st.session_state['generated_chapter']:
        st.markdown("---")
        st.subheader(f"📖 {st.session_state['chapter_topic']}")
        
        # Content Glass Container
        with st.container(border=True):
            st.markdown(st.session_state['generated_chapter'])
            
        # Download Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📥 Download Chapter as PDF", type="secondary", use_container_width=True):
             with st.spinner("Generating PDF..."):
                try:
                    pdf_payload = {
                        "topic": st.session_state['chapter_topic'],
                        "content": st.session_state['generated_chapter']
                    }
                    # Note: Using /chapter/download-pdf based on your API router prefix
                    pdf_resp = requests.post(f"{API_BASE_URL}/chapter/download-pdf", json=pdf_payload)
                    
                    if pdf_resp.status_code == 200:
                         st.download_button(
                            label="📄 Click to Save PDF",
                            data=pdf_resp.content,
                            file_name=f"Study_Chapter_{st.session_state['chapter_topic']}.pdf",
                            mime="application/pdf",
                            type="primary",
                            use_container_width=True
                        )
                    else:
                        st.error("Failed to generate PDF")
                except Exception as e:
                    st.error(f"PDF Error: {e}")
    elif not st.session_state['generated_chapter']:
        st.info("👈 Enter a topic above and click 'Generate Lesson' to start learning!")

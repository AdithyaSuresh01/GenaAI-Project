import streamlit as st
import requests
from frontend.utils.api import API_BASE_URL

def render_debug_page():
    # --- HEADER ---
    st.markdown("""
    <style>
        h1 {
            background: linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)
    st.title("🐛 AI Debugger")
    st.markdown("<p style='color: #a0a0a0;'>Paste your broken code, and our AI agents will find the bug and explain the fix.</p>", unsafe_allow_html=True)
    
    # --- CHECK LOGIN ---
    if not st.session_state.get('user'):
        st.error("Please login to use the debugger.")
        return

    # --- SESSION STATE ---
    if 'debug_solution' not in st.session_state:
        st.session_state['debug_solution'] = ""

    # --- GLASS CARD INPUTS ---
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            code = st.text_area("Broken Code", height=300, key="debug_code_input", placeholder="Paste code here...")
        with col2:
            err = st.text_area("Error Message (Optional)", height=300, key="debug_error_input", placeholder="Paste traceback or describe the issue...")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- FIX BUTTON ---
        if st.button("🔧 Fix My Code", type="primary", use_container_width=True):
            if not code:
                 st.warning("Please enter some code.")
            else:
                with st.spinner("🕵️ Agents are analyzing the stack trace..."):
                    try:
                        user_id = st.session_state['user']['id']
                        payload = {
                            "user_id": user_id,
                            "code_snippet": code, 
                            "error_message": err or "Find the bug and fix it."
                        }
                        
                        # API Call
                        response = requests.post(f"{API_BASE_URL}/debug", json=payload, timeout=30)
                        
                        if response.status_code == 200:
                            st.session_state['debug_solution'] = response.json().get("solution", "No solution returned.")
                            # Removed rerun to avoid clearing inputs if not needed, but can add if desired
                        else:
                            st.error(f"Error: {response.text}")
                            
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

    # --- RESULTS SECTION ---
    if st.session_state['debug_solution']:
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("💡 AI Solution")
        
        with st.container(border=True):
            st.markdown(st.session_state['debug_solution'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- DOWNLOAD BUTTON ---
        col_d, col_s = st.columns([1, 2])
        with col_d:
            if st.button("📥 Download Report PDF", type="secondary", use_container_width=True):
                with st.spinner("Generating PDF..."):
                    pdf_payload = {
                        "code": code,
                        "error": err,
                        "solution": st.session_state['debug_solution']
                    }
                    try:
                        resp = requests.post(f"{API_BASE_URL}/debug/download-pdf", json=pdf_payload)
                        
                        if resp.status_code == 200:
                            st.download_button(
                                label="📄 Save PDF Report",
                                data=resp.content,
                                file_name="Debug_Report.pdf",
                                mime="application/pdf",
                                type="primary",
                                use_container_width=True
                            )
                        else:
                            st.error("Failed to generate PDF")
                    except Exception as e:
                        st.error(f"Connection Error: {e}")

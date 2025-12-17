import streamlit as st
import requests
from frontend.utils.api import API_BASE_URL

def render_settings_page():
    # --- HEADER ---
    st.markdown("""
    <style>
        h1 {
            background: linear-gradient(90deg, #A18CD1 0%, #FBC2EB 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)
    st.title("⚙️ Settings & Integrations")
    
    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    # --- FETCH CURRENT KEYS ---
    # We need to know if they already have a key to show placeholders
    current_gemini_key = ""
    current_model = "gemini"
    gh_connected = False
    li_connected = False

    try:
        resp = requests.get(f"{API_BASE_URL}/user/{user['id']}/keys")
        if resp.status_code == 200:
            data = resp.json()
            current_gemini_key = data.get("gemini_api_key") or ""
            current_model = data.get("preferred_model") or "gemini"
            if data.get("github_token"): gh_connected = True
            if data.get("linkedin_token"): li_connected = True
    except:
        pass

    # --- SECTION 1: AI CONFIGURATION ---
    st.subheader("🧠 AI Model Configuration")
    
    with st.container(border=True):
        col_model, col_key = st.columns([1, 2])
        
        with col_model:
            # Dropdown to choose model
            model_choice = st.selectbox(
                "Preferred Intelligence Engine", 
                ["gemini", "perplexity"], 
                index=0 if current_model == "gemini" else 1,
                help="Gemini is faster and free. Perplexity is better for web research."
            )
            
        with col_key:
            # Input for API Key
            # We show a placeholder if a key exists so we don't reveal it
            placeholder = "••••••••••••••••" if current_gemini_key else "Enter Gemini API Key"
            api_key_input = st.text_input(
                "Gemini API Key", 
                type="password", 
                placeholder=placeholder,
                help="Required if you select Gemini. Get it from Google AI Studio."
            )

        if st.button("💾 Save AI Settings", type="primary"):
            payload = {
                "user_id": user['id'],
                "preferred_model": model_choice
            }
            # Only update key if user typed something new
            if api_key_input:
                payload["gemini_api_key"] = api_key_input
            
            try:
                resp = requests.post(f"{API_BASE_URL}/user/update-keys", json=payload)
                if resp.status_code == 200:
                    st.toast("AI Configuration Saved!", icon="✅")
                    # Update local state slightly to reflect change immediately if needed
                else:
                    st.error(f"Failed to save: {resp.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- SECTION 2: SOCIAL INTEGRATIONS ---
    st.subheader("🔌 External Accounts")
    
    # Check for OAuth redirects
    if "status" in st.query_params:
        status = st.query_params["status"]
        if status == "success_gh":
            st.toast("GitHub Connected!", icon="🐙")
        elif status == "success_li":
            st.toast("LinkedIn Connected!", icon="🔵")
        # Clear params logic if desired

    OAUTH_BASE_URL = API_BASE_URL.replace("/api/v1", "/api/oauth")
    
    col1, col2 = st.columns(2)

    # GITHUB CARD
    with col1:
        with st.container(border=True):
            st.markdown("##### 🐙 GitHub")
            if gh_connected:
                st.markdown("<p style='color:#00ff00; font-size: 0.9em;'>✅ Connected</p>", unsafe_allow_html=True)
                login_url = f"{OAUTH_BASE_URL}/github/login?user_id={user['id']}"
                st.link_button("🔄 Reconnect", login_url, use_container_width=True)
            else:
                st.markdown("<p style='color:#ff4b4b; font-size: 0.9em;'>❌ Not Connected</p>", unsafe_allow_html=True)
                login_url = f"{OAUTH_BASE_URL}/github/login?user_id={user['id']}"
                st.link_button("🔗 Connect", login_url, use_container_width=True)

    # LINKEDIN CARD
    with col2:
        with st.container(border=True):
            st.markdown("##### 🔵 LinkedIn")
            if li_connected:
                st.markdown("<p style='color:#00ff00; font-size: 0.9em;'>✅ Connected</p>", unsafe_allow_html=True)
                login_url = f"{OAUTH_BASE_URL}/linkedin/login?user_id={user['id']}"
                st.link_button("🔄 Reconnect", login_url, use_container_width=True)
            else:
                st.markdown("<p style='color:#ff4b4b; font-size: 0.9em;'>❌ Not Connected</p>", unsafe_allow_html=True)
                login_url = f"{OAUTH_BASE_URL}/linkedin/login?user_id={user['id']}"
                st.link_button("🔗 Connect", login_url, use_container_width=True)

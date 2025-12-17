import streamlit as st
import requests
from frontend.utils.api import API_BASE_URL

def render_auth_page():
    # --- MODERN CSS STYLING (Kept exactly as you provided) ---
    st.markdown("""
    <style>
        /* 1. Global Background & Reset */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        .stApp {
            background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #1a1a2e);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            font-family: 'Inter', sans-serif;
            overflow: hidden; 
        }
        
        .block-container {
            padding-top: 5rem !important;
            padding-bottom: 0rem !important;
            max-width: 100% !important;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* 2. Hide ALL Default Elements */
        #MainMenu {visibility: hidden;}
        footer {display: none !important;} 
        header {visibility: hidden;}
        div[data-testid="stStatusWidget"] {visibility: hidden;}

        /* 3. The Glass Card Container */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }

        /* 4. Tabs Styling */
        div[data-testid="stTabs"] button {
            background-color: transparent;
            color: #a0a0a0;
            font-weight: 600;
            font-size: 16px;
            border-radius: 5px;
            transition: all 0.3s;
        }
        div[data-testid="stTabs"] button[aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border-bottom: 2px solid #6a11cb;
        }

        /* 5. Input Fields */
        .stTextInput > div > div > input {
            background-color: rgba(0, 0, 0, 0.2) !important;
            color: white !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 10px !important;
            padding: 10px 15px !important;
        }
        .stTextInput > div > div > input:focus {
            border-color: #6a11cb !important;
            box-shadow: 0 0 10px rgba(106, 17, 203, 0.3) !important;
        }
        .stTextInput label p {
            color: #d1d5db !important;
            font-size: 14px;
        }

        /* 6. Neon Buttons */
        div.stButton > button {
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
            color: white !important;
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease !important;
            width: 100%;
            box-shadow: 0 4px 15px rgba(37, 117, 252, 0.3) !important;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(37, 117, 252, 0.6) !important;
        }

        /* 7. Typography */
        h1 {
            background: linear-gradient(to right, #ffffff, #a5b4fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-weight: 800;
            margin-bottom: 0px;
        }
        p {
            color: #94a3b8;
            text-align: center;
            font-size: 14px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- LAYOUT LOGIC ---
    col1, col2, col3 = st.columns([1, 1.5, 1]) 
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # --- THE GLASS CARD ---
        with st.container(border=True):
            
            # Header
            st.markdown("<h1>🎓 Student GenAI</h1>", unsafe_allow_html=True)
            st.markdown("<p>Your AI-Powered Learning Competitor</p>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Add Google Login Button Here (Optional, if you have the URL)
            # st.markdown(f'<a href="{API_BASE_URL}/oauth/login/google" target="_self"><button>Login with Google</button></a>', unsafe_allow_html=True)

            # Tabs
            tab_login, tab_signup = st.tabs(["🔐 Login", "✨ Sign Up"])
            
            # --- LOGIN TAB ---
            with tab_login:
                with st.form("login_form", border=False):
                    st.markdown("<br>", unsafe_allow_html=True)
                    email = st.text_input("Email", key="login_email", placeholder="student@example.com")
                    password = st.text_input("Password", type="password", key="login_pass", placeholder="••••••••")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    submitted = st.form_submit_button("Access Dashboard")
                    
                    if submitted:
                        if not email or not password:
                            st.warning("Please fill in all fields.")
                        else:
                            try:
                                resp = requests.post(f"{API_BASE_URL}/login", json={"email": email, "password": password})
                                if resp.status_code == 200:
                                    user_data = resp.json()
                                    
                                    # Save User Session
                                    st.session_state['user'] = {
                                        "id": user_data["user_id"],
                                        "name": user_data["name"],
                                        "email": user_data["email"],
                                        "profile_data": user_data.get("profile_data") 
                                    }
                                    
                                    st.toast(f"Welcome back, {user_data['name']}!", icon="🚀")
                                    
                                    # [LOGIC FIX] Check if profile exists to determine next page
                                    if user_data.get("profile_data"):
                                        st.session_state['navigate_to'] = "Roadmap Generator"
                                    else:
                                        # Force survey if no profile data
                                        st.session_state['navigate_to'] = "Settings" 
                                    
                                    st.rerun()
                                else:
                                    st.error(f"Login failed: {resp.json().get('detail', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Connection Error: {e}")

            # --- SIGNUP TAB ---
            with tab_signup:
                with st.form("signup_form", border=False):
                    st.markdown("<br>", unsafe_allow_html=True)
                    new_name = st.text_input("Full Name", key="reg_name", placeholder="John Doe")
                    new_email = st.text_input("Email", key="reg_email", placeholder="john@example.com")
                    new_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="••••••••")
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    reg_sub = st.form_submit_button("Create Account")
                    
                    if reg_sub:
                        if not new_name or not new_email or not new_pass:
                            st.warning("All fields are required.")
                        else:
                            try:
                                payload = {"email": new_email, "password": new_pass, "full_name": new_name}
                                resp = requests.post(f"{API_BASE_URL}/signup", json=payload)
                                if resp.status_code == 200:
                                    st.success("✅ Account created! Please switch to Login.")
                                    st.balloons()
                                else:
                                    st.error(f"Error: {resp.text}")
                            except Exception as e:
                                st.error(f"Connection Error: {e}")

        # Footer
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style='text-align: center; color: #64748b; font-size: 12px;'>
                Powered by CrewAI & Gemini Pro<br>
                For Demo: [user@vit.ac.in](mailto:user@vit.ac.in) / password123
            </div>
            """, 
            unsafe_allow_html=True
        )

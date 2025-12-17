import streamlit as st
from streamlit_option_menu import option_menu

def render_sidebar():
    # --- SAFETY CHECK ---
    if 'navigate_to' not in st.session_state:
        st.session_state['navigate_to'] = "Roadmap Generator"

    # --- CSS OVERRIDES ---
    st.markdown("""
    <style>
        /* 1. Force Sidebar Background (Dark Purple) */
        [data-testid="stSidebar"] {
            background-color: #0f0c29 !important;
            background-image: linear-gradient(180deg, #0f0c29 0%, #24243e 100%) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* 2. AGGRESSIVE OPTION MENU OVERRIDE */
        iframe[title="streamlit_option_menu.option_menu"] {
            background-color: transparent !important;
        }
        
        div[data-testid="stSidebarUserContent"] .nav-link-selected {
            background-color: #6a11cb !important;
        }

        /* 3. LOGOUT BUTTON STYLING */
        [data-testid="stSidebar"] button[kind="secondary"] {
            background: transparent !important;
            border: 1px solid #6a11cb !important;
            color: #ffffff !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stSidebar"] button[kind="secondary"]:hover {
            background: linear-gradient(90deg, #6a11cb 0%, #2575fc 100%) !important;
            border-color: transparent !important;
            box-shadow: 0 4px 15px rgba(37, 117, 252, 0.4) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- MENU DEFINITIONS ---
    page_map = {
        "Roadmap": "Roadmap Generator",
        "Tutor": "Study Chapter",
        "Builder": "AI Project Builder",
        "Projects": "My Projects",
        "Social": "Career & Social",
        "Debug": "Code Debugger",
        "Assessment": "Assessment Center",
        "Settings": "Settings"
    }
    
    reverse_map = {v: k for k, v in page_map.items()}
    current_page = st.session_state.get('navigate_to', "Roadmap Generator")
    current_short_name = reverse_map.get(current_page, "Roadmap")
    
    menu_options = list(page_map.keys())
    try:
        default_ix = menu_options.index(current_short_name)
    except ValueError:
        default_ix = 0

    with st.sidebar:
        # --- USER PROFILE HEADER ---
        if st.session_state.get('user'):
            user = st.session_state['user']
            # Fallback for name if missing
            safe_name = user.get('name', 'User') or 'User'
            first_char = safe_name[0].upper() if safe_name else "U"

            st.markdown(f"""
            <div style="
                display: flex; align-items: center; gap: 12px; padding: 15px 10px; 
                background: rgba(255, 255, 255, 0.05); border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 30px;
            ">
                <div style="
                    background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); 
                    color: white; width: 40px; height: 40px; border-radius: 50%; 
                    display: flex; align-items: center; justify-content: center; font-weight: bold;
                ">
                    {first_char}
                </div>
                <div style="overflow: hidden;">
                    <div style="font-weight: 600; color: white; font-size: 14px;">{safe_name}</div>
                    <div style="font-size: 11px; color: #a0a0a0;">{user.get('email', '')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- NAVIGATION MENU ---
        selected = option_menu(
            menu_title=None,
            options=menu_options,
            icons=["map", "book", "tools", "folder", "share", "bug", "clipboard-check", "gear"], 
            menu_icon="cast",
            default_index=default_ix, 
            key=f"nav_menu_sidebar", # Fixed key to prevent recreation issues
            styles={
                "container": {
                    "padding": "0!important", 
                    "background-color": "#0f0c29"  
                },
                "icon": {"color": "#a0a0a0", "font-size": "16px"}, 
                "nav-link": {
                    "font-size": "14px", "text-align": "left", "margin": "5px 0px", 
                    "color": "#e0e0e0", "border-radius": "8px", "padding": "10px 15px",
                    "background-color": "transparent"
                },
                "nav-link-selected": {
                    "background": "linear-gradient(90deg, #6a11cb 0%, #2575fc 100%)", 
                    "color": "white", "font-weight": "600",
                },
            }
        )
        
        # Navigation Logic
        if st.session_state.get('last_selected') != selected:
            st.session_state['navigate_to'] = page_map[selected]
            st.session_state['last_selected'] = selected
            st.rerun()
        
        # --- LOGOUT BUTTON ---
        st.markdown("<div style='margin-top: 50px;'></div>", unsafe_allow_html=True)
        
        if st.button("Logout", key="logout_btn", type="secondary"): 
            st.session_state['user'] = None
            # Clear all session data
            st.session_state.clear() 
            # Re-init minimal state
            st.session_state['navigate_to'] = "Roadmap Generator"
            st.rerun()

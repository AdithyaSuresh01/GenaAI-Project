import streamlit as st
import requests
import os
from frontend.utils.api import API_BASE_URL
from frontend.utils.helpers import get_projects

# --- HELPER: READ README ---
# NOTE: In production, use an API call. For local dev, direct file access is used.
def get_readme_content(user_id, project_name):
    """Reads the README.md from the project folder."""
    try:
        # Construct path relative to where the script runs
        path = os.path.join(os.getcwd(), "generated_projects", f"user_{user_id}", project_name, "README.md")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Error reading readme: {e}")
    return None

# --- CALLBACKS ---
def update_gh_fields():
    user = st.session_state['user']
    # Safety check: ensure key exists
    if 'social_gh_project_selection' not in st.session_state:
        return

    proj = st.session_state['social_gh_project_selection']
    
    # Clean Name for Repo
    clean_name = proj.replace(" ", "-").replace("_", "-").lower()
    st.session_state['social_gh_reponame'] = clean_name
    
    # READ README for Description
    readme = get_readme_content(user['id'], proj)
    
    if readme:
        # Extract a short description (first meaningful line)
        lines = [l.strip() for l in readme.split('\n') if l.strip()]
        desc = "AI Generated Project"
        for line in lines:
            # Skip headers or badges
            if not line.startswith("#") and not line.startswith("[!") and len(line) > 20:
                desc = line
                break
        st.session_state['social_gh_desc'] = desc[:250]
    else:
        st.session_state['social_gh_desc'] = f"Full-stack AI project: {proj}."

def auto_fill_linkedin():
    user = st.session_state['user']
    proj = st.session_state['social_li_project_selector']
    
    st.session_state['social_li_topic'] = proj
    
    readme = get_readme_content(user['id'], proj)
    
    if readme:
        # Load the README (truncated) into the context box
        st.session_state['social_li_desc'] = readme[:1500]
    else:
        st.session_state['social_li_desc'] = f"A project named {proj}."

def render_social_page():
    # --- HEADER STYLE ---
    st.markdown("""
    <style>
        h1 {
            background: linear-gradient(90deg, #0077B5 0%, #000000 100%); /* LinkedIn Blue to Black */
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("🚀 Career & Social Hub")
    
    user = st.session_state.get('user')
    if not user:
        st.error("Please login to access social features.")
        return

    # --- INIT STATE ---
    if 'social_li_topic' not in st.session_state: st.session_state['social_li_topic'] = ""
    if 'social_li_desc' not in st.session_state: st.session_state['social_li_desc'] = ""
    
    if 'social_gh_reponame' not in st.session_state: st.session_state['social_gh_reponame'] = ""
    if 'social_gh_desc' not in st.session_state: st.session_state['social_gh_desc'] = ""

    # Determine Active View (Handle navigation from Projects Page)
    active_view = st.session_state.get('social_active_tab', "linkedin")
    view_index = 1 if active_view == "github" else 0
    
    # Custom Radio styling handled by Dashboard CSS, just need layout
    selected_view = st.radio(
        "Choose Action:", 
        ["🔵 LinkedIn Automation", "🐙 GitHub Repo Manager"], 
        index=view_index,
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("<br>", unsafe_allow_html=True)

    saved_li_key = st.session_state.get('li_key') or user.get('linkedin_token')
    saved_gh_key = st.session_state.get('gh_key') or user.get('github_token')

    projects = get_projects("generated_projects", user['id'])
    project_names = list(projects.keys())

    # --- VIEW 1: LINKEDIN ---
    if selected_view == "🔵 LinkedIn Automation":
        
        # STATUS CARD
        if not saved_li_key:
            st.warning("⚠️ LinkedIn API Token is missing. Please add it in Settings.")
        
        # --- GLASS CARD: GENERATOR ---
        with st.container(border=True):
            st.subheader("✍️ AI Post Generator")
            
            # AUTO-FILL SECTION
            if project_names:
                with st.expander("⚡ Auto-fill from Saved Project", expanded=False):
                    col_sel, col_btn = st.columns([3, 1])
                    with col_sel:
                        st.selectbox("Select Project", project_names, key="social_li_project_selector")
                    with col_btn:
                        st.button("Load Details", on_click=auto_fill_linkedin, use_container_width=True)

            # MAIN INPUTS
            col1, col2 = st.columns([1, 1])
            with col1:
                st.text_input("Post Topic / Project Name", key="social_li_topic", placeholder="e.g. My New AI App")
            with col2:
                st.selectbox("Tone", ["Professional & Humble", "Excited & energetic", "Technical & Deep", "Storytelling"], key="social_li_tone")
            
            st.text_area(
                "Context (Paste README or Key Points)", 
                height=150, 
                key="social_li_desc", 
                help="The AI will read this to extract features and tech stack for the post."
            )

            if st.button("✨ Generate Viral Post"):
                with st.spinner("AI Copywriter is crafting your post..."):
                    payload = {
                        "project_name": st.session_state['social_li_topic'], 
                        "description": st.session_state['social_li_desc'], 
                        "tech_stack": "Included in description", 
                        "tone": st.session_state['social_li_tone']
                    }
                    try:
                        resp = requests.post(f"{API_BASE_URL}/generate-social", json=payload)
                        if resp.status_code == 200:
                            st.session_state['li_draft'] = resp.json().get('content', '')
                            # No rerun needed, just show it below
                        else:
                            st.error(f"Error: {resp.text}")
                    except Exception as e:
                        st.error(f"Conn Error: {e}")

        # --- PREVIEW & PUBLISH SECTION ---
        if st.session_state.get('li_draft'):
            st.markdown("<br>", unsafe_allow_html=True)
            col_edit, col_preview = st.columns([1, 1])
            
            with col_edit:
                st.subheader("📝 Edit Draft")
                final_content = st.text_area("Content", value=st.session_state['li_draft'], height=400, key="social_li_final", label_visibility="collapsed")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 Post to LinkedIn Now", type="primary", use_container_width=True):
                    if not saved_li_key:
                        st.error("Please connect LinkedIn in Settings first.")
                    else:
                        with st.spinner("Posting to LinkedIn..."):
                            resp = requests.post(f"{API_BASE_URL}/linkedin/post", json={"token": saved_li_key, "content": final_content})
                            if resp.status_code == 200:
                                st.balloons()
                                st.success("✅ Published successfully!")
                            else:
                                st.error(f"Failed: {resp.text}")

            with col_preview:
                st.subheader("👀 Preview")
                # Use the CSS class we defined in styles.py
                st.markdown(f"""
                <div class="linkedin-preview">
                    <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                        <div style="width: 48px; height: 48px; background: #ccc; border-radius: 50%;"></div>
                        <div>
                            <div class="li-name">{user.get('name', 'Your Name')}</div>
                            <div class="li-desc">Student at VIT • 1h • 🌐</div>
                        </div>
                    </div>
                    <div class="li-body">{final_content.replace(chr(10), '<br>')}</div>
                    <div class="li-footer">
                        <span>👍 Like</span>
                        <span>💬 Comment</span>
                        <span>share Repost</span>
                        <span>✈️ Send</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


    # --- VIEW 2: GITHUB ---
    elif selected_view == "🐙 GitHub Repo Manager":
        
        # STATUS CARD
        if not saved_gh_key:
             st.warning("⚠️ GitHub Token is missing. Please add it in Settings.")

        # --- GLASS CARD: REPO MANAGER ---
        with st.container(border=True):
            st.subheader("📦 Push Project to GitHub")
            
            if not project_names:
                st.info("No projects found. Go build something first!")
            else:
                gh_idx = 0
                # Handle Prefill from other pages
                if 'prefill_gh_project' in st.session_state:
                    target = st.session_state['prefill_gh_project']
                    if target in project_names:
                        gh_idx = project_names.index(target)
                        st.session_state['social_gh_project_selection'] = target 
                        update_gh_fields() 
                    # Clear prefill so we don't get stuck
                    del st.session_state['prefill_gh_project']

                # Selection Widget
                selected_proj = st.selectbox(
                    "Select Project to Upload", 
                    project_names, 
                    index=gh_idx, 
                    key="social_gh_project_selection",
                    on_change=update_gh_fields
                )
                
                # Run update once if descriptions are empty (first load)
                if not st.session_state.get('social_gh_reponame'):
                     update_gh_fields()

                st.markdown("---")
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    repo_name = st.text_input("New Repository Name", key="social_gh_reponame")
                with c2:
                    visibility = st.radio("Visibility", ["Public", "Private"], index=0, key="social_gh_vis")
                
                repo_desc = st.text_area("Repository Description", key="social_gh_desc", height=100)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if st.button("🐙 Create Repo & Push Code", type="primary", use_container_width=True):
                    if not saved_gh_key:
                        st.error("Connect GitHub in Settings first.")
                    else:
                        with st.spinner(f"Initializing Git, Creating Repo '{repo_name}', and Pushing..."):
                            payload = {
                                "user_id": str(user['id']), 
                                "token": saved_gh_key,
                                "project_name": selected_proj, # The folder name
                                "repo_name": repo_name,        # The desired repo name
                                "description": repo_desc,
                                "is_private": visibility == "Private"
                            }
                            # Note: The Backend endpoint is /github/push
                            try:
                                resp = requests.post(f"{API_BASE_URL}/github/push", json=payload, timeout=30)
                                result = resp.json()
                                
                                if result.get("status") == "success":
                                    st.balloons()
                                    st.success(f"✅ Success! Uploaded {result.get('files_uploaded', 'all')} files.")
                                    st.markdown(f"### [🔗 Click to View Repository]({result.get('url')})")
                                else:
                                    st.error(f"Error: {result.get('message')}")
                            except Exception as e:
                                st.error(f"Upload Failed: {e}")
    
    # Cleanup state to prevent stuck navigation
    if 'social_active_tab' in st.session_state:
        del st.session_state['social_active_tab']

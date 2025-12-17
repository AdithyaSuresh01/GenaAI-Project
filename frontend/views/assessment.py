import streamlit as st
import requests
import pandas as pd
from frontend.utils.api import API_BASE_URL

def render_assessment_page():
    # --- HEADER ---
    st.markdown("""
    <style>
        h1 {
            background: linear-gradient(90deg, #FF512F 0%, #DD2476 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
    </style>
    """, unsafe_allow_html=True)
    st.title("📝 Skill Assessment Center")
    st.markdown("<p style='color: #a0a0a0;'>Test your knowledge with AI-generated quizzes and assignments.</p>", unsafe_allow_html=True)

    user = st.session_state.get('user')
    if not user:
        st.error("Please login first.")
        return

    # --- SESSION INIT ---
    if 'data_quiz' not in st.session_state: st.session_state['data_quiz'] = None
    if 'data_assignment' not in st.session_state: st.session_state['data_assignment'] = None
    if 'data_test' not in st.session_state: st.session_state['data_test'] = None
    
    # State flags
    if 'quiz_submitted' not in st.session_state: st.session_state['quiz_submitted'] = False
    if 'quiz_score' not in st.session_state: st.session_state['quiz_score'] = 0 
    
    if 'test_submitted' not in st.session_state: st.session_state['test_submitted'] = False
    if 'test_score' not in st.session_state: st.session_state['test_score'] = 0
    if 'test_total' not in st.session_state: st.session_state['test_total'] = 0

    # Pre-fill topic if coming from Roadmap
    default_topic = st.session_state.get('assessment_prefill_topic', "Python Lists")

    # --- PAST RESULTS (Collapsible) ---
    with st.expander("📊 View Past Performance", expanded=False):
        try:
            resp = requests.get(f"{API_BASE_URL}/user-scores/{user['id']}")
            if resp.status_code == 200:
                scores = resp.json()
                if scores:
                    df = pd.DataFrame(scores)
                    # Clean up dataframe for display
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No completed tests yet.")
        except Exception as e:
            st.error(f"Error loading scores: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MAIN INTERFACE ---
    tab1, tab2, tab3 = st.tabs(["⚡ Pop Quiz", "📋 Assignment", "🏆 Mock Test"])
    
    # Common Input
    with st.container(border=True):
        topic = st.text_input("Topic to Assess", value=default_topic, key="assessment_topic_input")

    # --- TAB 1: QUIZ ---
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # A. GENERATE
        if not st.session_state['data_quiz'] or st.session_state['quiz_submitted']:
            col_gen, _ = st.columns([1, 2])
            with col_gen:
                if st.button("🎲 Generate Pop Quiz", key="btn_gen_quiz", type="primary"):
                    st.session_state['quiz_submitted'] = False
                    st.session_state['quiz_score'] = 0
                    
                    with st.spinner("Creating questions..."):
                        payload = {"user_id": user['id'], "topic": topic, "type": "quiz"}
                        try:
                            resp = requests.post(f"{API_BASE_URL}/generate-assessment", json=payload, timeout=20)
                            if resp.status_code == 200:
                                st.session_state['data_quiz'] = resp.json()
                                st.rerun()
                            else:
                                st.error(f"Error: {resp.text}")
                        except Exception as e:
                            st.error(f"Connection Error: {e}")

        # B. QUIZ FORM
        if st.session_state['data_quiz'] and not st.session_state['quiz_submitted']:
            quiz = st.session_state['data_quiz']
            
            with st.container(border=True):
                st.subheader(quiz.get('title', 'Pop Quiz'))
                st.markdown("---")
                
                with st.form("quiz_form", border=False):
                    current_score = 0
                    total = len(quiz.get('questions', []))
                    
                    for idx, q in enumerate(quiz.get('questions', [])):
                        st.markdown(f"**{idx+1}. {q.get('q')}**")
                        options = q.get('options', ["True", "False"])
                        # Key must be unique per question
                        user_ans = st.radio(f"Select Answer for Q{idx+1}", options, key=f"quiz_q_{idx}", label_visibility="collapsed")
                        
                        if user_ans == q.get('answer'):
                            current_score += 1
                        st.markdown("<br>", unsafe_allow_html=True)
                    
                    submitted = st.form_submit_button("Submit Answers", type="primary")
                    
                    if submitted:
                        st.session_state['quiz_score'] = current_score
                        
                        # Save Score
                        quiz_id = quiz.get('id')
                        if quiz_id:
                            try:
                                requests.post(f"{API_BASE_URL}/submit-score", json={"quiz_id": quiz_id, "score": current_score}, timeout=5)
                                st.toast("Score saved successfully!")
                            except:
                                pass
                        
                        st.session_state['quiz_submitted'] = True
                        st.rerun()

        # C. RESULTS
        if st.session_state['quiz_submitted']:
            quiz = st.session_state['data_quiz']
            score = st.session_state['quiz_score']
            total = len(quiz.get('questions', []))
            
            # Result Card
            if score / total >= 0.7:
                st.success(f"🎉 Great Job! Score: {score}/{total}")
                st.balloons()
            else:
                st.warning(f"Keep practicing! Score: {score}/{total}")
            
            c1, c2 = st.columns([1, 1])
            with c1:
                # Download
                if st.button("📥 Download Results PDF", key="dl_quiz"):
                    payload = {
                        "title": quiz.get('title', 'Assessment'),
                        "questions": quiz.get('questions', []),
                        "score": score,
                        "total": total,
                        "include_results": True
                    }
                    try:
                        resp = requests.post(f"{API_BASE_URL}/assessment/download-pdf", json=payload)
                        if resp.status_code == 200:
                            st.download_button("📄 Save Result PDF", resp.content, "quiz_results.pdf", "application/pdf")
                    except Exception as e:
                        st.error(f"PDF Error: {e}")
            
            with c2:
                if st.button("🔄 Take Another Quiz", key="clear_quiz"):
                    st.session_state['data_quiz'] = None
                    st.session_state['quiz_submitted'] = False
                    st.rerun()

    # --- TAB 2: ASSIGNMENT ---
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📋 Generate Homework Assignment", key="btn_gen_assign", type="primary"):
            with st.spinner("Designing task..."):
                payload = {"user_id": user['id'], "topic": topic, "type": "assignment"}
                try:
                    resp = requests.post(f"{API_BASE_URL}/generate-assessment", json=payload, timeout=20)
                    if resp.status_code == 200:
                        st.session_state['data_assignment'] = resp.json()
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

        if st.session_state['data_assignment']:
            data = st.session_state['data_assignment']
            
            with st.container(border=True):
                st.subheader(data.get('title', 'Assignment'))
                st.markdown("---")
                
                for i, q in enumerate(data.get('questions', [])):
                    st.markdown(f"**Task {i+1}:** {q.get('q')}")
                    with st.expander("See Expected Output"):
                        st.info(f"Expected: {q.get('answer')}")
                    st.markdown("<br>", unsafe_allow_html=True)

            # Download
            if st.button("📥 Download Assignment PDF", key="dl_assign"):
                payload = {
                    "title": data.get('title', 'Assignment'),
                    "questions": data.get('questions', []),
                    "include_results": False
                }
                try:
                    resp = requests.post(f"{API_BASE_URL}/assessment/download-pdf", json=payload)
                    if resp.status_code == 200:
                        st.download_button("📄 Save PDF", resp.content, "assignment.pdf", "application/pdf")
                except:
                    pass

    # --- TAB 3: MOCK TEST ---
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🏆 Start Timed Mock Test", key="btn_gen_test", type="primary"):
            with st.spinner("Preparing exam..."):
                payload = {"user_id": user['id'], "topic": topic, "type": "test"}
                try:
                    resp = requests.post(f"{API_BASE_URL}/generate-assessment", json=payload, timeout=20)
                    if resp.status_code == 200:
                        st.session_state['data_test'] = resp.json()
                        # Reset test state
                        st.session_state['test_submitted'] = False
                        st.rerun()
                    else:
                        st.error(f"Error: {resp.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

        if st.session_state['data_test'] and not st.session_state['test_submitted']:
            test = st.session_state['data_test']
            st.warning("⚠️ Time Limit: 10 Minutes (Self-timed). Do not refresh page.")
            
            with st.container(border=True):
                st.subheader(test.get('title', 'Mock Test'))
                
                with st.form("test_form", border=False):
                    score = 0
                    total = len(test.get('questions', []))
                    
                    for idx, q in enumerate(test.get('questions', [])):
                        st.markdown(f"**Q{idx+1}: {q.get('q')}**")
                        options = q.get('options', [])
                        if options:
                            user_ans = st.radio("Answer", options, key=f"test_q_{idx}", label_visibility="collapsed")
                            if user_ans == q.get('answer'):
                                score += 1
                        st.markdown("<br>", unsafe_allow_html=True)

                    submitted_test = st.form_submit_button("Finish Test", type="primary")
                    
                    if submitted_test:
                        st.session_state['test_score'] = score
                        st.session_state['test_total'] = total
                        st.session_state['test_submitted'] = True
                        
                        test_id = test.get('id')
                        if test_id:
                            try:
                                requests.post(f"{API_BASE_URL}/submit-score", json={"quiz_id": test_id, "score": score}, timeout=5)
                            except: pass
                        st.rerun()

        # Test Results
        if st.session_state['test_submitted']:
            score = st.session_state.get('test_score', 0)
            total = st.session_state.get('test_total', 0)
            test = st.session_state['data_test']
            
            st.markdown(f"### Final Score: {score}/{total}")
            st.progress(score/total)
            
            if st.button("📥 Download Test Report", key="dl_test"):
                payload = {
                    "title": test.get('title', 'Mock Test'),
                    "questions": test.get('questions', []),
                    "score": score,
                    "total": total,
                    "include_results": True
                }
                try:
                    resp = requests.post(f"{API_BASE_URL}/assessment/download-pdf", json=payload)
                    if resp.status_code == 200:
                        st.download_button("📄 Save Report", resp.content, "test_results.pdf", "application/pdf")
                except: pass

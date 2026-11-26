import os, time, json
from datetime import datetime, date
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Database & Engine Modules
from modules.database import (
    init_db, create_user, authenticate_user, get_student_profile, update_student_profile,
    get_subjects, get_topics, add_custom_topic, save_quiz_result, get_results,
    get_topic_stats, get_subject_stats, save_study_plan, get_study_plans,
    delete_study_plan, update_timetable_task, save_student_note, get_student_notes
)
from modules.ai_engine import (
    generate_explanation, generate_quiz, generate_adaptive_single_question,
    generate_study_timetable, generate_flashcards, generate_chat_response, is_ai_connected
)
from modules.analytics import (
    build_progress_summary, recommend_topics, create_radar_mastery_chart,
    create_topic_bar_chart, create_progress_timeline, create_accuracy_donut
)

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="LearnSphere AI – Personalized Adaptive Learning",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Custom UI Theme & Styles
def inject_custom_styles():
    st.markdown("""
    <style>
    /* Global layout & typography */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        color: #0f172a !important;
    }

    /* Universal High-Contrast Text Enforcement for Main Area */
    .stApp p, .stApp span, .stApp label, .stApp div[data-testid="stMarkdownContainer"] p {
        color: #0f172a !important;
    }
    
    /* Modern Sidebar Styling */
    [data-testid="stSidebar"] {
        background: #0f172a !important;
        border-right: 1px solid #1e293b !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #cbd5e1 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stRadio"] > div {
        gap: 6px;
    }

    [data-testid="stSidebar"] div[data-testid="stRadio"] label {
        padding: 8px 12px;
        border-radius: 8px;
        transition: all 0.2s ease;
    }

    /* Hero Banner */
    .hero-banner {
        padding: 1.8rem 2.2rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #1e3a8a 0%, #2563eb 60%, #3b82f6 100%);
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.25);
    }
    .hero-banner h1 {
        color: white !important;
        font-size: 2rem;
        font-weight: 800;
        margin: 0;
    }
    .hero-banner p {
        color: #e0e7ff !important;
        font-size: 1.05rem;
        margin-top: 0.4rem;
        margin-bottom: 0;
    }

    /* Assessment Banner - Vibrant & High Contrast */
    .assessment-banner {
        padding: 1.6rem 2rem;
        border-radius: 16px;
        background: linear-gradient(125deg, #0f172a 0%, #1e3a8a 60%, #2563eb 100%);
        color: white !important;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .assessment-banner h2 {
        color: #ffffff !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        margin: 0 0 0.4rem 0 !important;
    }
    .assessment-banner p {
        color: #cbd5e1 !important;
        font-size: 1rem !important;
        margin: 0 !important;
    }
    .assessment-badge-pill {
        background: rgba(255, 255, 255, 0.18);
        color: #ffffff !important;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border: 1px solid rgba(255, 255, 255, 0.25);
    }

    /* Question Card Container */
    .question-card {
        background: #ffffff !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 14px !important;
        padding: 1.5rem 1.6rem !important;
        margin-bottom: 1.2rem !important;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05) !important;
    }
    .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.9rem;
    }
    .question-num-pill {
        background: #eff6ff !important;
        color: #1d4ed8 !important;
        border: 1px solid #bfdbfe !important;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 0.84rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .question-title {
        color: #0f172a !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        line-height: 1.5 !important;
        margin: 0.2rem 0 0.8rem 0 !important;
    }
    
    /* Form & Radio Button Option Readability */
    div[data-testid="stForm"] {
        background: #ffffff !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 1.6rem !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
    }
    div[data-testid="stRadio"] > div {
        background: #f8fafc !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 0.8rem 1rem !important;
        gap: 10px !important;
    }
    div[data-testid="stRadio"] label {
        color: #0f172a !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        padding: 6px 10px !important;
        border-radius: 6px !important;
        transition: background 0.15s ease !important;
    }
    div[data-testid="stRadio"] label:hover {
        background: #eff6ff !important;
    }
    div[data-testid="stRadio"] label p {
        color: #0f172a !important;
        font-size: 1.02rem !important;
        font-weight: 600 !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0.2rem 0;
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Badges */
    .badge-weak {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 800;
        border: 1px solid #fecaca;
    }
    .badge-developing {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 800;
        border: 1px solid #fde68a;
    }
    .badge-mastered {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 800;
        border: 1px solid #a7f3d0;
    }
    .badge-difficulty {
        padding: 5px 14px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 0.84rem;
        display: inline-block;
        letter-spacing: 0.03em;
    }
    .diff-easy { background: #dcfce7 !important; color: #166534 !important; border: 1.5px solid #86efac !important; }
    .diff-medium { background: #fef9c3 !important; color: #854d0e !important; border: 1.5px solid #fde047 !important; }
    .diff-hard { background: #fee2e2 !important; color: #991b1b !important; border: 1.5px solid #fca5a5 !important; }
    .diff-adaptive { background: #dbeafe !important; color: #1e40af !important; border: 1.5px solid #93c5fd !important; }

    /* Flashcard styling */
    .flashcard {
        background: white;
        border: 2px solid #cbd5e1;
        border-radius: 16px;
        padding: 2.2rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    /* Timetable Task Row */
    .task-row {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.6rem;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_styles()

# Authentication Screen
def show_auth_screen():
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1rem;">
            <div style="font-size: 3.5rem;">🎓</div>
            <h1 style="color: #1e3a8a; font-weight: 800; margin: 0;">LearnSphere AI</h1>
            <p style="color: #64748b; font-size: 1.1rem; margin-top: 0.3rem;">
                Personalized Adaptive Learning Platform powered by Generative AI
            </p>
        </div>
        """, unsafe_allow_html=True)

        auth_tab1, auth_tab2 = st.tabs(["🔐 Sign In", "✨ Create Student Account"])

        with auth_tab1:
            with st.form("login_form"):
                email = st.text_input("Student Email", placeholder="student@university.edu")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Sign In to LearnSphere", use_container_width=True, type="primary")

                if submit_login:
                    user = authenticate_user(email.strip().lower(), password)
                    if user:
                        st.session_state.user = user
                        st.success(f"Welcome back, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("Invalid email or password. Please verify your credentials.")

        with auth_tab2:
            with st.form("signup_form"):
                name = st.text_input("Full Name", placeholder="Alex Morgan")
                signup_email = st.text_input("Email Address", placeholder="alex@university.edu")
                signup_pass = st.text_input("Create Password (min. 6 characters)", type="password")

                col_a, col_b = st.columns(2)
                with col_a:
                    target_exam = st.selectbox(
                        "Primary Target Goal / Curriculum",
                        [
                            "Software Engineering & AI",
                            "Data Science & Machine Learning",
                            "Computer Science Fundamentals",
                            "Competitive Exams & GATE",
                            "Web Development Mastery"
                        ]
                    )
                with col_b:
                    learning_pace = st.selectbox(
                        "Learning Pace Preference",
                        [
                            "Standard / Balanced",
                            "Deep & Foundational (Step-by-step)",
                            "Accelerated / Fast-Paced"
                        ]
                    )

                submit_signup = st.form_submit_button("Register & Begin Learning", use_container_width=True, type="primary")
                if submit_signup:
                    ok, msg = create_user(name.strip(), signup_email.strip().lower(), signup_pass, target_exam, learning_pace)
                    if ok:
                        st.success(msg + " You can now switch to the 'Sign In' tab to log in.")
                    else:
                        st.error(msg)

        # AI Status Pill
        st.markdown("---")
        ai_active = is_ai_connected()
        if ai_active:
            st.success("🟢 **Gemini AI Active:** Connected to Google Generative AI API.")
        else:
            st.info("ℹ️ **Offline / Demo Mode Active:** High-quality local curriculum banks loaded. To enable live Gemini AI generation, add `GEMINI_API_KEY` to `.env`.")

# Check session authentication
if "user" not in st.session_state:
    show_auth_screen()
    st.stop()

# Current authenticated student
user = st.session_state.user
student_profile = get_student_profile(user["id"]) or user

# Navigation Sidebar
with st.sidebar:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 1rem;">
        <span style="font-size: 2.2rem;">{student_profile.get('avatar', '🎓')}</span>
        <div>
            <h3 style="margin: 0; font-size: 1.15rem;">{student_profile['name']}</h3>
            <span style="font-size: 0.8rem; color: #94a3b8;">{student_profile.get('target_exam', 'Student')}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "📊 Dashboard",
            "⚡ Adaptive Quiz",
            "📝 Topic Assessment",
            "💬 AI Tutor",
            "📅 Study Timetable",
            "🗂️ AI Flashcards",
            "📈 Progress & Analytics",
            "⚙️ Profile & Goals"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    # Quick AI Status badge in sidebar
    if is_ai_connected():
        st.markdown('<span style="color:#4ade80; font-size:0.82rem;">● Gemini AI Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#fbbf24; font-size:0.82rem;">○ Offline Demo Engine</span>', unsafe_allow_html=True)

    if st.button("🚪 Log Out", use_container_width=True):
        del st.session_state.user
        st.rerun()

# Helper for subject & topic selection
subjects = get_subjects()
subject_names = [s["name"] for s in subjects]
subject_map = {s["name"]: s["id"] for s in subjects}

def render_subject_topic_selectors(key_prefix="selector"):
    c1, c2 = st.columns(2)
    with c1:
        default_sub_idx = 0
        if "preselected_subject" in st.session_state and st.session_state.preselected_subject in subject_names:
            default_sub_idx = subject_names.index(st.session_state.preselected_subject)
        selected_subject = st.selectbox("Subject", subject_names, index=default_sub_idx, key=f"{key_prefix}_subj")

    topics = get_topics(subject_map[selected_subject])
    topic_names = [t["name"] for t in topics]
    topic_map = {t["name"]: t["id"] for t in topics}

    with c2:
        default_top_idx = 0
        if "preselected_topic" in st.session_state and st.session_state.preselected_topic in topic_names:
            default_top_idx = topic_names.index(st.session_state.preselected_topic)
        selected_topic = st.selectbox("Topic", topic_names, index=default_top_idx, key=f"{key_prefix}_top") if topic_names else None

    return selected_subject, selected_topic, topic_map.get(selected_topic) if selected_topic else None

# =========================================================================
# PAGE 1: DASHBOARD
# =========================================================================
if page == "📊 Dashboard":
    first_name = student_profile["name"].split()[0]
    st.markdown(f"""
    <div class="hero-banner">
        <h1>Welcome back, {first_name}! {student_profile.get('avatar', '🎓')}</h1>
        <p>Your personalized AI learning path adapts in real time to your strengths and weaknesses.</p>
    </div>
    """, unsafe_allow_html=True)

    results = get_results(user["id"])
    summary = build_progress_summary(results)

    # Metric Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Quizzes Taken</div>
            <div class="metric-value">{summary['attempts']}</div>
            <span style="font-size:0.8rem; color:#64748b;">Total sessions</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        avg_color = "#10b981" if summary['average'] >= 80 else ("#f59e0b" if summary['average'] >= 60 else "#ef4444")
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Average Score</div>
            <div class="metric-value" style="color: {avg_color};">{summary['average']:.1f}%</div>
            <span style="font-size:0.8rem; color:#64748b;">Overall performance</span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Questions Solved</div>
            <div class="metric-value">{summary['total_questions']}</div>
            <span style="font-size:0.8rem; color:#64748b;">{summary['total_correct']} correct answers</span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Study Streak</div>
            <div class="metric-value">🔥 {summary['streak_days']} <span style="font-size:1rem; font-weight:600;">days</span></div>
            <span style="font-size:0.8rem; color:#64748b;">Consistency bonus</span>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Learner Rank</div>
            <div class="metric-value" style="font-size:1.25rem; color:#2563eb; margin-top:0.4rem;">{summary['level']}</div>
            <span style="font-size:0.8rem; color:#64748b;">⭐ {summary['xp']} XP</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two column layout: Weak Areas & Adaptive Recommendations | Multi-Subject Radar
    col_rec, col_radar = st.columns([3, 2])

    with col_rec:
        st.subheader("🎯 Weak Area Analysis & Adaptive Recommendations")
        topic_stats = get_topic_stats(user["id"])
        recommendations = recommend_topics(topic_stats)

        if recommendations:
            st.caption("LearnSphere analyzes your error patterns to recommend targeted drills:")
            for item in recommendations[:4]:
                badge_class = "badge-weak" if item["average"] < 60 else ("badge-developing" if item["average"] < 80 else "badge-mastered")
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1rem; margin-bottom: 0.75rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-weight: 700; font-size: 1.05rem; color: #0f172a;">{item['topic']}</span>
                                <span style="font-size: 0.8rem; color: #64748b; margin-left: 8px;">({item['subject']})</span>
                            </div>
                            <span class="{badge_class}">{item['status']}</span>
                        </div>
                        <p style="margin: 0.4rem 0 0.6rem; color: #475569; font-size: 0.9rem;">{item['reason']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"⚡ Practice '{item['topic']}'", key=f"btn_rec_{item['topic']}"):
                        st.session_state.preselected_subject = item['subject']
                        st.session_state.preselected_topic = item['topic']
                        st.session_state.start_adaptive = True
                        st.info(f"Loaded '{item['topic']}'. Navigate to '⚡ Adaptive Quiz' to begin your tailored drill!")
        else:
            st.info("💡 **No quiz results recorded yet.** Take your first diagnostic quiz to enable weakness detection and personalized recommendations!")

    with col_radar:
        st.subheader("🕸️ Subject Competency")
        subject_stats = get_subject_stats(user["id"])
        if subject_stats and len(subject_stats) >= 2:
            radar_fig = create_radar_mastery_chart(subject_stats)
            if radar_fig:
                st.plotly_chart(radar_fig, use_container_width=True)
        else:
            st.markdown("""
            <div style="background: white; border: 1px dashed #cbd5e1; border-radius: 12px; padding: 2.5rem 1.5rem; text-align: center; color: #64748b;">
                <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🕸️</div>
                <h4 style="margin: 0; color: #334155;">Multi-Subject Radar</h4>
                <p style="font-size: 0.88rem; margin-top: 0.4rem;">Complete quizzes across at least 2 subjects to reveal your multidimensional mastery spider chart.</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("🚀 Quick Action Hub")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="font-size: 2rem;">⚡</div>
            <h4 style="margin: 0.4rem 0;">Adaptive Quiz</h4>
            <p style="font-size: 0.82rem; color: #64748b;">Questions adjust difficulty in real-time based on your answers.</p>
        </div>
        """, unsafe_allow_html=True)
    with q2:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="font-size: 2rem;">💬</div>
            <h4 style="margin: 0.4rem 0;">AI Tutor</h4>
            <p style="font-size: 0.82rem; color: #64748b;">Get step-by-step intuitive explanations at your learning level.</p>
        </div>
        """, unsafe_allow_html=True)
    with q3:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="font-size: 2rem;">📅</div>
            <h4 style="margin: 0.4rem 0;">Study Timetable</h4>
            <p style="font-size: 0.82rem; color: #64748b;">Automatic day-by-day schedule tailored to your weak areas.</p>
        </div>
        """, unsafe_allow_html=True)
    with q4:
        st.markdown("""
        <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.2rem; text-align: center;">
            <div style="font-size: 2rem;">🗂️</div>
            <h4 style="margin: 0.4rem 0;">AI Flashcards</h4>
            <p style="font-size: 0.82rem; color: #64748b;">Active recall cards generated from notes and concepts.</p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================================
# PAGE 2: REAL-TIME ADAPTIVE QUIZ (Difficulty adjustment based on previous answers)
# =========================================================================
elif page == "⚡ Adaptive Quiz":
    st.markdown("""
    <div class="assessment-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2>⚡ Real-Time Adaptive Quiz Engine</h2>
                <p>The system dynamically increases difficulty on correct answers and scales down for remediation.</p>
            </div>
            <span class="assessment-badge-pill">⚡ Adaptive Engine</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    subject, topic, topic_id = render_subject_topic_selectors("adaptive")

    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        starting_diff = st.selectbox("Starting Difficulty", ["Easy", "Medium", "Hard"], index=1)
    with col_cfg2:
        total_session_q = st.slider("Session Length (Questions)", min_value=3, max_value=10, value=5)
    with col_cfg3:
        st.write("")
        st.write("")
        start_btn = st.button("🚀 Start Adaptive Session", type="primary", use_container_width=True)

    # Initialize adaptive session state
    if "adaptive_state" not in st.session_state or start_btn:
        if start_btn or ("start_adaptive" in st.session_state and st.session_state.start_adaptive):
            if "start_adaptive" in st.session_state:
                del st.session_state.start_adaptive
            st.session_state.adaptive_state = {
                "active": True,
                "subject": subject,
                "topic": topic,
                "topic_id": topic_id,
                "current_diff": starting_diff,
                "q_number": 1,
                "max_questions": total_session_q,
                "history": [],  # list of {question, selected, correct, is_correct, diff, explanation}
                "current_q": None,
                "answered_current": False,
                "start_time": time.time()
            }

    sess = st.session_state.get("adaptive_state")

    if sess and sess.get("active"):
        st.markdown("---")

        # Session Progress Bar & Trajectory
        q_num = sess["q_number"]
        max_q = sess["max_questions"]
        progress_val = (q_num - 1) / max_q
        st.progress(progress_val, text=f"Question {q_num} of {max_q} | Current Difficulty: {sess['current_diff']}")

        # Fetch question for current step if not present
        if sess["current_q"] is None:
            prev_correct = sess["history"][-1]["is_correct"] if sess["history"] else None
            with st.spinner(f"AI generating question #{q_num} at '{sess['current_diff']}' difficulty..."):
                sess["current_q"] = generate_adaptive_single_question(
                    sess["topic"],
                    sess["subject"],
                    sess["current_diff"],
                    q_num,
                    prev_correct
                )
            st.rerun()

        q_data = sess["current_q"]

        # Display question card with high-contrast styling
        diff_class = f"diff-{sess['current_diff'].lower()}"
        st.markdown(f"""
        <div class="question-card">
            <div class="question-header">
                <span class="question-num-pill">QUESTION {q_num} OF {max_q}</span>
                <span class="badge-difficulty {diff_class}">Difficulty: {sess['current_diff']}</span>
            </div>
            <div class="question-title">{q_data['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        if not sess["answered_current"]:
            with st.form(f"adaptive_form_{q_num}"):
                user_choice = st.radio(
                    "Choose the correct answer:",
                    q_data["options"],
                    index=None,
                    key=f"adaptive_choice_{q_num}"
                )
                submit_ans = st.form_submit_button("Submit Answer", type="primary", use_container_width=True)

                if submit_ans:
                    if not user_choice:
                        st.warning("Please select an option before submitting.")
                    else:
                        is_correct = (user_choice == q_data["answer"])
                        record = {
                            "question": q_data["question"],
                            "selected": user_choice,
                            "correct": q_data["answer"],
                            "is_correct": is_correct,
                            "difficulty": sess["current_diff"],
                            "explanation": q_data.get("explanation", "")
                        }
                        sess["history"].append(record)
                        sess["answered_current"] = True
                        st.rerun()
        else:
            # Immediate feedback shown after answering
            last_record = sess["history"][-1]
            if last_record["is_correct"]:
                st.success(f"🎉 **Correct!** Great job on this {last_record['difficulty']} question.")
                # Adaptive logic: level up if possible
                if sess["current_diff"] == "Easy":
                    next_diff = "Medium"
                elif sess["current_diff"] == "Medium":
                    next_diff = "Hard"
                else:
                    next_diff = "Hard"
            else:
                st.error(f"❌ **Incorrect.** You selected '{last_record['selected']}'. The correct answer was **'{last_record['correct']}'**.")
                # Adaptive logic: step down or reinforce
                if sess["current_diff"] == "Hard":
                    next_diff = "Medium"
                elif sess["current_diff"] == "Medium":
                    next_diff = "Easy"
                else:
                    next_diff = "Easy"

            with st.expander("💡 View Detailed AI Explanation", expanded=True):
                st.write(last_record["explanation"])

            # Button to advance to next question or conclude session
            if q_num < max_q:
                if st.button(f"Next Question (Adapting to: {next_diff}) ➔", type="primary"):
                    sess["current_diff"] = next_diff
                    sess["q_number"] += 1
                    sess["current_q"] = None
                    sess["answered_current"] = False
                    st.rerun()
            else:
                if st.button("🏁 Finish Adaptive Assessment & View Summary", type="primary"):
                    sess["active"] = False
                    # Calculate final stats and persist to database
                    total_solved = len(sess["history"])
                    correct_count = sum(1 for h in sess["history"] if h["is_correct"])
                    score_pct = round((correct_count / total_solved) * 100, 1)
                    time_taken = int(time.time() - sess["start_time"])

                    save_quiz_result(
                        user["id"],
                        sess["topic_id"],
                        score_pct,
                        total_solved,
                        correct_count,
                        difficulty="Adaptive",
                        time_taken=time_taken,
                        details=sess["history"]
                    )
                    st.session_state.last_adaptive_summary = {
                        "score": score_pct,
                        "correct": correct_count,
                        "total": total_solved,
                        "topic": sess["topic"],
                        "subject": sess["subject"],
                        "history": sess["history"],
                        "time_taken": time_taken
                    }
                    st.rerun()

    # Display completion summary if finished
    elif "last_adaptive_summary" in st.session_state:
        summ = st.session_state.last_adaptive_summary
        st.markdown(f"""
        <div class="hero-banner" style="background: linear-gradient(120deg, #059669 0%, #10b981 100%);">
            <h1>Assessment Completed! 🏆</h1>
            <p>You scored <strong>{summ['correct']} / {summ['total']} ({summ['score']}%)</strong> on <strong>{summ['topic']}</strong> in {summ['time_taken']} seconds.</p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Adaptive Trajectory Breakdown")
        for i, item in enumerate(summ["history"], 1):
            icon = "✅" if item["is_correct"] else "❌"
            with st.expander(f"{icon} Q{i} [{item['difficulty']}]: {item['question'][:60]}..."):
                st.write(f"**Your Answer:** {item['selected']}")
                st.write(f"**Correct Answer:** {item['correct']}")
                st.info(item["explanation"])

        if st.button("Start Another Quiz"):
            del st.session_state.last_adaptive_summary
            st.rerun()

# =========================================================================
# PAGE 3: STANDARD TOPIC ASSESSMENT
# =========================================================================
elif page == "📝 Topic Assessment":
    st.markdown("""
    <div class="assessment-banner">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <h2>📝 Topic Assessment Quiz</h2>
                <p>Test your knowledge across custom question sets, measure accuracy, and evaluate topic mastery.</p>
            </div>
            <span class="assessment-badge-pill">Curriculum Drill</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    subject, topic, topic_id = render_subject_topic_selectors("batch")

    c1, c2, c3 = st.columns(3)
    with c1:
        difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"], index=1, key="batch_diff")
    with c2:
        count = st.slider("Number of Questions", 3, 10, 5, key="batch_count")
    with c3:
        st.write("")
        st.write("")
        gen_batch_btn = st.button("⚡ Generate Assessment", type="primary", use_container_width=True)

    if gen_batch_btn:
        with st.spinner(f"Generating {count} questions for '{topic}'..."):
            st.session_state.batch_quiz_data = generate_quiz(topic, subject, difficulty, count)
            st.session_state.batch_topic_id = topic_id
            st.session_state.batch_topic = topic
            st.session_state.batch_subject = subject
            st.session_state.batch_difficulty = difficulty
            st.session_state.batch_start_time = time.time()

    quiz = st.session_state.get("batch_quiz_data")
    if quiz:
        diff_pill_class = f"diff-{difficulty.lower()}"
        st.markdown(f"""
        <div style="background: white; border: 2px solid #cbd5e1; border-radius: 12px; padding: 1rem 1.4rem; margin-bottom: 1.2rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 800; font-size: 1.2rem; color: #0f172a;">📋 {st.session_state.batch_topic}</span>
            <span class="badge-difficulty {diff_pill_class}">Level: {difficulty} · {len(quiz)} Questions</span>
        </div>
        """, unsafe_allow_html=True)

        with st.form("batch_quiz_form"):
            answers = []
            for i, q in enumerate(quiz):
                st.markdown(f"""
                <div class="question-card" style="margin-bottom: 0.8rem;">
                    <div class="question-header">
                        <span class="question-num-pill">Question {i+1} of {len(quiz)}</span>
                        <span class="badge-difficulty {diff_pill_class}">{q.get('difficulty', difficulty)}</span>
                    </div>
                    <div class="question-title">Q{i+1}. {q['question']}</div>
                </div>
                """, unsafe_allow_html=True)
                choice = st.radio(
                    f"Select answer for Question {i+1}:",
                    q["options"],
                    key=f"batch_ans_{i}",
                    index=None,
                    label_visibility="collapsed"
                )
                answers.append(choice)
                st.markdown("<hr style='margin: 1rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

            submitted = st.form_submit_button("Submit Assessment Answers", type="primary", use_container_width=True)

        if submitted:
            if None in answers:
                st.warning("Please answer all questions before submitting.")
            else:
                correct = sum(1 for a, q in zip(answers, quiz) if a == q["answer"])
                score = round((correct / len(quiz)) * 100, 1)
                time_taken = int(time.time() - st.session_state.get("batch_start_time", time.time()))

                details = [
                    {
                        "question": q["question"],
                        "selected": a,
                        "correct": q["answer"],
                        "explanation": q.get("explanation", ""),
                        "is_correct": (a == q["answer"])
                    }
                    for a, q in zip(answers, quiz)
                ]

                save_quiz_result(user["id"], st.session_state.batch_topic_id, score, len(quiz), correct, difficulty, time_taken, details)

                if score >= 80:
                    st.balloons()
                    st.success(f"🌟 Outstanding! You scored {correct}/{len(quiz)} ({score:.1f}%). Topic Mastered!")
                elif score >= 60:
                    st.info(f"👍 Good effort! You scored {correct}/{len(quiz)} ({score:.1f}%). Keep practicing to solidify concepts.")
                else:
                    st.warning(f"⚠️ You scored {correct}/{len(quiz)} ({score:.1f}%). We recommend reviewing this topic with the AI Tutor.")

                for i, d in enumerate(details, 1):
                    with st.expander(f"Question {i}: {'✅ Correct' if d['is_correct'] else '❌ Review Required'}"):
                        st.write(f"**Your Answer:** {d['selected']}")
                        st.write(f"**Correct Answer:** {d['correct']}")
                        st.write(d["explanation"])

                st.session_state.batch_quiz_data = None
                st.info("Results saved to your learning progress dashboard.")

        if submitted:
            if None in answers:
                st.warning("Please answer all questions before submitting.")
            else:
                correct = sum(1 for a, q in zip(answers, quiz) if a == q["answer"])
                score = round((correct / len(quiz)) * 100, 1)
                time_taken = int(time.time() - st.session_state.get("batch_start_time", time.time()))

                details = [
                    {
                        "question": q["question"],
                        "selected": a,
                        "correct": q["answer"],
                        "explanation": q.get("explanation", ""),
                        "is_correct": (a == q["answer"])
                    }
                    for a, q in zip(answers, quiz)
                ]

                save_quiz_result(user["id"], st.session_state.batch_topic_id, score, len(quiz), correct, difficulty, time_taken, details)

                if score >= 80:
                    st.balloons()
                    st.success(f"🌟 Outstanding! You scored {correct}/{len(quiz)} ({score:.1f}%). Topic Mastered!")
                elif score >= 60:
                    st.info(f"👍 Good effort! You scored {correct}/{len(quiz)} ({score:.1f}%). Keep practicing to solidify concepts.")
                else:
                    st.warning(f"⚠️ You scored {correct}/{len(quiz)} ({score:.1f}%). We recommend reviewing this topic with the AI Tutor.")

                for i, d in enumerate(details, 1):
                    with st.expander(f"Question {i}: {'✅ Correct' if d['is_correct'] else '❌ Review Required'}"):
                        st.write(f"**Your Answer:** {d['selected']}")
                        st.write(f"**Correct Answer:** {d['correct']}")
                        st.write(d["explanation"])

                st.session_state.batch_quiz_data = None
                st.info("Results saved to your learning progress dashboard.")

# =========================================================================
# PAGE 4: AI TUTOR (LangChain-powered multi-level tutoring)
# =========================================================================
elif page == "💬 AI Tutor":
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="margin: 0; color: #1e3a8a;">💬 LearnSphere AI Personal Tutor</h2>
        <p style="color: #64748b; margin-top: 0.2rem;">
            Ask questions, explore concepts, and receive structured explanations matched to your pace.
        </p>
    </div>
    """, unsafe_allow_html=True)

    subject, topic, topic_id = render_subject_topic_selectors("tutor")

    col_l1, col_l2 = st.columns([1, 1])
    with col_l1:
        level = st.select_slider(
            "Explanation Level",
            options=["Beginner / Intuitive", "Intermediate / Applied", "Advanced / In-Depth"],
            value="Intermediate / Applied"
        )
    with col_l2:
        pace = student_profile.get("learning_pace", "Standard / Balanced")
        st.write(f"**Active Learning Pace:** `{pace}`")

    question = st.text_area(
        "What concept or problem would you like to master?",
        placeholder="Example: How does B-Tree indexing speed up range queries compared to a binary search tree?",
        height=100
    )

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        explain_btn = st.button("Explain Concept", type="primary", use_container_width=True)

    if explain_btn and question.strip():
        with st.spinner("Your AI tutor is crafting a personalized explanation..."):
            ans = generate_explanation(question.strip(), level, subject, topic, pace)
            st.session_state.current_tutor_response = {
                "question": question.strip(),
                "topic": topic,
                "content": ans
            }

    if "current_tutor_response" in st.session_state:
        resp = st.session_state.current_tutor_response
        st.markdown(resp["content"])

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔖 Save to My Notes"):
            save_student_note(user["id"], resp["question"][:50], resp["topic"], resp["content"])
            st.success("Saved to your personal notes notebook!")

# =========================================================================
# PAGE 5: AUTOMATIC STUDY TIMETABLE GENERATOR
# =========================================================================
elif page == "📅 Study Timetable":
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="margin: 0; color: #1e3a8a;">📅 Automatic Personalized Study Timetable</h2>
        <p style="color: #64748b; margin-top: 0.2rem;">
            Generates an adaptive daily routine and checklist designed around your target exams and weak subjects.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_create, tab_saved = st.tabs(["✨ Generate New Timetable", "📋 My Saved Timetables"])

    with tab_create:
        subject, topic, topic_id = render_subject_topic_selectors("timetable")

        # Automatically detect student's weak topics to include
        topic_stats = get_topic_stats(user["id"])
        weak_topics = [t["topic"] for t in topic_stats if float(t["average"]) < 60]

        if weak_topics:
            st.warning(f"⚠️ LearnSphere detected {len(weak_topics)} weak topics to remediate: **{', '.join(weak_topics)}**.")

        c1, c2, c3 = st.columns(3)
        with c1:
            hours = st.number_input("Available Study Hours / Day", min_value=0.5, max_value=12.0, value=2.0, step=0.5)
        with c2:
            days = st.slider("Duration (Days)", min_value=3, max_value=14, value=7)
        with c3:
            goal = st.text_input("Target Goal / Milestone", value=f"Prepare for {subject} evaluation")

        if st.button("🚀 Generate Adaptive Timetable", type="primary", use_container_width=True):
            with st.spinner("AI is calculating optimal learning sessions, drills, and active recall slots..."):
                timetable_data = generate_study_timetable(
                    subject=subject,
                    topic=topic,
                    daily_hours=hours,
                    duration_days=days,
                    goal=goal,
                    weak_topics=weak_topics,
                    pace=student_profile.get("learning_pace", "Standard / Balanced")
                )
                plan_id = save_study_plan(
                    student_id=user["id"],
                    topic_id=topic_id,
                    goal=goal,
                    daily_hours=hours,
                    duration_days=days,
                    content=timetable_data.get("markdown_overview", ""),
                    schedule_json=timetable_data.get("tasks", [])
                )
                st.session_state.active_plan_id = plan_id
                st.success("New personalized study timetable generated and saved!")
                st.rerun()

    with tab_saved:
        plans = get_study_plans(user["id"])
        if not plans:
            st.info("No saved timetables yet. Generate your first timetable in the 'Generate New Timetable' tab!")
        else:
            for p in plans:
                created_date = p["created_at"][:10]
                with st.expander(f"📅 {p['goal'] or 'Study Plan'} ({p.get('duration_days', 7)} Days · {p.get('daily_hours', 2)} hrs/day) — Created {created_date}"):
                    st.markdown(p["content"])

                    # Interactive Checklist
                    if p["schedule_json"]:
                        tasks = json.loads(p["schedule_json"])
                        st.subheader("Daily Task Tracker")
                        completed_cnt = sum(1 for t in tasks if t.get("completed"))
                        st.progress(completed_cnt / len(tasks) if tasks else 0, text=f"{completed_cnt} of {len(tasks)} tasks completed")

                        # Group tasks by day
                        for day_num in range(1, p.get("duration_days", 7) + 1):
                            day_tasks = [t for t in tasks if t.get("day") == day_num]
                            if day_tasks:
                                st.write(f"**Day {day_num} Sessions:**")
                                for t in day_tasks:
                                    t_checked = st.checkbox(
                                        f"[{t.get('time_slot', 'Session')}] {t.get('title')} ({t.get('duration_minutes', 45)} mins) — *{t.get('activity_type', 'Study')}*",
                                        value=t.get("completed", False),
                                        key=f"task_{p['id']}_{t['id']}"
                                    )
                                    if t_checked != t.get("completed", False):
                                        update_timetable_task(p["id"], t["id"], t_checked)
                                        st.rerun()

                    c_del1, c_del2 = st.columns([1, 4])
                    with c_del1:
                        if st.button("🗑️ Delete Plan", key=f"del_plan_{p['id']}"):
                            delete_study_plan(p["id"], user["id"])
                            st.rerun()

# =========================================================================
# PAGE 6: AI FLASHCARDS
# =========================================================================
elif page == "🗂️ AI Flashcards":
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="margin: 0; color: #1e3a8a;">🗂️ AI Flashcards & Spaced Repetition</h2>
        <p style="color: #64748b; margin-top: 0.2rem;">
            Solidify memory retention through active recall flashcards generated from topics or notes.
        </p>
    </div>
    """, unsafe_allow_html=True)

    subject, topic, topic_id = render_subject_topic_selectors("flashcard")

    notes_input = st.text_area(
        "Paste custom lecture notes or key concepts (optional):",
        placeholder="Paste paragraphs from your textbook or lecture slides here, or leave blank to generate from topic directly.",
        height=90
    )

    card_count = st.slider("Number of Flashcards", 3, 12, 6)

    if st.button("✨ Generate Flashcards", type="primary"):
        source = notes_input.strip() if notes_input.strip() else f"{subject}: {topic}"
        with st.spinner("AI is extracting core definitions and active recall questions..."):
            st.session_state.flashcard_pool = generate_flashcards(source, card_count)
            st.session_state.flashcard_index = 0
            st.session_state.flashcard_flipped = False

    cards = st.session_state.get("flashcard_pool")
    if cards:
        idx = st.session_state.get("flashcard_index", 0)
        total_c = len(cards)
        current_card = cards[idx]

        st.markdown(f"**Card {idx + 1} of {total_c}**")
        st.progress((idx + 1) / total_c)

        # Card container
        st.markdown(f"""
        <div class="flashcard">
            <span style="font-size: 0.85rem; font-weight: 700; color: #2563eb; text-transform: uppercase;">
                {'FRONT · QUESTION' if not st.session_state.get('flashcard_flipped') else 'BACK · ANSWER & INSIGHT'}
            </span>
            <h2 style="color: #0f172a; margin: 1.2rem 0; font-size: 1.35rem; font-weight: 700;">
                {current_card['front'] if not st.session_state.get('flashcard_flipped') else current_card['back']}
            </h2>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            if st.button("🔄 Flip Card", use_container_width=True):
                st.session_state.flashcard_flipped = not st.session_state.get("flashcard_flipped", False)
                st.rerun()
        with col_f2:
            if st.button("⬅️ Previous Card", disabled=(idx == 0), use_container_width=True):
                st.session_state.flashcard_index -= 1
                st.session_state.flashcard_flipped = False
                st.rerun()
        with col_f3:
            if st.button("Next Card ➡️", disabled=(idx == total_c - 1), use_container_width=True):
                st.session_state.flashcard_index += 1
                st.session_state.flashcard_flipped = False
                st.rerun()

# =========================================================================
# PAGE 7: PROGRESS & DETAILED ANALYTICS
# =========================================================================
elif page == "📈 Progress & Analytics":
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="margin: 0; color: #1e3a8a;">📈 Detailed Learning Analytics</h2>
        <p style="color: #64748b; margin-top: 0.2rem;">
            Deep-dive into your cognitive trajectory, accuracy curves, and weak points.
        </p>
    </div>
    """, unsafe_allow_html=True)

    results = get_results(user["id"])
    if not results:
        st.info("No quiz attempts recorded yet. Take an adaptive quiz to populate your analytics charts!")
    else:
        summary = build_progress_summary(results)

        # Tabs for analytics views
        tab_topic, tab_timeline, tab_acc, tab_raw = st.tabs([
            "📊 Topic Mastery",
            "📈 Progress Timeline",
            "🎯 Accuracy Breakdown",
            "📋 Quiz Logs"
        ])

        with tab_topic:
            st.subheader("Topic Performance vs 80% Mastery Benchmark")
            topic_stats = get_topic_stats(user["id"])
            if topic_stats:
                bar_fig = create_topic_bar_chart(topic_stats)
                if bar_fig:
                    st.plotly_chart(bar_fig, use_container_width=True)
            else:
                st.write("Take more topic assessments to view comparison bars.")

        with tab_timeline:
            st.subheader("Accuracy Trajectory Over Time")
            timeline_fig = create_progress_timeline(results)
            if timeline_fig:
                st.plotly_chart(timeline_fig, use_container_width=True)

        with tab_acc:
            st.subheader("Overall Accuracy Ratio")
            col_donut, col_info = st.columns([1, 1])
            with col_donut:
                donut_fig = create_accuracy_donut(summary)
                if donut_fig:
                    st.plotly_chart(donut_fig, use_container_width=True)
            with col_info:
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 1.5rem;">
                    <h4>Summary Statistics</h4>
                    <p>• <strong>Total Questions Answered:</strong> {summary['total_questions']}</p>
                    <p>• <strong>Total Correct Answers:</strong> {summary['total_correct']}</p>
                    <p>• <strong>Overall Accuracy:</strong> {summary['accuracy']:.1f}%</p>
                    <p>• <strong>Highest Single Quiz Score:</strong> {summary['highest_score']:.1f}%</p>
                    <p>• <strong>Mastery Experience:</strong> {summary['xp']} XP ({summary['level']})</p>
                </div>
                """, unsafe_allow_html=True)

        with tab_raw:
            st.subheader("Detailed Quiz Session History")
            df_results = pd.DataFrame(results)
            if not df_results.empty:
                display_cols = ["topic", "subject", "difficulty", "score", "correct_count", "total_questions", "time_taken_seconds", "created_at"]
                available_cols = [c for c in display_cols if c in df_results.columns]
                st.dataframe(df_results[available_cols], use_container_width=True, hide_index=True)

# =========================================================================
# PAGE 8: PROFILE & GOALS
# =========================================================================
elif page == "⚙️ Profile & Goals":
    st.markdown("""
    <div style="margin-bottom: 1.2rem;">
        <h2 style="margin: 0; color: #1e3a8a;">⚙️ Student Profile & Personalization Settings</h2>
        <p style="color: #64748b; margin-top: 0.2rem;">
            Tune your learning engine parameters, pace, target exams, and study goals.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("profile_form"):
        p_name = st.text_input("Full Name", value=student_profile.get("name", ""))
        p_email = st.text_input("Email", value=student_profile.get("email", ""), disabled=True)

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            p_avatar = st.selectbox("Avatar Icon", ["🎓", "🚀", "💡", "🧠", "⚡", "🔬", "💻", "📚"], index=0)
            p_target = st.selectbox(
                "Target Curriculum / Exam Goal",
                [
                    "Software Engineering & AI",
                    "Data Science & Machine Learning",
                    "Computer Science Fundamentals",
                    "Competitive Exams & GATE",
                    "Web Development Mastery"
                ],
                index=0
            )
        with col_p2:
            p_pace = st.selectbox(
                "Learning Pace",
                [
                    "Standard / Balanced",
                    "Deep & Foundational (Step-by-step)",
                    "Accelerated / Fast-Paced"
                ],
                index=0
            )
            p_goal_mins = st.number_input("Daily Target Study Time (Minutes)", min_value=15, max_value=360, value=student_profile.get("daily_goal_minutes", 45), step=15)

        p_bio = st.text_area("Personal Learning Bio / Motivation", value=student_profile.get("bio", "Ready to learn with AI."))

        save_profile = st.form_submit_button("Save Profile Settings", type="primary")
        if save_profile:
            update_student_profile(user["id"], p_name, p_target, p_pace, p_goal_mins, p_avatar, p_bio)
            st.session_state.user["name"] = p_name
            st.session_state.user["avatar"] = p_avatar
            st.success("Profile preferences updated successfully!")
            st.rerun()

    # Add custom topic section
    st.markdown("---")
    st.subheader("➕ Add Custom Study Topic")
    st.caption("Expand the platform curriculum by registering custom topics for your courses:")
    col_add1, col_add2 = st.columns(2)
    with col_add1:
        add_subj = st.selectbox("Under Subject", subject_names, key="add_topic_subj")
    with col_add2:
        new_topic_name = st.text_input("New Topic Name", placeholder="e.g. Memory Management & Paging")

    if st.button("Add Topic to Platform"):
        if new_topic_name.strip():
            subj_id = subject_map[add_subj]
            success = add_custom_topic(subj_id, new_topic_name.strip())
            if success:
                st.success(f"Added '{new_topic_name.strip()}' under '{add_subj}'.")
                st.rerun()
            else:
                st.error("Failed to add topic. Topic might already exist.")
        else:
            st.warning("Please enter a valid topic name.")

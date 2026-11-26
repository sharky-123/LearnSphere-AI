# 🎓 LearnSphere AI – Personalized Adaptive Learning Platform

LearnSphere AI is an intelligent, Generative AI-powered adaptive educational platform designed to personalize learning, diagnose weak subjects, generate adaptive quizzes with real-time difficulty adjustment, deliver structured step-by-step concept explanations, and build customized daily study timetables.

---

## 📌 Problem Statement & Motivation
Traditional learning platforms deliver identical static content and assessments to all students regardless of their individual learning pace, prior knowledge, strengths, or weaknesses. LearnSphere AI solves this by continuously modeling student performance and adapting learning content, difficulty, and study schedules to each student's unique cognitive profile.

---

## 🚀 Key Features

1. **Student Profile Creation & Persona Customization**:
   - Secure student registration, password hashing (PBKDF2-HMAC-SHA256), and session authentication.
   - Customizable learning paces (*Deep & Foundational*, *Standard / Balanced*, *Accelerated / Fast-Paced*).
   - Target curriculum and exam selection (Software Engineering, Data Science, GATE, Web Dev).
   - Daily study goals (minutes) and avatar customization.

2. **⚡ Real-Time Adaptive Quiz Engine (Difficulty Adjustment Based on Previous Answers)**:
   - Dynamic assessment where questions adjust difficulty dynamically:
     - Answering correctly scales difficulty up (Easy ➔ Medium ➔ Hard).
     - Answering incorrectly scales difficulty down to diagnose foundational misconceptions.
   - Real-time difficulty badges, live progress trajectory, and post-session mastery breakdowns.

3. **📝 Comprehensive Topic Assessments**:
   - Topic-specific quizzes with configurable question counts (3–10) and difficulty levels.
   - Detailed rationale and explanation for all options (correct and incorrect distractors).

4. **💬 AI Learning Tutor (LangChain & Gemini API)**:
   - Multi-level concept explanations (Beginner/Intuitive, Intermediate/Applied, Advanced/In-Depth).
   - Pedagogical structure: Core concept summary, intuitive analogy, code walkthrough, common pitfalls, and quick retention check.
   - One-click "Save to My Notes" functionality.

5. **📅 Automatic Study Timetable Generator**:
   - Automatically detects the student's identified weak areas (< 60% accuracy).
   - Generates a day-by-day timetable based on available hours per day and target exam date.
   - Interactive task tracker with clickable checkboxes to track completed sessions.

6. **📊 Interactive Performance Analytics & Weakness Detection (Plotly & Pandas)**:
   - Multi-subject Mastery Radar (Spider) chart comparing student accuracy against the 80% benchmark.
   - Topic Performance Bar Chart color-coded by mastery:
     - 🔴 Weak (< 60% accuracy) — flags priority remediation.
     - 🟡 Developing (60–80% accuracy) — intermediate problem drill.
     - 🟢 Mastered (> 80% accuracy) — strong retention.
   - Score trajectory timeline with 3-quiz rolling average.
   - Accuracy ratio donut chart, study streak tracker (🔥), and XP / Level badge system.

7. **🗂️ AI Flashcards & Active Recall**:
   - Generates active recall flashcards from concepts or custom pasted lecture notes.
   - Interactive flip-card interface with navigation and progress indicators.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | Streamlit, Custom Modern Responsive CSS |
| **Backend & Core** | Python 3.10+, SQLite3 |
| **AI & Orchestration** | Google Gemini API (`google-genai`), LangChain (`langchain-core` PromptTemplates) |
| **Data & Visualization** | Pandas, Plotly Express & Graph Objects |
| **Security & Utilities** | Python `hashlib` (PBKDF2), `python-dotenv` |

---

## 📂 Project Architecture

```
LearnSphere_AI/
│
├── app.py                      # Main Streamlit application & navigation router
├── requirements.txt            # Python dependencies
├── .env.example                # Sample environment configuration
├── README.md                   # Project documentation
│
├── modules/
│   ├── __init__.py
│   ├── database.py             # SQLite schema, user auth, and progress persistence
│   ├── ai_engine.py            # LangChain prompts & Gemini API integration with demo fallback
│   └── analytics.py            # Plotly charts, weak area detection & XP calculation
│
└── database/
    └── learnsphere.db          # Auto-generated SQLite database
```

---

## ⚙️ Local Setup & Execution Guide

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Git (optional)

### 2. Activate Virtual Environment
From inside the `LearnSphere_AI` directory:

```powershell
# Windows PowerShell
.\venv\Scripts\activate
```

*(Or create a new venv if needed: `python -m venv venv`)*

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Gemini API (Optional)
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Edit `.env` and insert your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```
> *Note: If no API key is provided, LearnSphere AI operates seamlessly in **Offline Curriculum Mode**, serving pre-built curriculum question banks and structured timetables.*

### 5. Launch the Application
```powershell
streamlit run app.py
```

Open your browser to `http://localhost:8501`.

---

## 🧪 Demonstration Walkthrough

1. **Sign Up**: Register a student account with your name, email, target curriculum, and learning pace.
2. **Take an Adaptive Quiz**: Go to `⚡ Adaptive Quiz`, pick a topic, and observe how answering correctly increases question difficulty in real time.
3. **Inspect Dashboard**: Go to `📊 Dashboard` to see your updated XP, study streak, weak area recommendations, and multi-subject radar.
4. **Generate Study Timetable**: Go to `📅 Study Timetable` to produce an automatic schedule remediating your detected weak points.
5. **Ask AI Tutor**: Go to `💬 AI Tutor` to ask any technical question at Beginner, Intermediate, or Advanced depth.
6. **Practice with Flashcards**: Go to `🗂️ AI Flashcards` to flip through active recall cards.

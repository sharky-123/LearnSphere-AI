import sqlite3, hashlib, json
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "learnsphere.db"
DB_PATH.parent.mkdir(exist_ok=True)

SEED = {
    "Python Programming": [
        "Variables & Data Types",
        "Control Flow & Loops",
        "Functions & Scope",
        "Object-Oriented Programming (OOP)",
        "Data Structures (Lists, Dicts, Sets)",
        "Exception Handling & File I/O",
        "Generators & Decorators"
    ],
    "Data Structures & Algorithms": [
        "Arrays & Strings",
        "Linked Lists",
        "Stacks & Queues",
        "Binary Trees & BST",
        "Graphs & Graph Traversals",
        "Searching & Sorting Algorithms",
        "Dynamic Programming & Recursion"
    ],
    "Database Management (DBMS)": [
        "Relational Model & Keys",
        "ER Modeling & Schema Design",
        "SQL Queries & Joins",
        "Database Normalization (1NF to BCNF)",
        "Transactions & ACID Properties",
        "Concurrency Control & Indexing"
    ],
    "Generative AI & LLMs": [
        "Foundations of LLMs & Transformers",
        "Prompt Engineering Strategies",
        "Text Embeddings & Vector Stores",
        "Retrieval-Augmented Generation (RAG)",
        "AI Agents & Tool Calling",
        "Evaluation & Fine-Tuning"
    ],
    "Machine Learning Essentials": [
        "Supervised vs Unsupervised Learning",
        "Linear & Logistic Regression",
        "Decision Trees & Random Forests",
        "Neural Networks & Deep Learning",
        "Model Evaluation (Precision, Recall, ROC)"
    ],
    "Web Development Foundations": [
        "HTML5 & Semantic Structure",
        "CSS3 Layouts & Flexbox/Grid",
        "JavaScript ES6+ Fundamentals",
        "REST APIs & Client-Server Architecture",
        "Authentication & Security Basics"
    ]
}

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS students(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            target_exam TEXT DEFAULT 'Software Engineering & AI',
            learning_pace TEXT DEFAULT 'Standard / Balanced',
            daily_goal_minutes INTEGER DEFAULT 45,
            avatar TEXT DEFAULT '🎓',
            bio TEXT DEFAULT 'Ready to learn and master new skills with AI.',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS subjects(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS topics(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            UNIQUE(subject_id, name),
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        );

        CREATE TABLE IF NOT EXISTS quiz_results(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            topic_id INTEGER NOT NULL,
            score REAL NOT NULL,
            total_questions INTEGER NOT NULL,
            correct_count INTEGER NOT NULL DEFAULT 0,
            difficulty TEXT DEFAULT 'Medium',
            time_taken_seconds INTEGER DEFAULT 0,
            details TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(topic_id) REFERENCES topics(id)
        );

        CREATE TABLE IF NOT EXISTS study_plans(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            topic_id INTEGER,
            goal TEXT,
            daily_hours REAL DEFAULT 2.0,
            duration_days INTEGER DEFAULT 7,
            content TEXT NOT NULL,
            schedule_json TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS student_notes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            topic TEXT,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );
        """)

        # Migration helper for older schemas if columns don't exist
        existing_cols = [c["name"] for c in con.execute("PRAGMA table_info(students)").fetchall()]
        for col_name, col_type, col_def in [
            ("target_exam", "TEXT", "'Software Engineering & AI'"),
            ("learning_pace", "TEXT", "'Standard / Balanced'"),
            ("daily_goal_minutes", "INTEGER", "45"),
            ("avatar", "TEXT", "'🎓'"),
            ("bio", "TEXT", "'Ready to learn and master new skills with AI.'")
        ]:
            if col_name not in existing_cols:
                try:
                    con.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type} DEFAULT {col_def}")
                except Exception:
                    pass

        existing_quiz_cols = [c["name"] for c in con.execute("PRAGMA table_info(quiz_results)").fetchall()]
        for col_name, col_type, col_def in [
            ("correct_count", "INTEGER", "0"),
            ("difficulty", "TEXT", "'Medium'"),
            ("time_taken_seconds", "INTEGER", "0")
        ]:
            if col_name not in existing_quiz_cols:
                try:
                    con.execute(f"ALTER TABLE quiz_results ADD COLUMN {col_name} {col_type} DEFAULT {col_def}")
                except Exception:
                    pass

        existing_plan_cols = [c["name"] for c in con.execute("PRAGMA table_info(study_plans)").fetchall()]
        for col_name, col_type, col_def in [
            ("daily_hours", "REAL", "2.0"),
            ("duration_days", "INTEGER", "7"),
            ("schedule_json", "TEXT", "NULL")
        ]:
            if col_name not in existing_plan_cols:
                try:
                    con.execute(f"ALTER TABLE study_plans ADD COLUMN {col_name} {col_type} DEFAULT {col_def}")
                except Exception:
                    pass

        for subject, topics in SEED.items():
            con.execute("INSERT OR IGNORE INTO subjects(name) VALUES(?)", (subject,))
            sid = con.execute("SELECT id FROM subjects WHERE name=?", (subject,)).fetchone()["id"]
            for topic in topics:
                con.execute("INSERT OR IGNORE INTO topics(subject_id, name) VALUES(?,?)", (sid, topic))

def _hash(password):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"learnsphere_salt_v1", 120000).hex()

def create_user(name, email, password, target_exam="Software Engineering & AI", learning_pace="Standard / Balanced"):
    if not name or not email or not password:
        return False, "Please complete all required fields."
    if len(password) < 6:
        return False, "Password must contain at least 6 characters."
    try:
        with connect() as con:
            con.execute(
                """INSERT INTO students(name, email, password_hash, target_exam, learning_pace, created_at)
                   VALUES(?, ?, ?, ?, ?, ?)""",
                (name, email.strip().lower(), _hash(password), target_exam, learning_pace, datetime.now().isoformat(timespec="seconds"))
            )
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "This email is already registered."

def authenticate_user(email, password):
    with connect() as con:
        row = con.execute(
            """SELECT id, name, email, password_hash, target_exam, learning_pace, daily_goal_minutes, avatar, bio
               FROM students WHERE email=?""",
            (email.strip().lower(),)
        ).fetchone()
    if row and row["password_hash"] == _hash(password):
        return {
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "target_exam": row["target_exam"] or "Software Engineering & AI",
            "learning_pace": row["learning_pace"] or "Standard / Balanced",
            "daily_goal_minutes": row["daily_goal_minutes"] or 45,
            "avatar": row["avatar"] or "🎓",
            "bio": row["bio"] or ""
        }
    return None

def get_student_profile(student_id):
    with connect() as con:
        row = con.execute(
            """SELECT id, name, email, target_exam, learning_pace, daily_goal_minutes, avatar, bio, created_at
               FROM students WHERE id=?""",
            (student_id,)
        ).fetchone()
    return dict(row) if row else None

def update_student_profile(student_id, name, target_exam, learning_pace, daily_goal_minutes, avatar, bio):
    with connect() as con:
        con.execute(
            """UPDATE students
               SET name=?, target_exam=?, learning_pace=?, daily_goal_minutes=?, avatar=?, bio=?
               WHERE id=?""",
            (name, target_exam, learning_pace, daily_goal_minutes, avatar, bio, student_id)
        )
    return True

def get_subjects():
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM subjects ORDER BY name")]

def get_topics(subject_id):
    with connect() as con:
        return [dict(r) for r in con.execute("SELECT * FROM topics WHERE subject_id=? ORDER BY name", (subject_id,))]

def add_custom_topic(subject_id, topic_name):
    if not topic_name or not topic_name.strip():
        return False
    try:
        with connect() as con:
            con.execute("INSERT OR IGNORE INTO topics(subject_id, name) VALUES(?, ?)", (subject_id, topic_name.strip()))
        return True
    except Exception:
        return False

def save_quiz_result(student_id, topic_id, score, total, correct_count, difficulty="Medium", time_taken=0, details=None):
    with connect() as con:
        con.execute(
            """INSERT INTO quiz_results(student_id, topic_id, score, total_questions, correct_count, difficulty, time_taken_seconds, details, created_at)
               VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                student_id,
                topic_id,
                score,
                total,
                correct_count,
                difficulty,
                time_taken,
                json.dumps(details or []),
                datetime.now().isoformat(timespec="seconds")
            )
        )

def get_results(student_id):
    with connect() as con:
        rows = con.execute(
            """SELECT qr.id, qr.score, qr.total_questions, qr.correct_count, qr.difficulty,
                      qr.time_taken_seconds, qr.created_at, qr.details,
                      t.name AS topic, s.name AS subject, s.id AS subject_id, t.id AS topic_id
               FROM quiz_results qr
               JOIN topics t ON qr.topic_id = t.id
               JOIN subjects s ON t.subject_id = s.id
               WHERE qr.student_id = ?
               ORDER BY qr.created_at DESC""",
            (student_id,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_topic_stats(student_id):
    with connect() as con:
        rows = con.execute(
            """SELECT t.id AS topic_id, t.name AS topic, s.name AS subject,
                      COUNT(qr.id) AS attempts,
                      AVG(qr.score) AS average,
                      MAX(qr.score) AS high_score,
                      SUM(qr.correct_count) AS total_correct,
                      SUM(qr.total_questions) AS total_answered
               FROM quiz_results qr
               JOIN topics t ON qr.topic_id = t.id
               JOIN subjects s ON t.subject_id = s.id
               WHERE qr.student_id = ?
               GROUP BY t.id
               ORDER BY average ASC""",
            (student_id,)
        ).fetchall()
    return [dict(r) for r in rows]

def get_subject_stats(student_id):
    with connect() as con:
        rows = con.execute(
            """SELECT s.id AS subject_id, s.name AS subject,
                      COUNT(qr.id) AS attempts,
                      AVG(qr.score) AS average,
                      SUM(qr.correct_count) AS total_correct,
                      SUM(qr.total_questions) AS total_questions
               FROM quiz_results qr
               JOIN topics t ON qr.topic_id = t.id
               JOIN subjects s ON t.subject_id = s.id
               WHERE qr.student_id = ?
               GROUP BY s.id
               ORDER BY average ASC""",
            (student_id,)
        ).fetchall()
    return [dict(r) for r in rows]

def save_study_plan(student_id, topic_id, goal, daily_hours, duration_days, content, schedule_json=None):
    with connect() as con:
        cursor = con.execute(
            """INSERT INTO study_plans(student_id, topic_id, goal, daily_hours, duration_days, content, schedule_json, created_at)
               VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                student_id,
                topic_id,
                goal,
                daily_hours,
                duration_days,
                content,
                json.dumps(schedule_json) if schedule_json else None,
                datetime.now().isoformat(timespec="seconds")
            )
        )
        return cursor.lastrowid

def update_timetable_task(plan_id, task_id, is_completed):
    with connect() as con:
        row = con.execute("SELECT schedule_json FROM study_plans WHERE id=?", (plan_id,)).fetchone()
        if row and row["schedule_json"]:
            try:
                schedule = json.loads(row["schedule_json"])
                for item in schedule:
                    if item.get("id") == task_id:
                        item["completed"] = is_completed
                con.execute("UPDATE study_plans SET schedule_json=? WHERE id=?", (json.dumps(schedule), plan_id))
                return True
            except Exception:
                pass
    return False

def get_study_plans(student_id):
    with connect() as con:
        rows = con.execute(
            """SELECT sp.id, sp.goal, sp.daily_hours, sp.duration_days, sp.content,
                      sp.schedule_json, sp.created_at, t.name AS topic, s.name AS subject
               FROM study_plans sp
               LEFT JOIN topics t ON sp.topic_id = t.id
               LEFT JOIN subjects s ON t.subject_id = s.id
               WHERE sp.student_id = ?
               ORDER BY sp.id DESC""",
            (student_id,)
        ).fetchall()
    return [dict(r) for r in rows]

def delete_study_plan(plan_id, student_id):
    with connect() as con:
        con.execute("DELETE FROM study_plans WHERE id=? AND student_id=?", (plan_id, student_id))
    return True

def save_student_note(student_id, title, topic, content):
    with connect() as con:
        con.execute(
            """INSERT INTO student_notes(student_id, title, topic, content, created_at)
               VALUES(?, ?, ?, ?, ?)""",
            (student_id, title, topic, content, datetime.now().isoformat(timespec="seconds"))
        )

def get_student_notes(student_id):
    with connect() as con:
        rows = con.execute(
            """SELECT id, title, topic, content, created_at
               FROM student_notes WHERE student_id=? ORDER BY id DESC""",
            (student_id,)
        ).fetchall()
    return [dict(r) for r in rows]

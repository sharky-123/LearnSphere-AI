import os, sys
from pathlib import Path

# Set up project root in path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=== Starting LearnSphere AI Comprehensive Verification ===")

# 1. Test Database Module
print("\n[1/4] Testing modules.database...")
from modules.database import (
    init_db, create_user, authenticate_user, get_student_profile, update_student_profile,
    get_subjects, get_topics, add_custom_topic, save_quiz_result, get_results,
    get_topic_stats, get_subject_stats, save_study_plan, get_study_plans,
    update_timetable_task, save_student_note, get_student_notes
)

init_db()
print(" -> Database initialized successfully.")

# Test user creation
test_email = "test_student@example.com"
test_pass = "secret123"
ok, msg = create_user("Test Student", test_email, test_pass, "Software Engineering & AI", "Standard / Balanced")
print(f" -> create_user: ok={ok}, msg='{msg}'")

user = authenticate_user(test_email, test_pass)
assert user is not None, "Authentication failed for newly created user!"
print(f" -> authenticate_user successful: ID={user['id']}, Name={user['name']}")

# Test profile update
update_ok = update_student_profile(user["id"], "Test Student Pro", "Data Science & AI", "Accelerated / Fast-Paced", 60, "🚀", "Learning AI everyday.")
assert update_ok, "update_student_profile failed!"
profile = get_student_profile(user["id"])
assert profile["target_exam"] == "Data Science & AI"
print(" -> Profile retrieved & verified successfully.")

# Test subjects & topics
subjects = get_subjects()
assert len(subjects) >= 4, f"Expected at least 4 subjects, got {len(subjects)}"
sub_id = subjects[0]["id"]
topics = get_topics(sub_id)
assert len(topics) >= 3, f"Expected at least 3 topics for {subjects[0]['name']}, got {len(topics)}"
top_id = topics[0]["id"]
print(f" -> Found {len(subjects)} subjects and {len(topics)} topics in '{subjects[0]['name']}'.")

# Test custom topic addition
custom_ok = add_custom_topic(sub_id, "Test Automation & CI/CD")
print(f" -> add_custom_topic: {custom_ok}")

# Test saving quiz results
save_quiz_result(
    user["id"],
    top_id,
    score=80.0,
    total=5,
    correct_count=4,
    difficulty="Medium",
    time_taken=45,
    details=[{"question": "Q1", "selected": "A", "correct": "A", "is_correct": True}]
)
# Save another with lower score to test weakness detection
if len(topics) > 1:
    save_quiz_result(
        user["id"],
        topics[1]["id"],
        score=40.0,
        total=5,
        correct_count=2,
        difficulty="Adaptive",
        time_taken=60,
        details=[{"question": "Q2", "selected": "B", "correct": "C", "is_correct": False}]
    )

results = get_results(user["id"])
assert len(results) >= 2, f"Expected at least 2 results, got {len(results)}"
print(f" -> Saved and retrieved {len(results)} quiz results.")

topic_stats = get_topic_stats(user["id"])
assert len(topic_stats) >= 2
subject_stats = get_subject_stats(user["id"])
assert len(subject_stats) >= 1
print(f" -> Topic stats count: {len(topic_stats)}, Subject stats count: {len(subject_stats)}")

# Test study plans & timetable
plan_id = save_study_plan(
    user["id"],
    top_id,
    goal="Master Python data structures",
    daily_hours=2.0,
    duration_days=7,
    content="## Study Plan Overview",
    schedule_json=[{"id": "day1_task1", "day": 1, "title": "Review Concepts", "completed": False}]
)
assert plan_id is not None
update_timetable_task(plan_id, "day1_task1", True)
plans = get_study_plans(user["id"])
assert len(plans) >= 1
print(f" -> Saved study plan ID={plan_id}, updated task status, retrieved {len(plans)} plans.")

# Test student notes
save_student_note(user["id"], "Hash Table Collisions", "Data Structures", "Open addressing vs separate chaining.")
notes = get_student_notes(user["id"])
assert len(notes) >= 1
print(f" -> Saved and retrieved {len(notes)} student notes.")

# 2. Test Analytics Module
print("\n[2/4] Testing modules.analytics...")
from modules.analytics import (
    build_progress_summary, recommend_topics, create_radar_mastery_chart,
    create_topic_bar_chart, create_progress_timeline, create_accuracy_donut
)

summary = build_progress_summary(results)
assert summary["attempts"] >= 2
assert summary["xp"] > 0
print(f" -> Progress summary: {summary['attempts']} attempts, {summary['average']:.1f}% avg, Level: {summary['level']}, XP: {summary['xp']}")

recommendations = recommend_topics(topic_stats)
assert len(recommendations) >= 2
# Verify weak topic detected
weak = [r for r in recommendations if r["average"] < 60]
assert len(weak) >= 1, "Weak topic was not flagged correctly!"
print(f" -> Weakness detection passed: Found weak topic '{weak[0]['topic']}' ({weak[0]['average']}%) flagged with action: '{weak[0]['action']}'")

# Test chart generation
bar_chart = create_topic_bar_chart(topic_stats)
assert bar_chart is not None
timeline_chart = create_progress_timeline(results)
assert timeline_chart is not None
donut_chart = create_accuracy_donut(summary)
assert donut_chart is not None
radar_chart = create_radar_mastery_chart(subject_stats)
print(" -> All Plotly charts (Bar, Timeline, Donut, Radar) generated successfully.")

# 3. Test AI Engine Module
print("\n[3/4] Testing modules.ai_engine...")
from modules.ai_engine import (
    generate_explanation, generate_quiz, generate_adaptive_single_question,
    generate_study_timetable, generate_flashcards, is_ai_connected
)

print(f" -> is_ai_connected: {is_ai_connected()}")

# Test explanation
explanation = generate_explanation("Explain QuickSort partitioning", "Intermediate", "Data Structures & Algorithms", "Searching & Sorting")
assert explanation and len(explanation) > 50
print(f" -> generate_explanation generated {len(explanation)} chars of pedagogical text.")

# Test quiz generation
quiz = generate_quiz("Functions & Scope", "Python Programming", "Medium", 3)
assert len(quiz) == 3, f"Expected 3 questions, got {len(quiz)}"
assert len(quiz[0]["options"]) == 4
assert quiz[0]["answer"] in quiz[0]["options"]
print(" -> generate_quiz generated 3 valid 4-option MCQs with answers and explanations.")

# Test adaptive single question
q_adaptive = generate_adaptive_single_question("Variables & Data Types", "Python Programming", "Hard", 1, True)
assert q_adaptive and len(q_adaptive["options"]) == 4
assert q_adaptive["difficulty"] == "Hard"
print(" -> generate_adaptive_single_question produced valid adaptive question card.")

# Test study timetable generator
tt = generate_study_timetable("Python Programming", "Functions & Scope", 2.0, 7, "Exam prep", ["Variables"])
assert "markdown_overview" in tt
assert "tasks" in tt
assert len(tt["tasks"]) >= 7
print(f" -> generate_study_timetable produced plan with {len(tt['tasks'])} scheduled task items.")

# Test flashcards
cards = generate_flashcards("Recursion has base cases and recursive steps.", 4)
assert len(cards) == 4
assert "front" in cards[0] and "back" in cards[0]
print(f" -> generate_flashcards produced {len(cards)} active recall cards.")

# 4. Streamlit App Syntax & Import Check
print("\n[4/4] Testing app.py syntax...")
import py_compile
py_compile.compile(str(project_root / "app.py"), doraise=True)
print(" -> app.py compiled with zero syntax errors.")

print("\n========================================================")
print("🎉 ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
print("========================================================")
sys.exit(0)

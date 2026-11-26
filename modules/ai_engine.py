import os, json, re
from dotenv import load_dotenv

# LangChain components
from langchain_core.prompts import PromptTemplate
from google import genai

load_dotenv()

def _client():
    key = os.getenv("GEMINI_API_KEY")
    if key and key.strip() and key != "your_gemini_api_key_here":
        try:
            return genai.Client(api_key=key.strip())
        except Exception:
            return None
    return None

def _ask(prompt_text):
    client = _client()
    if not client:
        return None
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    try:
        response = client.models.generate_content(model=model_name, contents=prompt_text)
        return response.text or ""
    except Exception as e:
        print(f"[LearnSphere AI Engine Warning] Gemini API call failed: {e}")
        return None

def _json_from_text(text):
    if not text:
        return None
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.S)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return None
    return None

def is_ai_connected():
    client = _client()
    return client is not None

# =========================================================================
# 1. AI Personalized Concept Explanation (LangChain PromptTemplate)
# =========================================================================

EXPLANATION_TEMPLATE = """You are LearnSphere AI, a world-class adaptive educational tutor.
A student needs an intuitive, personalized explanation tailored to their profile and understanding level.

Student Profile:
- Understanding Level: {level}
- Learning Pace: {pace}
- Subject: {subject}
- Focus Topic: {topic}

Student Question / Concept:
{question}

Instructions:
1. Explain clearly in Markdown using a supportive, encouraging tone.
2. Structure your response with:
   - 🎯 **Core Concept in Plain English** (1-2 sentences)
   - 💡 **Intuitive Analogy or Real-World Example**
   - 🔍 **Deep Dive / Step-by-Step Breakdown** (with clean syntax-highlighted code if programming-related)
   - ⚠️ **Common Pitfalls & Mistakes Students Make**
   - 🧠 **Quick Check / Food for Thought Question**
3. Match the complexity to the '{level}' level and '{pace}' pace.
"""

def generate_explanation(question, level="Beginner", subject="General", topic="General", pace="Standard / Balanced"):
    prompt = PromptTemplate(
        input_variables=["level", "pace", "subject", "topic", "question"],
        template=EXPLANATION_TEMPLATE
    ).format(level=level, pace=pace, subject=subject, topic=topic, question=question)

    result = _ask(prompt)
    if result:
        return result

    # Offline high-quality fallback explanation
    return f"""### 🎯 Core Concept: {topic}
**Question:** *{question}*

In the context of **{subject}**, **{topic}** is a foundational building block.
At the **{level}** level, the best way to understand this is to break down the mechanism:

---

### 💡 Intuitive Analogy
Imagine organizing a physical library or a high-efficiency kitchen:
- Inputs are carefully structured and cataloged.
- Deterministic rules transform requirements into predictable outputs.
- Redundant overhead is eliminated to ensure optimal performance.

---

### 🔍 Step-by-Step Breakdown
1. **Foundation & Setup:** Understand the prerequisite states and types involved.
2. **Execution Flow:** Follow the lifecycle step-by-step from initialization to termination.
3. **Best Practices:** Maintain modularity, keep abstractions clean, and handle edge cases proactively.

```python
# Illustrative Python example for {topic}
def demonstrate_concept(data_input):
    # Process input according to {topic} principles
    processed = [x * 2 for x in data_input if x is not None]
    return {{"status": "success", "result": processed}}

sample_data = [1, 2, 3, 4]
print(demonstrate_concept(sample_data))
```

---

### ⚠️ Common Pitfalls to Avoid
- **Off-by-one or boundary mistakes:** Always verify edge conditions (empty inputs, zero, maximum ranges).
- **Ignoring scope and mutation:** Be mindful of whether operations mutate data in-place or return copies.
- **Premature optimization:** Strive first for correctness and readability before optimizing performance.

---

### 🧠 Quick Check Question
*How would you handle unexpected or null input in this pattern to guarantee failure safety?*

*(💡 Note: Add your Gemini API key in `.env` to unlock dynamically customized live AI responses.)*"""

# =========================================================================
# 2. AI Adaptive Quiz Generation (Topic & Single Question)
# =========================================================================

QUIZ_PROMPT_TEMPLATE = """You are an expert exam setter in computer science and STEM education.
Generate exactly {count} multiple-choice questions (MCQs) for:
Subject: {subject}
Topic: {topic}
Target Difficulty: {difficulty}

Requirements:
- Questions must be original, high quality, and pedagogically sound.
- Include 4 plausible options for each question (A, B, C, D text strings).
- Exactly ONE unambiguous correct option.
- Provide a clear, educational explanation explaining WHY the correct option is right and why common mistakes occur.
- Return ONLY valid JSON array with no conversational markdown text.

Format:
[
  {{
    "question": "Clear question text?",
    "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
    "answer": "Option 1",
    "explanation": "Detailed explanation of why Option 1 is correct.",
    "difficulty": "{difficulty}"
  }}
]
"""

def generate_quiz(topic, subject, difficulty="Medium", count=5):
    prompt = PromptTemplate(
        input_variables=["count", "subject", "topic", "difficulty"],
        template=QUIZ_PROMPT_TEMPLATE
    ).format(count=count, subject=subject, topic=topic, difficulty=difficulty)

    raw_response = _ask(prompt)
    data = _json_from_text(raw_response)

    if isinstance(data, list):
        valid = [
            q for q in data
            if isinstance(q, dict)
            and q.get("question")
            and isinstance(q.get("options"), list)
            and len(q["options"]) == 4
            and q.get("answer") in q["options"]
        ]
        if len(valid) >= 1:
            for q in valid:
                q["difficulty"] = q.get("difficulty", difficulty)
            return valid[:count]

    return _fallback_quiz(topic, subject, difficulty, count)

def generate_adaptive_single_question(topic, subject, current_difficulty="Medium", question_number=1, previous_was_correct=None):
    """
    Generates a single question dynamically adapting to the user's latest performance.
    """
    context = ""
    if previous_was_correct is True:
        context = "The student answered the previous question CORRECTLY. Increase the cognitive depth or challenge slightly."
    elif previous_was_correct is False:
        context = "The student answered the previous question INCORRECTLY. Test a core foundational sub-concept to diagnose misconceptions."

    prompt = f"""Generate exactly 1 adaptive multiple-choice question for:
Subject: {subject}
Topic: {topic}
Difficulty: {current_difficulty}
Question #{question_number}
Pedagogical context: {context}

Return ONLY a single JSON object (not an array):
{{
  "question": "Question text here?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "Option A",
  "explanation": "Detailed explanation.",
  "difficulty": "{current_difficulty}"
}}
"""
    raw_response = _ask(prompt)
    data = _json_from_text(raw_response)
    if isinstance(data, dict) and data.get("question") and isinstance(data.get("options"), list) and len(data["options"]) == 4 and data.get("answer") in data["options"]:
        data["difficulty"] = current_difficulty
        return data

    # Fallback single question
    fallback_pool = _fallback_quiz(topic, subject, current_difficulty, 5)
    selected = fallback_pool[(question_number - 1) % len(fallback_pool)]
    selected["difficulty"] = current_difficulty
    return selected

def _fallback_quiz(topic, subject, difficulty, count):
    # Specialized curriculum banks for key topics
    banks = {
        "Python Programming": [
            ("What is the time complexity of looking up a key in a standard Python dictionary on average?",
             ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
             "O(1)",
             "Python dictionaries are implemented using hash tables, offering amortized O(1) average-time complexity for key lookups."),
            ("In Python, how are parameters passed to functions?",
             ["Pass by assignment (object reference)", "Strictly pass by value", "Strictly pass by reference", "Pass by macro substitution"],
             "Pass by assignment (object reference)",
             "Python evaluates arguments using 'call-by-object-reference'. Mutable objects can be modified, while rebinding does not affect caller scope."),
            ("Which keyword is used to create a generator function in Python?",
             ["yield", "return", "generate", "async"],
             "yield",
             "The 'yield' statement suspends function execution and returns a generator iterator value without destroying local state."),
            ("What will `bool([])` evaluate to in Python?",
             ["False", "True", "TypeError", "None"],
             "False",
             "Empty sequences such as lists, tuples, strings, and dictionaries are considered falsy in Python boolean evaluation."),
            ("What is the purpose of the `__init__` method in Python classes?",
             ["To initialize newly created instance attributes", "To allocate memory for the object", "To destroy the object", "To make a class static"],
             "To initialize newly created instance attributes",
             "`__init__` acts as the constructor method that sets up initial state once Python allocates the instance with `__new__`.")
        ],
        "Database Management (DBMS)": [
            ("Which normal form guarantees the elimination of non-trivial multivalued dependencies?",
             ["Fourth Normal Form (4NF)", "First Normal Form (1NF)", "Second Normal Form (2NF)", "Third Normal Form (3NF)"],
             "Fourth Normal Form (4NF)",
             "4NF requires the relation to be in BCNF and contain no non-trivial multivalued dependencies (X ->-> Y)."),
            ("What does the 'I' in the ACID transaction model stand for?",
             ["Isolation", "Integrity", "Iteration", "Inheritance"],
             "Isolation",
             "Isolation ensures that concurrent transactions execute without interfering with one another's intermediate states."),
            ("Which SQL clause is used to filter records resulting from a GROUP BY aggregation?",
             ["HAVING", "WHERE", "FILTER", "LIMIT"],
             "HAVING",
             "The HAVING clause filters aggregated groups, whereas WHERE filters individual rows before aggregation occurs."),
            ("Which index structure is most widely used in relational database engines for range queries?",
             ["B+ Tree", "Hash Table", "Binary Search Tree", "Linked List"],
             "B+ Tree",
             "B+ Trees maintain sorted leaf nodes linked in a doubly-linked chain, making range scans and point lookups extremely efficient."),
            ("In an Entity-Relationship (ER) model, what does a double rectangle denote?",
             ["Weak Entity Set", "Relationship Set", "Multi-valued Attribute", "Derived Attribute"],
             "Weak Entity Set",
             "A weak entity set lacks a primary key of its own and depends on an identifying relationship with an owner entity.")
        ],
        "Data Structures & Algorithms": [
            ("Which data structure uses the Last-In, First-Out (LIFO) principle?",
             ["Stack", "Queue", "Binary Tree", "Heap"],
             "Stack",
             "Stacks strictly enforce LIFO order: elements pushed last are popped first."),
            ("What is the worst-case time complexity of QuickSort?",
             ["O(n^2)", "O(n log n)", "O(n)", "O(log n)"],
             "O(n^2)",
             "QuickSort degrades to O(n^2) in the worst case when pivot selection consistently partitions into empty and n-1 sub-arrays."),
            ("In a balanced Binary Search Tree (AVL or Red-Black), what is the search complexity for n nodes?",
             ["O(log n)", "O(1)", "O(n)", "O(n log n)"],
             "O(log n)",
             "Because balanced trees guarantee height h <= c * log2(n), search operations take O(log n) time."),
            ("Which algorithm is used to find the shortest path in a graph with non-negative edge weights?",
             ["Dijkstra's Algorithm", "Kruskal's Algorithm", "Prim's Algorithm", "Breadth First Search on unweighted graphs only"],
             "Dijkstra's Algorithm",
             "Dijkstra's algorithm greedily finds single-source shortest paths on weighted directed or undirected graphs with non-negative weights."),
            ("What auxiliary space does an in-place merge sort typically require compared to standard merge sort?",
             ["Standard requires O(n); in-place aims for O(1) or O(log n)", "Both require O(1)", "Both require O(n^2)", "Standard requires O(log n)"],
             "Standard requires O(n); in-place aims for O(1) or O(log n)",
             "Standard merge sort requires an auxiliary array of size O(n) during the merge phase.")
        ],
        "Generative AI & LLMs": [
            ("What is the primary mechanism that allows Transformer models to process sequence tokens in parallel?",
             ["Self-Attention Mechanism", "Recurrent Hidden States", "Convolutional Kernels", "Gradient Boosting"],
             "Self-Attention Mechanism",
             "Self-attention computes pairwise query-key relationships across all positions simultaneously, enabling massive parallelization."),
            ("In Retrieval-Augmented Generation (RAG), what is the role of the Vector Database?",
             ["To store and retrieve semantic embeddings for knowledge augmentation", "To train model weights from scratch", "To execute Python code", "To compress model weights"],
             "To store and retrieve semantic embeddings for knowledge augmentation",
             "Vector databases perform approximate nearest neighbor (ANN) search on embeddings to supply relevant grounding context to the prompt."),
            ("What does Temperature parameter control during LLM inference?",
             ["The randomness/entropy of token sampling probabilities", "The maximum number of tokens returned", "The learning rate of the model", "The context window size"],
             "The randomness/entropy of token sampling probabilities",
             "A lower temperature flattens distribution differences towards greedy selection; higher temperature increases output variety and creativity."),
            ("Which prompt engineering technique prompts the model to provide step-by-step intermediate reasoning?",
             ["Chain-of-Thought (CoT)", "Zero-Shot Prompting", "Negative Prompting", "Prefix Tuning"],
             "Chain-of-Thought (CoT)",
             "Chain-of-Thought prompting asks the model to articulate intermediate reasoning steps before delivering the final answer."),
            ("What is 'hallucination' in the context of Large Language Models?",
             ["Generating plausible-sounding but factually incorrect or ungrounded statements", "Running out of GPU memory", "Decoding tokens backwards", "Stopping generation early"],
             "Generating plausible-sounding but factually incorrect or ungrounded statements",
             "Hallucination refers to LLM generations that appear coherent but assert incorrect, fabricated, or ungrounded facts.")
        ]
    }

    # Match subject or general fallback
    selected_pool = None
    for key, questions in banks.items():
        if key.lower() in subject.lower() or key.lower() in topic.lower():
            selected_pool = questions
            break
    if not selected_pool:
        selected_pool = banks["Python Programming"]

    results = []
    for i in range(count):
        item = selected_pool[i % len(selected_pool)]
        results.append({
            "question": f"[{difficulty}] {item[0]}",
            "options": list(item[1]),
            "answer": item[2],
            "explanation": item[3],
            "difficulty": difficulty
        })
    return results

# =========================================================================
# 3. Automatic Study Timetable & Schedule Generator
# =========================================================================

TIMETABLE_PROMPT_TEMPLATE = """You are an expert academic curriculum architect.
Create a personalized, highly structured {duration_days}-day study timetable for a student.

Parameters:
- Subject: {subject}
- Primary Focus Topic: {topic}
- Daily Available Hours: {daily_hours} hours/day
- Student Learning Pace: {pace}
- Student Target Goal: {goal}
- Identified Weak Sub-Topics to Remediate: {weak_topics}

Format Requirements:
Output valid JSON object with two top-level keys:
1. "markdown_overview": A motivating markdown study plan with strategic study tips, milestones, and review schedule.
2. "tasks": An array of discrete, schedule items matching the {duration_days} days.

Each task in "tasks" must have:
- "id": unique string like "day1_task1"
- "day": integer (1 to {duration_days})
- "time_slot": string like "Morning (09:00 - 10:30)" or "Evening (19:00 - 20:30)"
- "activity_type": one of ["Concept Theory", "Coding / Hands-on Practice", "Flashcards & Recall", "Adaptive Quiz Assessment", "Weak Area Drill"]
- "title": concise task title
- "description": specific actionable instructions
- "duration_minutes": integer
- "completed": false

Return ONLY raw JSON with no extra commentary.
"""

def generate_study_timetable(subject, topic, daily_hours=2.0, duration_days=7, goal="Master core concepts", weak_topics=None, pace="Standard / Balanced"):
    weak_str = ", ".join(weak_topics) if weak_topics else "None identified yet (reinforce core foundations)"
    prompt = PromptTemplate(
        input_variables=["subject", "topic", "daily_hours", "duration_days", "goal", "weak_topics", "pace"],
        template=TIMETABLE_PROMPT_TEMPLATE
    ).format(
        subject=subject,
        topic=topic,
        daily_hours=daily_hours,
        duration_days=duration_days,
        goal=goal or "Master topic foundations",
        weak_topics=weak_str,
        pace=pace
    )

    raw_response = _ask(prompt)
    data = _json_from_text(raw_response)

    if isinstance(data, dict) and data.get("tasks") and isinstance(data["tasks"], list):
        return data

    # Offline algorithmic timetable synthesis
    return _build_fallback_timetable(subject, topic, daily_hours, duration_days, goal, weak_topics, pace)

def _build_fallback_timetable(subject, topic, daily_hours, duration_days, goal, weak_topics, pace):
    tasks = []
    minutes_per_day = int(daily_hours * 60)
    slot1_mins = min(50, minutes_per_day // 2)
    slot2_mins = minutes_per_day - slot1_mins

    milestones = [
        ("Diagnostic & Concept Grounding", "Review foundational definitions, mental models, and notation.", "Concept Theory"),
        ("Mechanics & Worked Examples", "Work through standard canonical examples and understand execution flow.", "Coding / Hands-on Practice"),
        ("Weak Area Remediation", f"Target high-leverage challenges and common mistakes in {topic}.", "Weak Area Drill"),
        ("Active Recall & Self-Testing", "Test retention without reference notes using flashcards.", "Flashcards & Recall"),
        ("Comprehensive Adaptive Assessment", "Complete a full topic quiz and analyze error reports.", "Adaptive Quiz Assessment"),
        ("Edge Cases & Advanced Patterns", "Analyze corner cases, performance trade-offs, and scaling.", "Concept Theory"),
        ("Final Mastery Simulation & Review", "Synthesize all learnings into an executive summary cheatsheet.", "Coding / Hands-on Practice")
    ]

    for day in range(1, duration_days + 1):
        idx = (day - 1) % len(milestones)
        m_title, m_desc, m_type = milestones[idx]

        # Task 1: Concept / Core drill
        tasks.append({
            "id": f"day{day}_task1",
            "day": day,
            "time_slot": "Session 1 (Focus Block)",
            "activity_type": m_type,
            "title": f"Day {day}: {m_title}",
            "description": f"{m_desc} Focus on {topic} ({subject}).",
            "duration_minutes": slot1_mins,
            "completed": False
        })

        # Task 2: Active Practice / Assessment
        tasks.append({
            "id": f"day{day}_task2",
            "day": day,
            "time_slot": "Session 2 (Reinforcement)",
            "activity_type": "Adaptive Quiz Assessment" if day % 2 == 0 else "Flashcards & Recall",
            "title": f"Day {day}: Active Recall & Practice",
            "description": f"Spend {slot2_mins} minutes testing knowledge retrieval and recording doubts.",
            "duration_minutes": slot2_mins,
            "completed": False
        })

    markdown_overview = f"""### 📅 {duration_days}-Day Personalized Adaptive Study Timetable
**Subject:** `{subject}` | **Primary Focus:** `{topic}`  
**Daily Commitment:** `{daily_hours} hours/day` ({minutes_per_day} minutes/day)  
**Learning Pace:** `{pace}` | **Target Goal:** *{goal}*  

---

#### 🎯 Strategic Learning Roadmap
- **Phase 1 (Days 1–{max(1, duration_days//3)}):** Diagnostic ground-truth, syntax/theory solidification, and active notation.
- **Phase 2 (Days {max(2, duration_days//3 + 1)}–{max(2, 2*duration_days//3)}):** Deep-dive problem solving and targeted remediation of weak areas ({', '.join(weak_topics) if weak_topics else 'core topics'}).
- **Phase 3 (Days {max(3, 2*duration_days//3 + 1)}–{duration_days}):** High-stakes adaptive testing, edge-case analysis, and rapid memory consolidation.

> 💡 **Study Strategy Tip:** Use the interactive checklist below to mark tasks as you complete them. Maintain your daily study streak to maximize retention!
"""

    return {
        "markdown_overview": markdown_overview,
        "tasks": tasks
    }

# =========================================================================
# 4. AI Flashcard Generator
# =========================================================================

def generate_flashcards(source_or_topic, count=6):
    prompt = f"""Generate exactly {count} educational flashcards for study notes or topic:
"{source_or_topic}"

Return ONLY a valid JSON array of objects with keys:
"front": Concise question or term on front of flashcard
"back": Clear, high-impact explanation/answer on back of card

Format:
[
  {{"front": "What is ...?", "back": "It is ..."}}
]
"""
    raw_response = _ask(prompt)
    data = _json_from_text(raw_response)
    if isinstance(data, list):
        cards = [
            c for c in data
            if isinstance(c, dict) and c.get("front") and c.get("back")
        ]
        if cards:
            return cards[:count]

    # Offline fallback cards
    words = [w.strip() for w in re.split(r"[\n.!?]+", source_or_topic) if len(w.strip()) > 10]
    fallback = []
    for i in range(count):
        chunk = words[i % len(words)] if words else source_or_topic
        fallback.append({
            "front": f"Key Concept #{i+1}: {source_or_topic.split()[0] if source_or_topic else 'Concept'}",
            "back": f"Essential takeaway: {chunk}. Remember to review how this relates to broader problem-solving patterns."
        })
    return fallback

# =========================================================================
# 5. Interactive Chat AI Tutor (Multi-Turn)
# =========================================================================

def generate_chat_response(messages, subject="General", topic="General", student_profile=None):
    profile_info = ""
    if student_profile:
        profile_info = f"Student Name: {student_profile.get('name')}; Learning Pace: {student_profile.get('learning_pace')}; Target Exam: {student_profile.get('target_exam')}."

    history_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in messages[-6:]])

    prompt = f"""You are LearnSphere AI, a friendly, encouraging, and pedagogically rigorous AI tutor.
Subject Context: {subject}
Topic Context: {topic}
{profile_info}

Conversation History:
{history_text}

Reply to the student's latest message with a helpful, conversational, step-by-step response.
Use Markdown formatting, helpful code blocks or bullet points where appropriate, and end with an encouraging question to verify their understanding.
"""
    result = _ask(prompt)
    if result:
        return result

    latest_user_msg = messages[-1]["content"] if messages else "help"
    return generate_explanation(latest_user_msg, "Intermediate", subject, topic, "Standard / Balanced")

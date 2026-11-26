import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

def build_progress_summary(results):
    if not results:
        return {
            "attempts": 0,
            "average": 0.0,
            "topics": 0,
            "total_questions": 0,
            "total_correct": 0,
            "accuracy": 0.0,
            "streak_days": 0,
            "xp": 0,
            "level": "Level 1 (Novice)",
            "highest_score": 0.0
        }

    df = pd.DataFrame(results)
    attempts = len(df)
    average = float(df["score"].mean())
    highest = float(df["score"].max())
    topics_count = len(df["topic"].unique())
    total_q = int(df["total_questions"].sum())
    total_c = int(df["correct_count"].sum()) if "correct_count" in df.columns else int(total_q * (average / 100))
    accuracy = (total_c / total_q * 100) if total_q > 0 else average

    # Calculate streak (consecutive days with quiz activity)
    streak_days = calculate_streak(df["created_at"].tolist())

    # XP calculation: 10 XP per question answered + 15 bonus XP per correct answer + 50 XP per quiz + streak bonus
    xp = (total_q * 10) + (total_c * 15) + (attempts * 50) + (streak_days * 30)

    # Determine mastery level
    level = "Level 1: Novice"
    if xp >= 2500:
        level = "Level 5: Grandmaster"
    elif xp >= 1200:
        level = "Level 4: Scholar"
    elif xp >= 600:
        level = "Level 3: Explorer"
    elif xp >= 200:
        level = "Level 2: Apprentice"

    return {
        "attempts": attempts,
        "average": average,
        "topics": topics_count,
        "total_questions": total_q,
        "total_correct": total_c,
        "accuracy": accuracy,
        "streak_days": streak_days,
        "xp": xp,
        "level": level,
        "highest_score": highest
    }

def calculate_streak(date_strings):
    if not date_strings:
        return 0
    try:
        dates = sorted(list(set([datetime.fromisoformat(d.replace("Z", "")).date() for d in date_strings])), reverse=True)
        today = date.today()
        streak = 0
        current_check = today

        # If today is not in dates, check if yesterday was in dates
        if dates and dates[0] == today:
            streak = 1
            current_check = today
        elif dates and (today - dates[0]).days == 1:
            streak = 1
            current_check = dates[0]
        else:
            return 0

        for i in range(1, len(dates)):
            expected = current_check - pd.Timedelta(days=1)
            if dates[i] == expected:
                streak += 1
                current_check = dates[i]
            else:
                break
        return streak
    except Exception:
        return 1

def recommend_topics(topic_stats):
    recommendations = []
    for item in topic_stats:
        avg = float(item["average"] or 0)
        attempts = int(item["attempts"] or 0)
        topic_name = item["topic"]
        subject_name = item.get("subject", "General")

        if avg < 60:
            status = "Weak (Needs Attention)"
            action = "Targeted Remedial Practice"
            reason = f"Current average is {avg:.1f}%. Foundational concepts and edge cases need review."
            badge_color = "#ef4444"
        elif avg < 80:
            status = "Developing"
            action = "Intermediate Problem Drill"
            reason = f"Current average is {avg:.1f}%. Solid start; practice intermediate questions to reach mastery."
            badge_color = "#f59e0b"
        else:
            status = "Mastered"
            action = "Advanced Challenge / Revision"
            reason = f"Current average is {avg:.1f}%. Excellent grasp; challenge yourself with hard questions."
            badge_color = "#10b981"

        recommendations.append({
            "topic": topic_name,
            "subject": subject_name,
            "average": avg,
            "attempts": attempts,
            "status": status,
            "action": action,
            "reason": reason,
            "badge_color": badge_color
        })

    # Sort so weak subjects appear first
    recommendations.sort(key=lambda x: (x["average"], -x["attempts"]))
    return recommendations

# =========================================================================
# Plotly Interactive Chart Creators
# =========================================================================

def create_radar_mastery_chart(subject_stats):
    if not subject_stats:
        return None

    subjects = [s["subject"] for s in subject_stats]
    averages = [round(float(s["average"]), 1) for s in subject_stats]

    # Close the radar loop
    radar_subjects = subjects + [subjects[0]]
    radar_averages = averages + [averages[0]]

    fig = go.Figure()

    # Benchmark target trace (80% Mastery target)
    fig.add_trace(go.Scatterpolar(
        r=[80] * len(radar_subjects),
        theta=radar_subjects,
        mode='lines',
        name='Mastery Benchmark (80%)',
        line=dict(color='rgba(16, 185, 129, 0.4)', dash='dash')
    ))

    # Student actual performance trace
    fig.add_trace(go.Scatterpolar(
        r=radar_averages,
        theta=radar_subjects,
        fill='toself',
        name='Your Mastery',
        fillcolor='rgba(37, 99, 235, 0.25)',
        line=dict(color='#2563eb', width=2.5),
        marker=dict(size=7, color='#1d4ed8')
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[20, 40, 60, 80, 100],
                ticktext=["20%", "40%", "60%", "80%", "100%"],
                tickfont=dict(size=10, color="#64748b")
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color="#1e293b", family="sans-serif")
            )
        ),
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        height=340,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_topic_bar_chart(topic_stats):
    if not topic_stats:
        return None

    df = pd.DataFrame(topic_stats)
    df["average"] = df["average"].apply(lambda x: round(float(x), 1))

    # Assign color according to performance
    def get_color(avg):
        if avg < 60:
            return "#ef4444"  # Red
        elif avg < 80:
            return "#f59e0b"  # Amber
        return "#10b981"      # Green

    df["color"] = df["average"].apply(get_color)

    fig = go.Figure(go.Bar(
        x=df["average"],
        y=df["topic"],
        orientation='h',
        marker=dict(color=df["color"], cornerradius=4),
        text=df["average"].apply(lambda v: f"{v}%"),
        textposition='outside'
    ))

    # Reference lines
    fig.add_vline(x=60, line_dash="dot", line_color="#ef4444", annotation_text="Weak (<60%)", annotation_position="top left")
    fig.add_vline(x=80, line_dash="dash", line_color="#10b981", annotation_text="Mastered (80%+)", annotation_position="top right")

    fig.update_layout(
        xaxis=dict(range=[0, 110], title="Average Score (%)", ticksuffix="%"),
        yaxis=dict(title="", autorange="reversed"),
        margin=dict(l=10, r=20, t=30, b=30),
        height=max(260, len(df) * 38),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_progress_timeline(results):
    if not results:
        return None

    df = pd.DataFrame(results)
    df["created_at_dt"] = pd.to_datetime(df["created_at"])
    df = df.sort_values("created_at_dt")
    df["score"] = df["score"].astype(float)
    df["rolling_avg"] = df["score"].rolling(window=3, min_periods=1).mean().round(1)
    df["attempt_num"] = range(1, len(df) + 1)

    fig = go.Figure()

    # Raw scores trace
    fig.add_trace(go.Scatter(
        x=df["attempt_num"],
        y=df["score"],
        mode='lines+markers',
        name='Quiz Score',
        line=dict(color='#93c5fd', width=1.5, dash='dot'),
        marker=dict(size=8, color='#3b82f6'),
        hovertext=df.apply(lambda r: f"Quiz #{r['attempt_num']}<br>Topic: {r['topic']}<br>Score: {r['score']}%", axis=1),
        hoverinfo='text'
    ))

    # Rolling average trend trace
    fig.add_trace(go.Scatter(
        x=df["attempt_num"],
        y=df["rolling_avg"],
        mode='lines',
        name='Learning Trend (3-quiz avg)',
        line=dict(color='#2563eb', width=3)
    ))

    fig.update_layout(
        xaxis=dict(title="Quiz Attempt #", dtick=1),
        yaxis=dict(title="Score (%)", range=[0, 105], ticksuffix="%"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=20, b=30),
        height=320,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_accuracy_donut(summary):
    total = summary.get("total_questions", 0)
    correct = summary.get("total_correct", 0)
    incorrect = max(0, total - correct)

    if total == 0:
        return None

    fig = go.Figure(data=[go.Pie(
        labels=["Correct Answers", "Incorrect / Review"],
        values=[correct, incorrect],
        hole=.68,
        marker=dict(colors=["#10b981", "#ef4444"]),
        textinfo="percent+label",
        showlegend=False
    )])

    fig.update_layout(
        annotations=[dict(text=f"{summary.get('accuracy', 0):.1f}%<br><span style='font-size:12px;color:#64748b'>Accuracy</span>",
                          x=0.5, y=0.5, font_size=20, showarrow=False)],
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

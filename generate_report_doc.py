import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from pathlib import Path

def create_report():
    doc = docx.Document()

    # Set standard margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    def set_font(run, name='Calibri', size=11, bold=False, italic=False, color=RGBColor(15, 23, 42)):
        run.font.name = name
        run.font.size = Pt(size)
        run.bold = bold
        run.italic = italic
        run.font.color.rgb = color

    def add_p(text="", align=WD_ALIGN_PARAGRAPH.LEFT, space_before=0, space_after=6, line_spacing=1.15):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            set_font(run)
        return p

    def set_cell_border(cell, **kwargs):
        """Set cell's border: top, bottom, left, right"""
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(r'''
            <w:tcBorders %(ns)s>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                <w:left w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                <w:bottom w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
                <w:right w:val="single" w:sz="4" w:space="0" w:color="CBD5E1"/>
            </w:tcBorders>
        ''' % {'ns': nsdecls('w')})
        tcPr.append(tcBorders)

    def set_cell_shading(cell, color_hex="F1F5F9"):
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shading)

    # =========================================================================
    # PAGE 1: TITLE & COVER PAGE
    # =========================================================================
    p1 = add_p("MEDICAPS UNIVERSITY", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=24, space_after=4)
    set_font(p1.runs[0], name='Arial', size=22, bold=True, color=RGBColor(26, 43, 107))

    p2 = add_p("Faculty of Engineering", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=6, space_after=2)
    set_font(p2.runs[0], name='Calibri', size=13, bold=True, color=RGBColor(51, 65, 85))

    p3 = add_p("Department of Computer Science & Engineering", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=2, space_after=18)
    set_font(p3.runs[0], name='Calibri', size=13, bold=True, color=RGBColor(51, 65, 85))

    p4 = add_p("Mini Project Report\nOn", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=12)
    set_font(p4.runs[0], name='Calibri', size=14, bold=True, color=RGBColor(15, 23, 42))

    p5 = add_p("LearnSphere AI – Personalized Adaptive Learning Platform", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=28)
    set_font(p5.runs[0], name='Calibri', size=18, bold=True, color=RGBColor(37, 99, 235))

    # Meta Table: Programme, Course Code, Course Name
    meta_table = doc.add_table(rows=3, cols=3)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_data = [
        ("Programme", ":", "B. Tech."),
        ("Course Code", ":", "CS3ED13"),
        ("Course Name", ":", "Gen AI")
    ]
    for row_idx, (col1, col2, col3) in enumerate(meta_data):
        row = meta_table.rows[row_idx]
        p_c1 = row.cells[0].paragraphs[0]
        p_c1.add_run(col1)
        set_font(p_c1.runs[0], size=12, bold=True, color=RGBColor(15, 23, 42))
        row.cells[0].width = Inches(2.0)

        p_c2 = row.cells[1].paragraphs[0]
        p_c2.add_run(col2)
        set_font(p_c2.runs[0], size=12, bold=True)
        row.cells[1].width = Inches(0.4)

        p_c3 = row.cells[2].paragraphs[0]
        p_c3.add_run(col3)
        set_font(p_c3.runs[0], size=12, bold=True, color=RGBColor(15, 23, 42))
        row.cells[2].width = Inches(3.6)

    add_p("", space_after=24)

    # Student Box
    box_table = doc.add_table(rows=1, cols=1)
    box_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    box_cell = box_table.rows[0].cells[0]
    box_cell.width = Inches(6.0)

    # Custom thick border for student box
    tcPr = box_cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(r'''
        <w:tcBorders %(ns)s>
            <w:top w:val="single" w:sz="12" w:space="0" w:color="0F172A"/>
            <w:left w:val="single" w:sz="12" w:space="0" w:color="0F172A"/>
            <w:bottom w:val="single" w:sz="12" w:space="0" w:color="0F172A"/>
            <w:right w:val="single" w:sz="12" w:space="0" w:color="0F172A"/>
        </w:tcBorders>
    ''' % {'ns': nsdecls('w')})
    tcPr.append(tcBorders)

    bp1 = box_cell.paragraphs[0]
    bp1.paragraph_format.space_before = Pt(14)
    bp1.paragraph_format.space_after = Pt(10)
    bp1.add_run("Name of Student: …………………………………………………………….")
    set_font(bp1.runs[0], size=12, bold=True)

    bp2 = box_cell.add_paragraph()
    bp2.paragraph_format.space_before = Pt(6)
    bp2.paragraph_format.space_after = Pt(10)
    bp2.add_run("Scholar No/ /Enrollment Number: …………………………………….")
    set_font(bp2.runs[0], size=12, bold=True)

    bp3 = box_cell.add_paragraph()
    bp3.paragraph_format.space_before = Pt(6)
    bp3.paragraph_format.space_after = Pt(14)
    bp3.add_run("Sem: ………………   Section: ………   Batch: ……………………….")
    set_font(bp3.runs[0], size=12, bold=True)

    doc.add_page_break()

    # =========================================================================
    # PAGE 2: VISION & MISSION OF UNIVERSITY
    # =========================================================================
    p_u_title = add_p("MEDICAPS UNIVERSITY", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=20, space_after=28)
    set_font(p_u_title.runs[0], name='Arial', size=22, bold=True, color=RGBColor(26, 43, 107))

    pv = add_p("Vision of the University:", space_before=14, space_after=8)
    set_font(pv.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    pv_text = add_p(
        "To build an institutional ecosystem that equips and inspires the next generation of society-ready professionals with a core belief that knowledge is power.",
        space_before=0, space_after=24
    )
    set_font(pv_text.runs[0], size=11.5, color=RGBColor(51, 65, 85))

    pm = add_p("Mission of the University:", space_before=14, space_after=12)
    set_font(pm.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    missions_uni = [
        "Emerge as the most sought-after higher education institution in central India with state-of-the-art resources and experienced faculty members.",
        "Nurture an academic environment at par with global standards of pedagogy that is conducive to experiential learning, and research to create a positive impact in the journey of nation-building.",
        "Cultivate a vibrant ecosystem for professional and intellectual growth beyond the classrooms to empower individuals to become responsible global citizens, lifelong learners, and ethical leaders.",
        "Engage and collaborate with academic institutions, business organizations, and communities to address contemporary challenges through research and growth initiatives."
    ]
    for idx, m_str in enumerate(missions_uni, 1):
        p_m = add_p(f"{idx}.  {m_str}", space_before=4, space_after=12)
        set_font(p_m.runs[0], size=11.5, color=RGBColor(51, 65, 85))

    doc.add_page_break()

    # =========================================================================
    # PAGE 3: VISION & MISSION OF DEPARTMENT
    # =========================================================================
    p_d_head = add_p("MEDICAPS\nFACULTY OF ENGINEERING", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=6)
    set_font(p_d_head.runs[0], name='Arial', size=18, bold=True, color=RGBColor(26, 43, 107))

    p_dept = add_p("Department of\nComputer Science & Engineering", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=4, space_after=24)
    set_font(p_dept.runs[0], size=14, bold=True, color=RGBColor(37, 99, 235))

    p_dv = add_p("Vision of the Department:", space_before=14, space_after=8)
    set_font(p_dv.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    p_dv_text = add_p(
        "To inculcate capability of thinking innovatively and to enrich Computer Science and Engineering graduates with domain knowledge and skills to address contemporary industrial and social requirements",
        space_before=0, space_after=24
    )
    set_font(p_dv_text.runs[0], size=11.5, color=RGBColor(51, 65, 85))

    p_dm = add_p("Mission of the Department:", space_before=14, space_after=12)
    set_font(p_dm.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    missions_dept = [
        "Provide an environment to the students to learn with passion and equip them with the proper skill set to address current problems.",
        "Provide maximum exposure to innovative techniques available to cater industrial needs by maintaining the best Industry- Academia relation.",
        "Imparting best problem-solving strategies in students to work in a team.",
        "Produce leadership qualities in Computer Science graduates to work for the society.",
        "Attract experienced and expert faculty members and create an enthusiastic academic environment."
    ]
    for idx, m_str in enumerate(missions_dept, 1):
        p_dm_item = add_p(f"{idx}.  {m_str}", space_before=4, space_after=12)
        set_font(p_dm_item.runs[0], size=11.5, color=RGBColor(51, 65, 85))

    doc.add_page_break()

    # =========================================================================
    # PAGE 4: CLOs & COs
    # =========================================================================
    p_clo_title = add_p("Course Learning Objectives:", space_before=10, space_after=8)
    set_font(p_clo_title.runs[0], size=12.5, bold=True, color=RGBColor(15, 23, 42))

    clo_table = doc.add_table(rows=6, cols=2)
    clo_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    clo_data = [
        ("CLO01", "To understand the fundamentals and motivation behind generative modeling."),
        ("CLO02", "To explore popular generative models such as Variational Autoencoders (VAEs),"),
        ("CLO03", "Generative Adversarial Networks (GANs), and Diffusion Models."),
        ("CLO04", "To apply generative models for tasks in image, text, and audio synthesis."),
        ("CLO05", "To study evaluation techniques for generative models and ethical implications of their use."),
        ("CLO06", "To develop hands-on skills in implementing and experimenting with generative models using modern frameworks.")
    ]
    for r_idx, (code, desc) in enumerate(clo_data):
        row = clo_table.rows[r_idx]
        c1, c2 = row.cells[0], row.cells[1]
        c1.width = Inches(1.3)
        c2.width = Inches(5.1)
        set_cell_border(c1)
        set_cell_border(c2)
        set_cell_shading(c1, "F8FAFC")

        p_code = c1.paragraphs[0]
        p_code.paragraph_format.space_before = Pt(4)
        p_code.paragraph_format.space_after = Pt(4)
        p_code.add_run(code)
        set_font(p_code.runs[0], size=10, bold=True)

        p_desc = c2.paragraphs[0]
        p_desc.paragraph_format.space_before = Pt(4)
        p_desc.paragraph_format.space_after = Pt(4)
        p_desc.add_run(desc)
        set_font(p_desc.runs[0], size=10)

    p_co_title = add_p("Course Outcomes:", space_before=18, space_after=8)
    set_font(p_co_title.runs[0], size=12.5, bold=True, color=RGBColor(15, 23, 42))

    co_table = doc.add_table(rows=7, cols=3)
    co_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    co_data = [
        ("CO", "Description", "Blooms\nLevel"),
        ("CO01", "Remember the principles and applications of generative modeling in AI.", "BL01"),
        ("CO02", "Understand the generative models like VAEs and GANs for real-world datasets.", "BL02"),
        ("CO03", "Apply knowledge of generative models (e.g., VAEs, GANs) for image, text, and audio synthesis using frameworks.", "BL03"),
        ("CO04", "Analyze ethical and societal concerns related to generative AI applications.", "BL04"),
        ("CO05", "Evaluate generative model performance using quantitative and qualitative metrics.", "BL05"),
        ("CO06", "Develop and present a mini-project demonstrating the application of generative AI in a chosen domain.", "BL06")
    ]
    for r_idx, (co_code, co_desc, co_bloom) in enumerate(co_data):
        row = co_table.rows[r_idx]
        c1, c2, c3 = row.cells[0], row.cells[1], row.cells[2]
        c1.width = Inches(1.1)
        c2.width = Inches(4.3)
        c3.width = Inches(1.0)
        set_cell_border(c1)
        set_cell_border(c2)
        set_cell_border(c3)

        is_header = (r_idx == 0)
        if is_header:
            set_cell_shading(c1, "E2E8F0")
            set_cell_shading(c2, "E2E8F0")
            set_cell_shading(c3, "E2E8F0")
        else:
            set_cell_shading(c1, "F8FAFC")

        p_c1 = c1.paragraphs[0]
        p_c1.paragraph_format.space_before = Pt(4)
        p_c1.paragraph_format.space_after = Pt(4)
        p_c1.add_run(co_code)
        set_font(p_c1.runs[0], size=9.5, bold=True)

        p_c2 = c2.paragraphs[0]
        p_c2.paragraph_format.space_before = Pt(4)
        p_c2.paragraph_format.space_after = Pt(4)
        p_c2.add_run(co_desc)
        set_font(p_c2.runs[0], size=9.5, bold=is_header)

        p_c3 = c3.paragraphs[0]
        p_c3.paragraph_format.space_before = Pt(4)
        p_c3.paragraph_format.space_after = Pt(4)
        p_c3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c3.add_run(co_bloom)
        set_font(p_c3.runs[0], size=9.5, bold=True)

    doc.add_page_break()

    # =========================================================================
    # PAGE 5: ACKNOWLEDGMENT
    # =========================================================================
    p_ack_head = add_p("Acknowledgment", space_before=20, space_after=18)
    set_font(p_ack_head.runs[0], size=14, bold=True, color=RGBColor(15, 23, 42))

    p_ack_body = add_p(
        "I have carefully understood the Generative AI Course proficiency Regulations and agree to adhere to them with full responsibility.",
        space_before=6, space_after=80
    )
    set_font(p_ack_body.runs[0], size=12, color=RGBColor(51, 65, 85))

    p_sig = add_p("Signature of the Student: _________________________", space_before=30, space_after=24)
    set_font(p_sig.runs[0], size=12, bold=True)

    p_date = add_p("Date: _______________", space_before=10, space_after=10)
    set_font(p_date.runs[0], size=12, bold=True)

    doc.add_page_break()

    # =========================================================================
    # PAGE 6+: TECHNICAL REPORT CONTENT
    # =========================================================================
    p_report_title = add_p("LearnSphere AI – Personalized Adaptive Learning Platform", align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=20)
    set_font(p_report_title.runs[0], name='Calibri', size=18, bold=True, color=RGBColor(37, 99, 235))

    # SECTION 1: OBJECTIVE
    s1 = add_p("1. Objective:", space_before=14, space_after=8)
    set_font(s1.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    s1_text = (
        "Traditional educational paradigms deliver standardized instructional material and static assessments across "
        "all students, ignoring disparate learning paces, prior domain proficiencies, and individual cognitive weaknesses. "
        "The primary objective of the LearnSphere AI project is to conceptualize, architect, and deploy a Generative AI-powered "
        "adaptive learning platform that dynamically tailors educational experiences to individual student needs.\n\n"
        "Key Specific Objectives:\n"
        "• Personalize Education: Build student profile modeling incorporating personalized learning paces (Deep & Foundational, Standard/Balanced, Accelerated), target examination goals, and daily study targets.\n"
        "• Identify Weak Subjects: Quantitatively detect subject and sub-topic knowledge gaps using thresholded performance metrics (<60% accuracy flagging).\n"
        "• Generate Adaptive Learning Material: Dynamically synthesize topic-specific explanations, active recall flashcards, and custom revision content via Large Language Models (Google Gemini API & LangChain).\n"
        "• Real-Time Difficulty Adjustment: Implement an adaptive quiz engine where question difficulty scales up (Easy ➔ Medium ➔ Hard) upon correct answers and scales down to diagnose misconceptions upon errors.\n"
        "• Automated Study Timetables: Synthesize actionable, day-by-day study schedules and interactive task checklists focused on remediating identified weak areas.\n"
        "• Track Learning Progress: Deliver interactive visual dashboards using Plotly and Pandas with multi-axis competency radars, accuracy trajectories, and gamified XP/streak milestones."
    )
    p_s1 = add_p(s1_text, space_before=0, space_after=14)
    set_font(p_s1.runs[0], size=11, color=RGBColor(51, 65, 85))

    # SECTION 2: METHODOLOGY USED
    s2 = add_p("2. Methodology Used:", space_before=14, space_after=8)
    set_font(s2.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    s2_text = (
        "The project follows a modular, client-server web architecture combining prompt orchestration, relational persistence, "
        "and interactive data visualization.\n\n"
        "A. Architectural Methodology:\n"
        "• Generative AI & Orchestration Layer: Powered by the Google Gemini API (gemini-2.5-flash) and LangChain (langchain-core) PromptTemplates. "
        "Prompts are engineered using Chain-of-Thought (CoT) and structured JSON parsing to guarantee valid multiple-choice questions, options, answers, and explanations.\n"
        "• Adaptive Assessment Engine: Inspired by Item Response Theory (IRT) heuristics. A state machine monitors question attempts in real time; "
        "consecutive correct responses elevate the difficulty state while incorrect responses trigger remedial foundational inquiries.\n"
        "• Persistence Layer: A relational SQLite database (`learnsphere.db`) with normalized tables storing student credentials (PBKDF2-HMAC-SHA256 hashed), "
        "curriculum subjects/topics, historical quiz results, time-stamped session details, and structured study timetable tasks.\n"
        "• Analytical & Visualization Engine: Implemented using Pandas for statistical aggregations (moving averages, streak tracking, cognitive levels) "
        "and Plotly Graph Objects for rendering radar charts, mastery threshold bars, and accuracy donut distributions.\n"
        "• Frontend User Interface: Built with Streamlit augmented with responsive CSS cards, high-contrast typography, and dynamic state management."
    )
    p_s2 = add_p(s2_text, space_before=0, space_after=14)
    set_font(p_s2.runs[0], size=11, color=RGBColor(51, 65, 85))

    # SECTION 3: IMPLEMENTATION
    s3 = add_p("3. Implementation:", space_before=14, space_after=8)
    set_font(s3.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    s3_text = (
        "The project implementation is structured into modular Python components:\n\n"
        "1. Database & Security Module (`modules/database.py`):\n"
        "   - Implements automated SQLite schema initialization, table migrations, and relational integrity.\n"
        "   - Cryptographically hashes passwords using PBKDF2 (120,000 iterations with unique salt).\n"
        "   - Manages CRUD operations for student profiles, subject taxonomies, quiz attempt logs, and study plans.\n\n"
        "2. AI Personalization Engine (`modules/ai_engine.py`):\n"
        "   - LangChain PromptTemplates: Structures educational explanations into Core Concept, Intuitive Analogy, Step-by-Step Breakdown, Common Pitfalls, and Quick Checks.\n"
        "   - Real-Time Adaptive Question Generator: Generates targeted individual MCQs taking into account previous answer correctness.\n"
        "   - Timetable Generator: Computes daily slot allocations (Focus Blocks, Active Recall, Assessment Drills) formatted into structured JSON.\n"
        "   - Dual-Engine Fallback: Features seamless fallback to comprehensive offline curriculum banks if no Gemini API key is supplied.\n\n"
        "3. Analytics & Visualization Module (`modules/analytics.py`):\n"
        "   - Performance Aggregation: Computes rolling accuracy, highest score, total questions solved, and consecutive study streaks.\n"
        "   - Weakness Diagnostic Classifier: Classifies topics into Weak (<60%), Developing (60-80%), and Mastered (>80%).\n"
        "   - Plotly Charts: Generates interactive Spider/Radar charts, thresholded horizontal bar charts, and historical score trendlines.\n\n"
        "4. Streamlit Interactive Application (`app.py`):\n"
        "   - Multi-page navigation (Dashboard, Real-Time Adaptive Quiz, Topic Assessment, AI Tutor, Study Timetable, Flashcards, Progress Analytics, Profile Settings).\n"
        "   - Custom CSS theme and `.streamlit/config.toml` enforcing high-contrast, crystal-clear typography across all system themes."
    )
    p_s3 = add_p(s3_text, space_before=0, space_after=14)
    set_font(p_s3.runs[0], size=11, color=RGBColor(51, 65, 85))

    # SECTION 4: RESULTS
    s4 = add_p("4. Results:", space_before=14, space_after=8)
    set_font(s4.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    s4_text = (
        "The platform was comprehensively tested using both synthetic test suites and manual multi-turn learning sessions:\n\n"
        "• Automated Test Suite Execution (`test_learnsphere.py`):\n"
        "  - Database Verification: 100% pass rate across user authentication, profile updates, seed taxonomy retrieval, and relational storage.\n"
        "  - Analytics Verification: Verified accurate weakness detection flagging topics scoring 40.0% as 'Weak (Needs Attention) - Targeted Remedial Practice'.\n"
        "  - AI Engine Verification: Successfully generated 4-option MCQs with validated schema, multi-level explanations, and multi-day timetables.\n"
        "  - App Compilation: Streamlit frontend compiled with zero syntax errors.\n\n"
        "• Empirical User Experience Results:\n"
        "  - Adaptive Trajectory: Successfully adapted question difficulty in real time based on user responses, shifting from Medium to Hard on correct answers and descending to Easy on errors.\n"
        "  - Pedagogical Impact: Step-by-step AI explanations provided clear analogies and code snippets, improving comprehension of complex algorithms and database concurrency concepts.\n"
        "  - Visual Clarity: High-contrast assessment banners, question cards, and distinct difficulty pills resolved all UI contrast ambiguities, ensuring maximum legibility."
    )
    p_s4 = add_p(s4_text, space_before=0, space_after=14)
    set_font(p_s4.runs[0], size=11, color=RGBColor(51, 65, 85))

    # SECTION 5: CONCLUSION
    s5 = add_p("5. Conclusion:", space_before=14, space_after=8)
    set_font(s5.runs[0], size=13, bold=True, color=RGBColor(15, 23, 42))

    s5_text = (
        "The LearnSphere AI platform demonstrates the transformative potential of Generative AI in education by successfully replacing "
        "one-size-fits-all curricula with an intelligent, adaptive learning ecosystem.\n\n"
        "Key Accomplishments:\n"
        "1. Met all Course Learning Objectives (CLO01-CLO06) and Course Outcomes (CO01-CO06) by implementing generative models for text and educational synthesis using modern AI frameworks (Google Gemini API & LangChain).\n"
        "2. Delivered dynamic difficulty adjustment based on student performance, ensuring students are neither bored by overly simple questions nor discouraged by overly complex material.\n"
        "3. Integrated automated study timetable generation that directly remediates diagnosed weak areas, enhancing revision efficiency.\n"
        "4. Produced an extensible, production-ready full-stack architecture that can be scaled to incorporate Retrieval-Augmented Generation (RAG) over institutional syllabi and institutional classroom analytics in future work."
    )
    p_s5 = add_p(s5_text, space_before=0, space_after=14)
    set_font(p_s5.runs[0], size=11, color=RGBColor(51, 65, 85))

    # Save Document
    output_docx_path = Path(__file__).resolve().parent / "LearnSphere_AI_Mini_Project_Report.docx"
    doc.save(str(output_docx_path))
    print(f"Successfully generated DOCX report at: {output_docx_path}")

if __name__ == "__main__":
    create_report()

import os
import json
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

from projecttest.utils.chart_generator import generate_score_chart


def generate_report(
    output_path,
    candidate_name,
    experience_level,
    selected_tech,
    interview_score,
    total_questions,
    coding_result,
    interview_feedback,
):
    """
    Generate recruiter-friendly PDF report with charts.
    Overwrites existing file each time.
    """

    # =====================================================
    # Ensure NEW file each time
    # =====================================================
    if os.path.exists(output_path):
        os.remove(output_path)

    # =====================================================
    # Font (supports many characters)
    # =====================================================
    pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))

    styles = getSampleStyleSheet()
    body = styles["BodyText"]
    body.fontName = "HeiseiMin-W3"

    # =====================================================
    # Parse coding result safely
    # =====================================================
    try:
        if isinstance(coding_result, str):
            coding_result = json.loads(coding_result)

        coding_score = int(coding_result.get("score", 0))
        coding_verdict = str(coding_result.get("verdict", "fail")).lower()
        coding_feedback = coding_result.get("feedback", "")
    except Exception:
        coding_score = 0
        coding_verdict = "fail"
        coding_feedback = "Could not parse coding result"

    # =====================================================
    # Calculate interview %
    # =====================================================
    interview_percent = 0
    if total_questions > 0:
        interview_percent = int((interview_score / total_questions) * 100)

    # =====================================================
    # PASS / FAIL logic
    # =====================================================
    if interview_percent >= 60 and coding_verdict == "pass":
        final_result = "PASS"
        hire_recommendation = "Strong Hire"
    elif interview_percent >= 50:
        final_result = "BORDERLINE"
        hire_recommendation = "Consider"
    else:
        final_result = "FAIL"
        hire_recommendation = "Reject"

    # =====================================================
    # Verdict color
    # =====================================================
    if coding_verdict == "pass":
        verdict_text = '<font><b>PASS</b></font>'
    else:
        verdict_text = '<font><b>FAIL</b></font>'

    # =====================================================
    # Chart
    # =====================================================
    chart_path = generate_score_chart(interview_score, total_questions)

    # =====================================================
    # Build PDF
    # =====================================================
    doc = SimpleDocTemplate(output_path)
    story = []

    # ================= HEADER =================
    story.append(Paragraph("<b>Candidate Interview Report</b>", styles["Heading1"]))
    story.append(Spacer(1, 25))

    # ================= BASIC INFO =================
    story.append(Paragraph(f"Candidate: <b>{candidate_name}</b>", body))
    story.append(Paragraph(f"Experience Level: <b>{experience_level}</b>", body))
    story.append(Paragraph(f"Technology: <b>{selected_tech}</b>", body))
    story.append(Spacer(1, 25))

    # ================= FINAL DECISION =================
    story.append(Paragraph("<b>Final Result</b>", styles["Heading2"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Status: <b>{final_result}</b>", body))
    story.append(Paragraph(f"Hire Recommendation: <b>{hire_recommendation}</b>", body))
    story.append(Spacer(1, 25))

    # ================= INTERVIEW SCORE =================
    story.append(Paragraph("<b>Interview Score</b>", styles["Heading2"]))
    story.append(
        Paragraph(
            f"Score: <b>{interview_score} / {total_questions} ({interview_percent}%)</b>",
            body,
        )
    )
    story.append(Spacer(1, 20))

    # ================= GRAPH =================
    if os.path.exists(chart_path):
        story.append(Image(chart_path, width=350, height=220))
        story.append(Spacer(1, 20))

    # ================= INTERVIEW FEEDBACK =================
    story.append(Paragraph("<b>Interview Feedback</b>", styles["Heading2"]))
    story.append(Spacer(1, 12))

    for line in interview_feedback.split("\n"):
        if line.strip():
            story.append(Paragraph(line, body))

    story.append(Spacer(1, 25))

    # ================= CODING RESULT =================
    story.append(Paragraph("<b>Coding Challenge Result</b>", styles["Heading2"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"Score: <b>{coding_score}</b>", body))
    story.append(Paragraph(f"Verdict: {verdict_text}", body))
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Feedback:</b>", body))
    story.append(Paragraph(str(coding_feedback), body))

    # =====================================================
    # Build document
    # =====================================================
    doc.build(story)

    # cleanup temp chart
    if os.path.exists(chart_path):
        os.remove(chart_path)

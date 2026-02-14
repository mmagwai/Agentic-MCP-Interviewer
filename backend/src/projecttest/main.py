from projecttest.crew import InterviewCrew
from projecttest.utils.file_reader import read_cv_file
from crewai import Agent, Task, Crew
from projecttest.grading_crew import GradingCrew
from projecttest.utils.pdf_report import generate_report

import json


# =====================================================
# Helper to get task output safely
# =====================================================
def get_task_output(result, task_name):
    for task in result.tasks_output:
        if task.name == task_name:
            return task.raw.strip()
    return ""

# =====================================================
# INTERVIEW PERFORMANCE SUMMARY
# =====================================================
def generate_interview_feedback(questions, answers):
    interviewer = Agent(
        role="Senior Technical Interviewer",
        goal="Summarize candidate interview performance",
        backstory="You write professional hiring recommendations.",
        verbose=False
    )

    qa_text = ""
    for i, (q, a) in enumerate(zip(questions, answers), start=1):
        qa_text += f"Q{i}: {q}\nA{i}: {a}\n\n"

    task = Task(
        description=f"""
        Based on the interview below, provide:

        Strengths:
        Weaknesses:
        Recommendation: (Hire / No Hire / Next Round)

        Interview:
        {qa_text}
        """,
        agent=interviewer,
        expected_output="Professional evaluation"
    )

    crew = Crew(
        agents=[interviewer],
        tasks=[task],
        verbose=False
    )

    result = crew.kickoff()
    return result.raw


# =====================================================
# MAIN PIPELINE
# =====================================================
def run():
    cv_path = input("Enter path to CV file:\n").strip()
    cv_text = read_cv_file(cv_path)

    # =====================================================
    # ================= INTERVIEW =========================
    # =====================================================

    while True:
        selected_tech = input("\nEnter technology to be interviewed on:\n").strip()

        crew = InterviewCrew().crew()
        result = crew.kickoff(
            inputs={
                "cv_text": cv_text,
                "selected_tech": selected_tech
            }
        )

        output = get_task_output(result, "generate_interview_questions")

        if output == "Selected technology not found in CV.":
            print("Technology not found. Try again.")
            continue
        else:
            break

    questions = [q for q in output.split("\n") if q.strip()]
    score = 0
    answers = []  


    for idx, question in enumerate(questions, start=1):
        print(f"\nQuestion {idx}: {question}")
        answer = input("Your answer: ")
        answers.append(answer) 

        if evaluate_answer(question, answer):
            print("Acceptable answer")
            score += 1
        else:
            print("Incorrect answer")

    print(f"\nFinal Score: {score}/{len(questions)}")
    interview_feedback = generate_interview_feedback(questions, answers)

    # =====================================================
    # ================ CODING CHALLENGE ===================
    # =====================================================

    print("\n\n=== CODING CHALLENGE ===\n")

    challenge = get_task_output(result, "generate_coding_challenge")

    if challenge == "No coding challenge for this technology.":
        print(challenge)
        return

    print(challenge)

    solution_path = input("\nEnter path to your solution file:\n").strip()

    try:
        with open(solution_path, "r", encoding="utf-8") as f:
            candidate_code = f.read()
    except Exception:
        print("Could not read file.")
        return

    # =====================================================
    # ================== CODE GRADING =====================
    # =====================================================

    grading_crew = GradingCrew().crew()

    grading_result = grading_crew.kickoff(
        inputs={
            "candidate_code": candidate_code,
            "problem": challenge
        }
    )

    grade_raw = grading_result.raw

    print("\n=== CODE EVALUATION ===\n")
    print(grade_raw)

    # =====================================================
    # ================== PDF REPORT =======================
    # =====================================================

    analysis = get_task_output(result, "analyze_cv_task")

    try:
        analysis_json = json.loads(analysis)
        candidate_name = analysis_json.get("candidate_name", "Unknown")
        experience_level = analysis_json.get("experience_level", "Unknown")
    except Exception:
        candidate_name = "Unknown"
        experience_level = "Unknown"


    # ---- simple extraction (upgrade later with parser) ----
    candidate_name = "Candidate"
    experience_level = "Unknown"

    for line in analysis.split("\n"):
        if "name" in line.lower():
            candidate_name = line.split(":")[-1].strip()

        if "senior" in line.lower():
            experience_level = "Senior"
        elif "intermediate" in line.lower():
            experience_level = "Intermediate"
        elif "junior" in line.lower():
            experience_level = "Junior"

    generate_report(
        output_path="interview_report.pdf",
        candidate_name=candidate_name,
        experience_level=experience_level,
        selected_tech=selected_tech,
        interview_score=score,
        total_questions=len(questions),
        coding_result=grade_raw,
        interview_feedback=interview_feedback
    )


    print("\n PDF report generated: interview_report.pdf")


# =====================================================
# LLM ANSWER GRADER
# =====================================================
def evaluate_answer(question, answer):
    grader_agent = Agent(
        role="Technical Interview Grader",
        goal="Evaluate if a candidate's answer is acceptable",
        backstory=(
            "You are a senior technical interviewer. "
            "You judge answers leniently but require core concepts to be correct."
        ),
        verbose=False
    )

    grading_task = Task(
        description=f"""
        Interview Question:
        {question}

        Candidate Answer:
        {answer}

        Decide if the answer is ACCEPTABLE for an interview.
        Be lenient and accept partial explanations if main idea is present.

        Respond ONLY in valid JSON:
        {{
          "acceptable": true | false
        }}
        """,
        agent=grader_agent,
        expected_output="JSON with acceptable=true or false"
    )

    grading_crew = Crew(
        agents=[grader_agent],
        tasks=[grading_task],
        verbose=False
    )

    result = grading_crew.kickoff()

    try:
        verdict = json.loads(result.raw)
        return verdict.get("acceptable", False)
    except json.JSONDecodeError:
        return False


if __name__ == "__main__":
    run()

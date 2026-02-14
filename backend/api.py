from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


import shutil
import os
import json
import sys



class RunCodeRequest(BaseModel):
    language: str
    code: str


# allow imports from src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from projecttest.analysis_crew import CVAnalysisCrew
from projecttest.question_crew import QuestionCrew
from projecttest.utils.file_reader import read_cv_file
from projecttest.evaluation_crew import EvaluationCrew
from projecttest.grading_crew import GradingCrew
from projecttest.challenge_crew import ChallengeCrew
from projecttest.utils.pdf_report import generate_report


# =====================================================
# APP
# =====================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev mode
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# TEMP MEMORY (replace with DB later)
# =====================================================
INTERVIEW_CONTEXT = {
    "candidate_name": "",
    "experience_level": "",
    "selected_tech": "",
    "interview_score": 0,
    "total_questions": 0,
    "interview_feedback": "",
}


# =====================================================
# HELPER → Extract task output
# =====================================================
def get_task_output(result, task_name: str):
    for task in result.tasks_output:
        if task.name == task_name:
            return task.raw.strip()
    return ""


# =====================================================
# 1️ ANALYZE CV
# =====================================================
@app.post("/analyze-cv")
async def analyze_cv(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cv_text = read_cv_file(temp_path)

        crew = CVAnalysisCrew().crew()
        result = crew.kickoff(inputs={"cv_text": cv_text})

        raw = get_task_output(result, "analyze_cv_task")

        try:
            data = json.loads(raw)
        except Exception:
            data = {
                "candidate_name": "Unknown",
                "experience_level": "Unknown",
                "tech_stack": [],
            }

        INTERVIEW_CONTEXT["candidate_name"] = data.get("candidate_name", "")
        INTERVIEW_CONTEXT["experience_level"] = data.get("experience_level", "")

        return data

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================
# 2️ GENERATE INTERVIEW QUESTIONS
# =====================================================
@app.post("/questions")
async def generate_questions(
    file: UploadFile = File(...),
    selected_tech: str = Form(...),
):
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cv_text = read_cv_file(temp_path)

        crew = QuestionCrew().crew()
        result = crew.kickoff(
            inputs={
                "cv_text": cv_text,
                "selected_tech": selected_tech,
            }
        )

        raw = get_task_output(result, "generate_interview_questions")

        if "not found" in raw.lower():
            return {
                "questions": [],
                "message": "Selected technology not found in CV.",
            }

        cleaned = []
        for line in raw.split("\n"):
            line = line.strip()
            line = line.lstrip("0123456789.-) ")
            if line:
                cleaned.append(line)

        INTERVIEW_CONTEXT["selected_tech"] = selected_tech
        INTERVIEW_CONTEXT["total_questions"] = len(cleaned)

        return {
            "questions": cleaned,
            "total": len(cleaned),
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================
# 3️ EVALUATE ANSWER
# =====================================================
@app.post("/evaluate-answer")
async def evaluate_answer(
    question: str = Form(...),
    answer: str = Form(...)
):
    crew = EvaluationCrew().crew()

    result = crew.kickoff(
        inputs={
            "question": question,
            "answer": answer
        }
    )

    raw = get_task_output(result, "evaluate_answer")

    try:
        data = json.loads(raw)
    except Exception:
        data = {
            "score": 0,
            "feedback": "Could not evaluate answer",
            "correct": False
        }

    INTERVIEW_CONTEXT["interview_score"] += int(data.get("score", 0))
    INTERVIEW_CONTEXT["interview_feedback"] += (
        f"Q: {question}\n"
        f"A: {answer}\n"
        f"Score: {data.get('score', 0)}\n"
        f"Feedback: {data.get('feedback', '')}\n\n"
    )

    return data


# =====================================================
# 4️ GENERATE CODING CHALLENGE
# =====================================================
@app.post("/coding-challenge")
async def coding_challenge(
    file: UploadFile = File(...),
    selected_tech: str = Form(...),
    experience_level: str = Form(...)
):
    temp_path = f"temp_{file.filename}"

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        cv_text = read_cv_file(temp_path)

        crew = ChallengeCrew().crew()

        result = crew.kickoff(
            inputs={
                "selected_tech": selected_tech,
                "cv_text": cv_text,
                "experience_level": experience_level,
            }
        )

        raw = get_task_output(result, "generate_coding_challenge")

        if "no coding challenge" in raw.lower():
            return {"challenge": ""}

        return {"challenge": raw}

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# =====================================================
# 5 GRADE CODE SUBMISSION
# =====================================================
@app.post("/grade-code")
async def grade_code(
    problem: str = Form(...),
    code: str = Form(...),
):
    crew = GradingCrew().crew()

    result = crew.kickoff(
        inputs={
            "problem": problem,
            "candidate_code": code,
        }
    )

    raw = get_task_output(result, "grade_coding_solution")

    try:
        data = json.loads(raw)
    except Exception:
        data = {"score": 0, "verdict": "fail", "feedback": "error"}

    os.makedirs("reports", exist_ok=True)
    output_path = f"reports/{INTERVIEW_CONTEXT['candidate_name']}_report.pdf"

    generate_report(
        output_path=output_path,
        candidate_name=INTERVIEW_CONTEXT["candidate_name"],
        experience_level=INTERVIEW_CONTEXT["experience_level"],
        selected_tech=INTERVIEW_CONTEXT["selected_tech"],
        interview_score=INTERVIEW_CONTEXT["interview_score"],
        total_questions=INTERVIEW_CONTEXT["total_questions"],
        coding_result=data,
        interview_feedback=INTERVIEW_CONTEXT["interview_feedback"],
    )

    print("Report saved to:", os.path.abspath(output_path))
    return data


# ======================================================
# RUN CODE  (MCP stdio bridge)
# =====================================================
@app.post("/run-code")
async def run_code_endpoint(req: RunCodeRequest):
    """
    Forwards code execution to the MCP HTTP server running on port 8001.
    The MCP server handles the actual subprocess execution and returns
    stdout / stderr / exit_code.
    """
    if not req.language or not req.code:
        return {"stdout": "", "stderr": "Missing language or code", "exit_code": 1}

    payload = {
        "language": req.language.strip().lower(),
        "code": req.code,
    }

    try:
        from mcp.client.streamable_http import streamablehttp_client
        from mcp import ClientSession

        async with streamablehttp_client("http://127.0.0.1:8001/mcp/") as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("run_code", payload)

                if result.content:
                    raw = result.content[0].text
                    try:
                        return json.loads(raw)
                    except Exception:
                        return {"stdout": raw, "stderr": "", "exit_code": 0}

                return {"stdout": "", "stderr": "Empty response from MCP server", "exit_code": 1}

    except Exception as e:
        import traceback
        err = traceback.format_exc()
        print("RUN CODE ERROR:", err, flush=True)
        if "Connect" in err or "refused" in err.lower():
            return {
                "stdout": "",
                "stderr": "MCP server is not running. Start it with: python mcp_server/server.py",
                "exit_code": 1,
            }
        return {"stdout": "", "stderr": str(e), "exit_code": 1}
# Projecttest-MCP: AI Technical Interviewer

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Components & Features](#components--features)
6. [API Endpoints](#api-endpoints)
7. [AI Agents & Crews](#ai-agents--crews)
8. [MCP Code Runner Server](#mcp-code-runner-server)
9. [Interview Workflow](#interview-workflow)
10. [Configuration](#configuration)
11. [Installation & Setup](#installation--setup)
12. [Running the Application](#running-the-application)
13. [Development](#development)
14. [Security Considerations](#security-considerations)
15. [Extending the Application](#extending-the-application)

---

## Project Overview

**Projecttest-MCP** is a full-stack AI-powered technical interview system that automates candidate evaluation. The application leverages CrewAI (multi-agent AI framework) to create intelligent agents that:

- Analyze candidate CVs to extract experience level and tech stack
- Generate personalized interview questions based on the candidate's profile
- Evaluate candidate answers in real-time
- Create coding challenges suited to the candidate's skill level
- Grade code submissions and provide feedback
- Generate comprehensive PDF reports

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React + TypeScript)                    │
│  ┌───────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────────────┐ │
│  │ UploadCV  │───▶│ TechSelector │───▶│Questions │───▶│ CodingChallenge │ │
│  └───────────┘    └──────────────┘    └──────────┘    └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND (FastAPI + CrewAI)                        │
│  ┌─────────────┐   ┌─────────────┐   ┌───────────┐   ┌─────────┐  ┌──────┐ │
│  │ CV Analysis │   │  Question  │   │Evaluation│   │ Grading │  │MCP   │ │
│  │    Crew     │   │    Crew     │   │   Crew   │   │  Crew   │  │Client│ │
│  └─────────────┘   └─────────────┘   └───────────┘   └─────────┘  └──────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MCP SERVER (Code Execution)                          │
│                         Port: 8001 (streamable-http)                        │
│                    Supports: Python, JavaScript, Java, C#, C++             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19.2.0 | UI Framework |
| TypeScript | 5.9 | Type-safe JavaScript |
| Vite | 7.2.4 | Build tool |
| Monaco Editor | 4.7.0 | Code editor component |
| React Icons | 5.5.0 | Icon library |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | - | REST API framework |
| CrewAI | 1.9.3 | Multi-agent AI framework |
| Python | 3.10 - 3.13 | Runtime |
| UV | - | Package manager |
| Pydantic | - | Data validation |

### MCP Server
| Technology | Purpose |
|------------|---------|
| FastMCP | MCP protocol server |
| Subprocess | Code execution sandbox |

---

## Project Structure

```
projecttest-mcp/
├── backend/                          # FastAPI backend
│   ├── api.py                        # API endpoints
│   ├── pyproject.toml                # Python dependencies
│   ├── uv.lock                       # Locked dependencies
│   ├── src/projecttest/
│   │   ├── __init__.py
│   │   ├── main.py                   # CLI entry point
│   │   ├── analysis_crew.py         # CV Analysis Crew
│   │   ├── question_crew.py         # Question Generation Crew
│   │   ├── evaluation_crew.py       # Answer Evaluation Crew
│   │   ├── grading_crew.py          # Code Grading Crew
│   │   ├── challenge_crew.py        # Coding Challenge Crew
│   │   ├── crew_old.py              # Legacy crew implementation
│   │   ├── crew_validation.py      # Crew validation logic
│   │   ├── config/
│   │   │   ├── agents.yaml          # Agent definitions
│   │   │   ├── tasks.yaml           # Task definitions
│   │   │   ├── analysis_tasks.yaml  # CV analysis tasks
│   │   │   ├── question_tasks.yaml  # Question generation tasks
│   │   │   └── grading_tasks.yaml   # Code grading tasks
│   │   ├── models/
│   │   │   └── cv_analysis.py       # Pydantic data models
│   │   ├── utils/
│   │   │   ├── file_reader.py       # CV file parsing
│   │   │   ├── pdf_report.py        # PDF report generation
│   │   │   └── chart_generator.py   # Chart generation utilities
│   │   └── tools/
│   │       ├── __init__.py
│   │       ├── custom_tool.py       # Custom tools
│   │       ├── run_code_tool.py     # Code execution tool
│   │       └── code_runner.py       # Code runner utility
│   └── tests/                       # Backend tests
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── App.tsx                  # Main application
│   │   ├── App.css                  # Application styles
│   │   ├── main.tsx                 # Entry point
│   │   ├── index.css                # Global styles
│   │   ├── components/
│   │   │   ├── UploadCV.tsx         # CV upload component
│   │   │   ├── TechSelector.tsx     # Technology selection
│   │   │   ├── Questions.tsx        # Interview questions
│   │   │   └── CodingChallenge.tsx  # Coding challenge with editor
│   │   ├── services/
│   │   │   └── api.ts               # API client
│   │   ├── types/
│   │   │   └── candidate.ts         # TypeScript types
│   │   └── assets/
│   │       ├── react.svg
│   │       └── images/
│   │           └── icon1.png
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── eslint.config.js
│
├── mcp_server/                       # MCP Code Execution Server
│   └── server.py                     # FastMCP server (port 8001)
│
├── .venv/                            # Python virtual environment
├── README.md
└── PROJECT_DOCUMENTATION.md
```

---

## Components & Features

### Frontend Components

#### 1. UploadCV
- **File**: `frontend/src/components/UploadCV.tsx`
- **Purpose**: File upload interface for CV submission
- **Supported formats**: PDF, DOCX
- **Features**: Drag-and-drop, file validation

#### 2. TechSelector
- **File**: `frontend/src/components/TechSelector.tsx`
- **Purpose**: Allow candidates to select technology for interview
- **Features**: Displays tech stack extracted from CV

#### 3. Questions
- **File**: `frontend/src/components/Questions.tsx`
- **Purpose**: Display interview questions and accept answers
- **Features**: Sequential question display, real-time evaluation

#### 4. CodingChallenge
- **File**: `frontend/src/components/CodingChallenge.tsx`
- **Purpose**: Present coding challenge with in-browser code editor
- **Features**: Monaco Editor integration, syntax highlighting, code execution via MCP

### Backend Modules

#### CrewAI Crews
| Crew | File | Purpose |
|------|------|---------|
| CV Analysis | `analysis_crew.py` | Extract candidate info from CV |
| Question Generation | `question_crew.py` | Generate interview questions |
| Evaluation | `evaluation_crew.py` | Evaluate candidate answers |
| Grading | `grading_crew.py` | Grade code submissions |
| Challenge | `challenge_crew.py` | Generate coding challenges |

#### Utilities
| Module | File | Purpose |
|--------|------|---------|
| File Reader | `utils/file_reader.py` | Parse CV files (PDF, DOCX) |
| PDF Report | `utils/pdf_report.py` | Generate interview reports |
| Chart Generator | `utils/chart_generator.py` | Create visualizations |

---

## API Endpoints

### Base URL
```
http://127.0.0.1:8000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze-cv` | Analyze uploaded CV |
| POST | `/questions` | Generate interview questions |
| POST | `/evaluate-answer` | Evaluate candidate's answer |
| POST | `/coding-challenge` | Generate coding challenge |
| POST | `/grade-code` | Grade code submission |
| POST | `/run-code` | Execute code via MCP |

---

### POST /analyze-cv

Analyze a candidate's CV to extract information.

**Request:**
```http
POST /analyze-cv
Content-Type: multipart/form-data

file: <CV file (PDF/DOCX)>
```

**Response:**
```json
{
  "candidate_name": "John Doe",
  "experience_level": "Senior",
  "tech_stack": ["Python", "JavaScript", "React", "AWS"]
}
```

---

### POST /questions

Generate technology-specific interview questions.

**Request:**
```http
POST /questions
Content-Type: multipart/form-data

file: <CV file>
selected_tech: "Python"
```

**Response:**
```json
{
  "questions": [
    "Explain the difference between list and tuple in Python.",
    "What is a decorator in Python?",
    "How does garbage collection work in Python?"
  ],
  "total": 3
}
```

---

### POST /evaluate-answer

Evaluate a candidate's answer to an interview question.

**Request:**
```http
POST /evaluate-answer
Content-Type: application/x-www-form-urlencoded

question: "Explain closures in JavaScript"
answer: "A closure is..."
```

**Response:**
```json
{
  "score": 8,
  "feedback": "Good explanation of lexical scoping...",
  "correct": true
}
```

---

### POST /coding-challenge

Generate a coding challenge based on technology and experience level.

**Request:**
```http
POST /coding-challenge
Content-Type: multipart/form-data

file: <CV file>
selected_tech: "Python"
experience_level: "Senior"
```

**Response:**
```json
{
  "challenge": "Implement a function that..."
}
```

---

### POST /grade-code

Grade a candidate's code submission and generate PDF report.

**Request:**
```http
POST /grade-code
Content-Type: application/x-www-form-urlencoded

problem: "Implement binary search"
code: "def binary_search(arr, target):..."
```

**Response:**
```json
{
  "score": 85,
  "verdict": "pass",
  "feedback": "Efficient implementation..."
}
```

**Side Effect**: Generates PDF report in `reports/<candidate_name>_report.pdf`

---

### POST /run-code

Execute code via the MCP server and return results.

**Request:**
```json
{
  "language": "python",
  "code": "print('Hello, World!')"
}
```

**Response:**
```json
{
  "stdout": "Hello, World!\n",
  "stderr": "",
  "exit_code": 0
}
```

---

## AI Agents & Crews

### Agent Configuration

Agents are defined in `backend/src/projecttest/config/agents.yaml`:

```yaml
cv_analyzer:
  role: Technical Recruiter and CV Analyzer
  goal: Analyze a candidate CV to extract years of experience, determine seniority level, and list all relevant technical skills.
  backstory: You are an experienced technical recruiter...

interviewer:
  role: Senior Technical Interviewer
  goal: Design high-quality technical interview questions tailored to a candidate's experience level and chosen technology.
  backstory: You have conducted hundreds of technical interviews...

answer_grader:
  role: Technical Interview Evaluator
  goal: Evaluate interview answers fairly and realistically
  backstory: You are a senior engineer conducting technical interviews...
```

### Crew Workflows

1. **CV Analysis Crew**: Analyzes CV → Extracts candidate info → Returns structured data
2. **Question Crew**: Generates questions based on tech stack and experience
3. **Evaluation Crew**: Evaluates answers → Provides scores and feedback
4. **Grading Crew**: Grades code → Returns verdict and feedback
5. **Challenge Crew**: Creates coding challenges → Returns problem description

---

## MCP Code Runner Server

The MCP (Model Context Protocol) server provides code execution capabilities.

### Location
`mcp_server/server.py`

### Start Command
```bash
python mcp_server/server.py
```

### Server Details
- **Host**: 127.0.0.1
- **Port**: 8001
- **Protocol**: streamable-http
- **Endpoint**: `http://127.0.0.1:8001/mcp/`

### Supported Languages
| Language | Compiler/Runtime | Timeout |
|----------|------------------|---------|
| Python | `python` | 10s |
| JavaScript | `node` | 10s |
| Java | `javac` + `java` | 15s compile, 10s run |
| C# | `csc`/Mono | 15s compile, 10s run |
| C++ | `g++`/`clang++` | 15s compile, 10s run |

### Code Wrapping
The MCP server automatically wraps code snippets:
- Python: Direct execution
- JavaScript: Direct execution
- Java: Wraps in `class Main` if needed
- C#: Wraps in namespace with `Main` method
- C++: Adds `int main()` if missing

---

## Interview Workflow

```
┌─────────────┐     ┌─────────────┐     ┌───────────┐
│  1. Upload  │────▶│  2. Analyze │────▶│ 3. Select │
│     CV       │     │     CV      │     │   Tech    │
└─────────────┘     └─────────────┘     └───────────┘
                                                  │
                                                  ▼
┌─────────────┐     ┌─────────────┐     ┌───────────┐
│  8. Grade   │◀────│  7. Submit  │◀────│  6. Code  │
│    Code     │     │   Solution  │     │ Challenge │
└─────────────┘     └─────────────┘     └───────────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌───────────┐
│  9. Report │◀────│  5. Evaluate│◀────│  4. Answer │
│  (PDF)      │     │   Answers   │     │  Questions│
└─────────────┘     └─────────────┘     └───────────┘
```

### Step-by-Step

1. **Upload CV**: Candidate uploads PDF/DOCX resume
2. **Analyze CV**: AI extracts name, experience level, tech stack
3. **Select Tech**: Candidate chooses technology for interview
4. **Answer Questions**: Candidate answers generated questions
5. **Evaluate Answers**: AI evaluates each answer in real-time
6. **Coding Challenge**: AI generates a problem based on profile
7. **Submit Solution**: Candidate writes and submits code
8. **Grade Code**: AI grades the solution
9. **Generate Report**: PDF report is created with all results

---

## Configuration

### Environment Variables

Create `.env` in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Crew Configuration Files

| File | Purpose |
|------|---------|
| `config/agents.yaml` | Define agent roles, goals, backstories |
| `config/tasks.yaml` | Define task descriptions and expected outputs |
| `config/analysis_tasks.yaml` | CV analysis task definitions |
| `config/question_tasks.yaml` | Question generation task definitions |
| `config/grading_tasks.yaml` | Code grading task definitions |

### Data Models

Defined in `backend/src/projecttest/models/cv_analysis.py`:
- `CVAnalysis`: Pydantic model for CV analysis output

---

## Installation & Setup

### Prerequisites
- Python 3.10 - 3.13
- Node.js (for frontend)
- npm or yarn
- OpenAI API key

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies using UV
uv install

# Or using pip
pip install -e .
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Install specific dependencies (if needed)
npm install @monaco-editor/react react-icons
```

### MCP Server Setup

The MCP server uses FastMCP:
```bash
# Install MCP dependencies
pip install mcp fastmcp
```

---

## Running the Application

### Option 1: Full Stack (Recommended)

1. **Start MCP Server** (Terminal 1):
```bash
cd D:\dev\projecttest-mcp
python mcp_server/server.py
```

2. **Start Backend** (Terminal 2):
```bash
cd D:\dev\projecttest-mcp\backend
uvicorn api:app --reload --port 8000
```

3. **Start Frontend** (Terminal 3):
```bash
cd D:\dev\projecttest-mcp\frontend
npm run dev
```

4. **Access Application**:
- Frontend: http://localhost:5173
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

### Option 2: CLI Mode

The backend also supports a command-line interface:

```bash
cd backend
python -m projecttest.main
```

This runs an interactive interview in the terminal.

---

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest tests/
```

### Linting

**Frontend:**
```bash
cd frontend
npm run lint
```

### Building for Production

**Frontend:**
```bash
cd frontend
npm run build
```

### Adding New Crews

1. Create a new crew file in `backend/src/projecttest/`
2. Define agents in `config/agents.yaml`
3. Define tasks in `config/tasks.yaml`
4. Add endpoint in `api.py`
5. Update frontend to consume the new endpoint

### Adding New Components

1. Create component in `frontend/src/components/`
2. Add to `App.tsx` workflow
3. Update API service if needed

---

## Security Considerations

### Current Configuration (Development)
- CORS is set to allow all origins (`*`)
- No authentication on API endpoints
- Temporary files are cleaned up after each request

### Production Recommendations
1. **Restrict CORS**: Configure specific allowed origins
2. **Add Authentication**: Implement API key or OAuth
3. **Secure API Keys**: Use environment variables, never commit to git
4. **Code Execution Sandbox**: The MCP server runs code in subprocesses with timeouts - consider additional isolation for production
5. **Rate Limiting**: Implement request rate limiting
6. **Input Validation**: Add more robust file type validation
7. **PDF Storage**: Implement secure storage for generated reports

---

## Troubleshooting

### Common Issues

1. **MCP Server Not Running**
   - Error: "MCP server is not running"
   - Solution: Start with `python mcp_server/server.py`

2. **OpenAI API Key Missing**
   - Error: API key not found
   - Solution: Add `OPENAI_API_KEY` to `.env` file

3. **Port Already in Use**
   - Error: "Port 8000 is already in use"
   - Solution: Kill existing process or use different port

4. **CV Parsing Error**
   - Error: Cannot read CV file
   - Solution: Ensure file is PDF or DOCX format

5. **Frontend Build Fails**
   - Solution: Run `npm install` again, clear node_modules

---

## License

This project is a template powered by [crewAI](https://crewai.com).

---

## Support

- CrewAI Documentation: https://docs.crewai.com
- CrewAI GitHub: https://github.com/joaomdmoura/crewai
- Discord: https://discord.com/invite/X4JWnZnxPb

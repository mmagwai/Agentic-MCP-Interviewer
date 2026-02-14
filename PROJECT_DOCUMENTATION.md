# AI Technical Interviewer - Project Documentation

## Overview

AI Technical Interviewer is a full-stack application that automates technical candidate evaluation using AI agents. The system analyzes CVs, generates personalized interview questions, evaluates answers, provides coding challenges, and generates PDF reports.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React + TypeScript)           │
│  ┌───────────┐  ┌──────────────┐  ┌──────────┐  ┌────────────┐ │
│  │ UploadCV  │→│ TechSelector  │→│Questions │→│CodingChall │ │
│  └───────────┘  └──────────────┘  └──────────┘  └────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI + CrewAI)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌───────────┐ │
│  │ CV Analysis │  │ Interview   │  │ Answer   │  │ Code      │ │
│  │ Crew        │  │ Question    │  │ Evaluation│ │ Grading   │ │
│  └─────────────┘  └─────────────┘  └──────────┘  └───────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Frontend
- **Framework**: React 19.2.0
- **Language**: TypeScript 5.9
- **Build Tool**: Vite 7.2.4
- **Styling**: CSS Modules
- **Linting**: ESLint with TypeScript support

### Backend
- **Framework**: FastAPI
- **AI Framework**: CrewAI 1.9.3
- **Python Version**: 3.10 - 3.13
- **Package Manager**: UV

## Project Structure

```
projecttest/
├── backend/
│   ├── api.py                    # FastAPI endpoints
│   ├── pyproject.toml            # Backend dependencies
│   ├── .env                      # Environment variables
│   ├── knowledge/                # Knowledge base for AI agents
│   ├── src/projecttest/
│   │   ├── main.py               # CLI entry point
│   │   ├── analysis_crew.py      # CV analysis AI crew
│   │   ├── question_crew.py      # Interview question generation
│   │   ├── evaluation_crew.py    # Answer evaluation
│   │   ├── grading_crew.py      # Code grading
│   │   ├── challenge_crew.py    # Coding challenge generation
│   │   ├── utils/
│   │   │   ├── file_reader.py    # CV file parsing
│   │   │   └── pdf_report.py     # PDF report generation
│   │   └── models/
│   │       └── cv_analysis.py    # Data models
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── App.tsx               # Main application component
│   │   ├── App.css               # Application styles
│   │   ├── main.tsx              # Entry point
│   │   ├── components/
│   │   │   ├── UploadCV.tsx      # CV upload component
│   │   │   ├── TechSelector.tsx  # Technology selection
│   │   │   ├── Questions.tsx     # Interview questions display
│   │   │   └── CodingChallenge.tsx
│   │   ├── services/
│   │   │   └── api.ts            # API client
│   │   └── types/
│   │       └── candidate.ts      # TypeScript types
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
└── README.md
```

## API Endpoints

### CV Analysis
- **Endpoint**: `POST /analyze-cv`
- **Description**: Extracts candidate name, experience level, and tech stack from uploaded CV
- **Input**: PDF/DOCX file
- **Output**: JSON with candidate details

### Interview Questions
- **Endpoint**: `POST /questions`
- **Description**: Generates technology-specific interview questions based on CV
- **Input**: CV file, selected technology
- **Output**: Array of questions

### Answer Evaluation
- **Endpoint**: `POST /evaluate-answer`
- **Description**: Evaluates candidate's answer and provides feedback
- **Input**: Question, candidate answer
- **Output**: Score, feedback, correctness flag

### Coding Challenge
- **Endpoint**: `POST /coding-challenge`
- **Description**: Generates a coding challenge based on technology and experience level
- **Input**: CV file, technology, experience level
- **Output**: Coding problem description

### Code Grading
- **Endpoint**: `POST /grade-code`
- **Description**: Grades candidate's code submission
- **Input**: Problem description, code file
- **Output**: Score, verdict, feedback
- **Side Effect**: Generates PDF report

## Interview Workflow

1. **Upload CV**: Candidate uploads their CV (PDF/DOCX)
2. **CV Analysis**: AI extracts name, experience level, and tech stack
3. **Select Technology**: Candidate chooses which technology to be interviewed on
4. **Generate Questions**: AI generates personalized interview questions
5. **Answer Questions**: Candidate answers questions one by one
6. **Evaluate Answers**: AI evaluates each answer and provides feedback
7. **Coding Challenge**: AI generates a coding challenge
8. **Submit Solution**: Candidate submits code solution
9. **Grade Code**: AI grades the solution
10. **Generate Report**: PDF report is automatically generated

## Setup Instructions

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies using UV
uv install

# Configure environment variables
# Edit .env file and add your OPENAI_API_KEY

# Run the backend server
uvicorn api:app --reload
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Run linting
npm run lint
```

## Configuration

### Environment Variables (Backend)

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_api_key_here
```

### Crew Configuration

AI agents are configured in YAML files:
- `config/agents.yaml`: Agent definitions
- `config/tasks.yaml`: Task definitions

Modify these files to customize agent behavior.

## AI Crews

### CV Analysis Crew
Analyzes CV and extracts:
- Candidate name
- Experience level (Junior/Intermediate/Senior)
- Tech stack (programming languages, frameworks, tools)

### Interview Question Crew
Generates contextual interview questions based on:
- Candidate's tech stack
- Experience level
- Technology selected for interview

### Evaluation Crew
Evaluates candidate answers against:
- Technical accuracy
- Completeness
- Understanding depth

### Grading Crew
Grades code submissions based on:
- Correctness
- Code quality
- Efficiency
- Best practices

## Output

### PDF Report
The system generates a comprehensive PDF report containing:
- Candidate information
- Interview questions and answers
- Evaluation scores
- Coding challenge results
- Final recommendation

Output file: `interview_report.pdf`

## Dependencies

### Frontend Dependencies
```json
{
  "react": "^19.2.0",
  "react-dom": "^19.2.0"
}
```

### Backend Dependencies
```toml
crewai[google-genai,tools]==1.9.3
```

## Development

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn api:app --reload
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Access the application at `http://localhost:5173`

### CLI Mode

The backend also supports a CLI mode for testing:

```bash
cd backend
python -m projecttest.main
```

## Security Notes

- CORS is configured to allow all origins (`*`) for development
- In production, restrict CORS to specific domains
- API keys should never be committed to version control
- Temporary files are cleaned up after each request

## Extending the Application

### Adding New Crews

1. Create a new crew file in `backend/src/projecttest/`
2. Define agents and tasks
3. Add endpoint in `api.py`
4. Update frontend to consume the new endpoint

### Adding New Components

1. Create component in `frontend/src/components/`
2. Add to `App.tsx` workflow
3. Update API service if needed

## License

This project is a template powered by [crewAI](https://crewai.com).

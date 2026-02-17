# 🧠 Agentic MCP Technical Interviewer

An AI-powered multi-agent technical interview system built with:

- ⚡ FastAPI (Backend API)
- 🤖 CrewAI (Agent Orchestration)
- 🔌 MCP Server (Tool Execution Layer)
- 🎨 React + Vite (Frontend)
- 🧾 Report generation (PDF feedback)
- 📊 Code analysis & evaluation

This project simulates an intelligent technical interviewer using autonomous AI agents.

---

# 🏗️ Architecture Overview

The system consists of **three services**:

1. **Frontend** → React app (User Interface)
2. **Backend API** → FastAPI + CrewAI agents
3. **MCP Server** → Tool execution & controlled operations

All three services must run simultaneously in development.

---

# 🖥️ System Requirements

### Required Software

- ✅ Python **3.12.8**
- ✅ Node.js (LTS)
- ✅ Git

Verify installation:

```bash
python --version
node -v
npm -v
git --version

# Installation Guide


**Backend Setup**

Ensure your version of Python is 3.13 or Lower

1. Navigate to the backend folder

cd backend

2. Create Virtual Environment

python -m venv venv

3. Activate it

Windows: venv\Scripts\activate
Mac/Linux: source venv/bin/activate

4. Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt

5. Setup Environment Variables

create a .env file inside backend and paste your API key and Model, e.g:

OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=your_openai_key

6. Run the Backend:
uvicorn api:app --reload --port 8000
Your backend should run at:
http://127.0.0.1:8000




**MCP SERVER SETUP**

1. Open a new terminal and go to the mcp-server directory

cd mcp-server

2. Create a Virtual Environment and Activate it

python -m venv venv

venv\Scripts\activate

3. Install Requirements

pip install --upgrade pip
pip install -r requirements.txt

4. Run the Server

uvicorn main:app --port 8001

**Backend Setup**

1. Open a third terminal and install

npm install

2. Run The Front End

npm run dev

The frontend will run on:
http://localhost:5173

# BugFlow

BugFlow is an AI-powered bug lifecycle management platform built with FastAPI, React, TypeScript, Tailwind CSS, and SQLite.

## Run

```powershell
cd backend
..\.venv\Scripts\pip install -r requirements.txt
..\.venv\Scripts\alembic -c alembic.ini upgrade head
..\.venv\Scripts\uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000`; API health is at `http://localhost:8000/health`.

## Milestone 2

Severity and workflow enforcement, comments, attachments, activities, sprint planning, stored AI triage, local duplicate detection, advanced issue filtering, and expanded dashboard metrics are integrated into the existing platform.

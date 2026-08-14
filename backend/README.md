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

The frontend runs at `http://localhost:3000`; the API health endpoint is `http://localhost:8000/health`.

## Milestone 2

- Severity, enforced Open -> In Progress -> In Review -> Resolved workflow, and activity audit trail.
- Comments, validated file attachments, sprint planning and issue assignment.
- Stored local AI triage recommendations and local duplicate detection using Sentence Transformers/FAISS when available, with a deterministic local fallback.
- Issue-board filters and sorting plus dashboard severity, sprint, workflow, activity, and duplicate metrics.

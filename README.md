# BugFlow

BugFlow is a full-stack software issue tracking platform built with FastAPI, React, TypeScript, Tailwind CSS, and SQLite.

## Features
- JWT authentication and role-based access
- Project management
- Issue management with search, filters, and pagination
- Responsive modern dashboard

## Backend

### Install
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Run
```bash
uvicorn app.main:app --reload --port 8000
```

### Migrations
```bash
alembic upgrade head
```

## Frontend

### Install
```bash
cd frontend
npm install
```

### Run
```bash
npm run dev
```

## API URLs
- http://localhost:8000/health
- http://localhost:8000/api/auth/register
- http://localhost:8000/api/auth/login
- http://localhost:8000/api/projects
- http://localhost:8000/api/issues

## Folder Structure
- backend/app
- frontend/src
- docs
- scripts

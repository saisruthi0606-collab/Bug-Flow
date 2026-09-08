# BugFlow Architecture

```text
React Frontend
    |
Axios / REST API
    |
FastAPI Backend
    |
Services / Business Logic
    |
SQLAlchemy
    |
SQLite
```

The frontend uses React, TypeScript, Tailwind CSS, React Query, and Axios. FastAPI routes authenticate with JWT, validate Pydantic payloads, apply RBAC and resource visibility rules, and delegate AI, duplicate, risk, and activity behavior to services.

## AI and RAG flow

```text
User Question
  -> Query Processing
  -> Semantic + Lexical Retrieval
  -> RBAC Filtering
  -> Relevant BugFlow Context
  -> Gemini when configured
  -> Answer + Source IDs
```

Normal conversation can bypass retrieval. BugFlow questions use permitted issue, comment, activity, and historical resolution context. Gemini keys remain backend configuration.

## Defect intelligence flow

```text
Defect Report
  -> Validation and Classification
  -> Severity / Priority Assistance
  -> Semantic Search
  -> Similar Defects
  -> Historical Resolutions
  -> Resolution Assistance
  -> Developer Review
  -> Fix
  -> Verification
  -> Close
```

The final dashboard reuses persisted analytics for categories, severity, priority, status, backlog, trends, duplicate signals, resolution time, workload, sprint progress, and recent activity. It shows no-data states when a metric has no underlying records.
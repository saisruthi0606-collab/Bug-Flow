# BugFlow

## Intelligent Software Defect Tracking System With Resolution Assistance

BugFlow is an AI-powered software defect tracking and management system designed to help development teams report, track, analyze, prioritize, and resolve software defects efficiently.

The system combines conventional defect tracking with intelligent features such as Risk Radar, Retrieval-Augmented Generation (RAG), historical resolution assistance, AI-powered explanations, and an intelligent BugFlow Assistant.

---

## Features

### 1. Authentication and Role-Based Access Control

- Secure user authentication using JWT.
- Role-based access control (RBAC).
- Protected project, issue, sprint, analytics, and AI features.
- Users can access only the projects and issues they are authorized to view.
- Backend authorization is enforced independently of frontend filtering.

---

### 2. Project Management

BugFlow supports project-based defect management.

Users can:

- Create and manage projects.
- View project-specific issues.
- Organize defects by project.
- Manage project-related sprints.
- Analyze project-level engineering risk.

All project information is retrieved from the actual database.

---

### 3. Intelligent Issue Tracking

BugFlow provides complete defect lifecycle management.

Issues can contain:

- Issue ID
- Title
- Description
- Severity
- Priority
- Status
- Assigned developer
- Sprint
- Comments
- Attachments
- Activity history
- Creation and update timestamps

The system supports issue status progression such as:

`Open → Assigned → In Progress → Resolved → Verified → Closed`

Reopened issues are also tracked because they can contribute to engineering risk.

---

### 4. Defect Risk Radar

Risk Radar provides an intelligent view of engineering risk using the existing BugFlow risk heuristic.

Risk is evaluated using factors such as:

- Severity
- Priority
- Status
- Issue age
- Reopen history
- Sprint deadline
- Developer workload
- Duplicate/regression signals

The Risk Radar provides:

- Overall project risk score
- Risk level
- Critical / High / Medium / Low risk counts
- Risk factor breakdown
- Top-risk issues
- Recommended actions
- Individual issue risk scores
- Explain Risk functionality

#### Project-Wise Risk Radar

Risk Radar is designed at the project level.

Users can select a project and view risk information specifically for that project.

The selected project controls:

- Overall risk score
- Risk counts
- Risk factors
- Top risks
- Recommended actions
- Engineering Risk issue list
- Risk explanations
- BugFlow Assistant context

The system does not mix issues from different projects.

Only authorized project and issue data is included in risk calculations.

---

### 5. Explain Risk

For individual defects, BugFlow provides an **Explain Risk** feature.

The system explains why an issue has its current risk level using actual issue attributes.

The explanation can consider:

- Severity
- Priority
- Current status
- Issue age
- Reopen count
- Sprint/deadline information
- Developer workload
- Duplicate signals

The numerical risk score is calculated deterministically by the backend. AI is used only for explanation and assistance where appropriate.

---

### 6. BugFlow Assistant

BugFlow includes an intelligent assistant for questions about:

- Issues
- Previous resolutions
- Risk
- Projects
- Sprints
- Project trends
- Defect prioritization

The assistant provides immediate responses from available BugFlow data when a question can be answered deterministically.

For example, questions about an issue's:

- risk score
- severity
- priority
- status
- age
- reopen history

can be answered directly from the application's current data.

For deeper questions, the assistant can use Gemini and the BugFlow RAG pipeline.

The assistant also provides fallback responses when the AI service is unavailable but sufficient BugFlow data exists.

---

### 7. Retrieval-Augmented Generation (RAG)

BugFlow implements a custom Retrieval-Augmented Generation pipeline.

The architecture is:

```text
User Question
      ↓
Query Processing
      ↓
Retrieve Relevant BugFlow Data
      ↓
RBAC / Visibility Filtering
      ↓
Build Context
      ↓
Gemini
      ↓
Answer + Sources
````

The retrieval system can use:

* Semantic similarity
* Lexical matching/fallback
* Issue information
* Historical resolution information

RAG is used for BugFlow-specific questions while normal conversational questions can be handled without unnecessary retrieval.

The system also returns relevant issue/source references where applicable to improve traceability.

---

### 8. Historical Resolution Intelligence

BugFlow can retrieve previously resolved, verified, or closed issues to assist with resolving new defects.

This allows the system to identify relevant historical resolutions and provide useful context for similar defects.

Example workflow:

```text
New Defect
    ↓
Find Similar Historical Defects
    ↓
Retrieve Previous Resolution
    ↓
Provide Resolution Context
    ↓
Assist Developer
```

---

### 9. AI Bug Fix Impact Predictor

BugFlow includes an AI-assisted Bug Fix Impact Predictor.

It helps estimate the potential impact of modifying an issue or applying a fix.

The feature can use relevant issue/project information to provide an impact-oriented report.

The implementation is designed so that:

* Issue visibility follows existing RBAC.
* Baseline analysis remains available without depending entirely on Gemini.
* AI enhancement can provide additional explanation where available.

---

### 10. AI Issue Enhancement

BugFlow provides AI-assisted issue enhancement capabilities to improve defect information.

AI assistance can help generate or improve:

* Issue descriptions
* Reproduction information
* Technical summaries
* Resolution-oriented information

The existing issue data remains the source of truth.

---

### 11. Screenshot-Based Assistant

The BugFlow Assistant supports screenshot/image input.

Supported image formats include:

* PNG
* JPG
* JPEG
* WEBP

Images are validated before processing.

The system applies:

* File extension validation
* MIME validation
* File-size limits
* Image signature validation
* Authenticated upload handling

Uploaded screenshots are treated as untrusted input.

Raw images are not stored in chat history; the chat history stores image attachment metadata.

---

### 12. Sprint Management

BugFlow supports sprint-based defect organization.

Sprints can be associated with projects and issues.

Sprint information can be used for:

* Issue organization
* Progress tracking
* Deadline analysis
* Risk analysis
* Project health evaluation

Sprint progress is calculated from actual issue data rather than hardcoded percentages.

---

### 13. Analytics

BugFlow provides analytics for understanding defect and development activity.

Analytics can include information related to:

* Defect distribution
* Severity
* Priority
* Issue status
* Developer workload
* Resolution timing
* Duplicate defects
* Sprint progress
* Risk

Analytics are generated from actual application data.

---

### 14. Dashboard

The BugFlow Dashboard provides an overview of the current project and development activity.

Dashboard information can include:

* Issue statistics
* Sprint progress
* Defect distribution
* Recent activity
* Project information
* Risk-related information

Dashboard values are retrieved from the backend/database rather than using static demonstration values.

---

### 15. Comments and Activity Tracking

BugFlow supports issue collaboration through:

* Comments
* Activity history
* Issue updates
* Status changes
* Assignment changes

Activity information helps provide traceability throughout the defect lifecycle.

---

### 16. Notifications

BugFlow supports notifications for relevant project and issue events.

Notifications help users stay informed about changes requiring attention.

---

### 17. Attachments

Issues can contain attachments for supporting defect investigation.

Attachment access is protected through authenticated and path-safe serving mechanisms.

File validation is applied to uploaded content.

---

## Risk Analysis Architecture

BugFlow uses a deterministic risk heuristic rather than allowing an AI model to arbitrarily determine numerical risk.

The general flow is:

```text
Issue Data
   ↓
Severity
Priority
Status
Age
Reopen History
Sprint Deadline
Developer Workload
Duplicate Signals
   ↓
Risk Heuristic
   ↓
Issue Risk Score
   ↓
Risk Level
   ↓
Project-Level Risk Aggregation
   ↓
Risk Radar
```

Gemini can then be used to explain or summarize the calculated results.

This keeps numerical risk calculations consistent and explainable.

---

## Project-Level Risk Flow

```text
Select Project
      ↓
Validate User Authorization
      ↓
Retrieve Authorized Project Issues
      ↓
Calculate Individual Risk
      ↓
Aggregate Project Risk
      ↓
Generate Risk Factors
      ↓
Identify Top Risks
      ↓
Generate Recommended Actions
      ↓
Display Risk Radar
```

Only data belonging to the selected and authorized project is used.

---

## Technology Stack

### Frontend

* React
* TypeScript
* Tailwind CSS
* Axios
* Vite

### Backend

* Python 3.12
* FastAPI
* Pydantic
* JWT Authentication
* SQLite
* Pytest

### AI

* Google Gemini
* Custom RAG pipeline
* Semantic similarity retrieval
* Lexical retrieval fallback
* Historical resolution retrieval

### Development and Testing

* Git
* GitHub
* GitHub Actions
* Pytest
* Frontend production build

---

## System Architecture

```text
                 ┌──────────────────────┐
                 │      React UI        │
                 │ TypeScript + Tailwind│
                 └──────────┬───────────┘
                            │
                         Axios
                            │
                            ▼
                 ┌──────────────────────┐
                 │     FastAPI API      │
                 │ Authentication/RBAC  │
                 └──────────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
          SQLite       Risk Engine       RAG
              │             │             │
              │             │             ▼
              │             │          Gemini
              │             │
              └─────────────┴─────────────┐
                                           ▼
                              Intelligent BugFlow
                                   Assistance
```

---

## RAG Architecture

```text
                 User Question
                       │
                       ▼
                Query Processing
                       │
                       ▼
              Relevant Data Retrieval
                       │
                       ▼
                RBAC Filtering
                       │
                       ▼
                 Context Builder
                       │
                       ▼
                    Gemini
                       │
                       ▼
              Answer + Relevant Sources
```

The RAG system is implemented as a custom retrieval pipeline instead of depending on a separate orchestration framework.

---

## Database

BugFlow uses SQLite for local development and application data storage.

The database stores information such as:

* Users
* Projects
* Issues
* Sprints
* Comments
* Attachments
* Activity records
* Chat history
* Notifications
* Related AI/RAG information

Database indexes are used for frequently queried fields where appropriate.

---

## API Documentation

FastAPI automatically provides interactive API documentation.

When the backend is running:

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### ReDoc

```text
http://127.0.0.1:8000/redoc
```

Swagger UI allows developers to inspect endpoints, parameters, authentication requirements, and API responses.

---

## Running the Project

### Backend

Use Python 3.12.

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

Or from the backend directory:

```powershell
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The backend will run on:

```text
http://127.0.0.1:8000
```

### Frontend

Install dependencies and start the development server:

```bash
npm install
npm run dev
```

The frontend will normally run on:

```text
http://localhost:3000
```

---

## Environment Configuration

Create the required environment configuration for the backend.

Example:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash
```

Do not commit real API keys or credentials to GitHub.

---

## Testing

Backend tests are implemented using Pytest.

Run:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The test suite covers areas including:

* Authentication
* Authorization
* Issue management
* Risk analysis
* Risk Radar
* RAG
* BugFlow Assistant
* Security
* Project access
* AI-related functionality

The frontend can be validated using:

```bash
npm run build
```

---

## Security

BugFlow applies multiple security controls:

* JWT-based authentication
* Role-based access control
* Backend authorization
* Project ownership/access validation
* Issue visibility filtering
* RAG visibility filtering
* Authenticated attachment serving
* Path-safe file access
* File type validation
* File size validation
* Image signature validation
* Protection against registration-based role escalation
* Inactive-user rejection

AI-generated responses are constrained by the authorized BugFlow context.

---

## CI/CD

BugFlow uses GitHub Actions for automated validation.

The CI pipeline can validate:

* Python backend tests
* Backend compilation
* Frontend build
* Application regressions

This helps ensure that changes do not break existing functionality.

---

## Design Principles

BugFlow follows these principles:

1. **Real application data over hardcoded values**
2. **Backend authorization over frontend-only filtering**
3. **Deterministic calculations for numerical risk**
4. **AI for explanation and intelligent assistance**
5. **RAG for relevant project knowledge retrieval**
6. **Traceable AI responses using relevant sources**
7. **Graceful fallback when AI services are unavailable**
8. **Project-specific risk analysis**
9. **Secure handling of uploaded files**
10. **Preservation of existing functionality during feature enhancement**

---

## Milestone 2 — Lifecycle & Intelligence

Status:

```text
COMPLETED
```

Includes:

* Extended defect lifecycle
* Sprint management
* Kanban board
* Comments
* Attachments
* Activity history
* Notifications
* AI classification
* Severity/priority assistance
* Missing information detection
* Duplicate detection
* Semantic search
* Resolution assistance
* Root-cause assistance
* Investigation guidance

---

## Milestone 3 — Advanced AI & Intelligence

Status:

```text
COMPLETED
```

Includes:

* Analytics
* REST APIs
* RAG
* Gemini integration
* AI chatbot
* Normal conversational AI
* BugFlow-aware AI questions
* Chat history
* AI feedback
* Historical Resolution Intelligence
* Defect Risk Radar
* AI Bug Fix Impact Predictor
* CI/CD
* Documentation

---

# 35. Key Features Summary

| Feature                            | Status    |
| ---------------------------------- | --------- |
| User Authentication                | Completed |
| JWT Security                       | Completed |
| RBAC                               | Completed |
| Project Management                 | Completed |
| Defect CRUD                        | Completed |
| Defect Lifecycle                   | Completed |
| Sprint Management                  | Completed |
| Kanban Board                       | Completed |
| Comments                           | Completed |
| Attachments                        | Completed |
| Activity History                   | Completed |
| Notifications                      | Completed |
| AI Classification                  | Completed |
| Severity/Priority Assistance       | Completed |
| Duplicate Detection                | Completed |
| Semantic Search                    | Completed |
| AI Resolution Assistance           | Completed |
| Historical Resolution Intelligence | Completed |
| RAG                                | Completed |
| Gemini Integration                 | Completed |
| AI Chatbot                         | Completed |
| Chat History                       | Completed |
| AI Feedback                        | Completed |
| Analytics                          | Completed |
| Defect Risk Radar                  | Completed |
| AI Bug Fix Impact Predictor        | Completed |
| REST APIs                          | Completed |
| CI/CD                              | Completed |

---

# 36. Why BugFlow Stands Out

BugFlow is not only a traditional defect tracking application.

It combines:

```text
Defect Management
        +
Secure Authentication
        +
RBAC
        +
Lifecycle Management
        +
Collaboration
        +
AI Analysis
        +
Semantic Search
        +
RAG
        +
Generative AI
        +
Historical Resolution Intelligence
        +
Risk Prediction
        +
Fix Impact Prediction
        +
Analytics
```

This makes BugFlow an intelligent software engineering platform rather than a simple issue tracker.

---

# 37. Future Scope

Possible future enhancements include:

* Voice-based bug reporting
* OCR-based error extraction
* Automatic stack-trace analysis
* AI-generated test cases
* Release risk prediction
* Cross-project analytics
* CI/CD issue integration
* Mobile applications
* Advanced developer productivity analytics
* Automated regression-test recommendations
* Advanced AI-based code-change impact analysis

---

# 38. Security Reminder

Never commit the following to GitHub:

```text
.env
API keys
Passwords
JWT secrets
Database credentials
Private tokens
```

Use environment variables for sensitive configuration.

Example:

```env
GEMINI_API_KEY=your_key_here
```

---

# 39. Project Philosophy

BugFlow is built around three stages:

```text
DETECT
  ↓
Identify and understand defects

DEBUG
  ↓
Investigate, analyze and resolve defects

DELIVER
  ↓
Verify, close and improve software quality
```

---

# 40. Final Project Status

```text
MILESTONE 1 — FOUNDATION
                ✓ COMPLETED

MILESTONE 2 — LIFECYCLE & INTELLIGENCE
                ✓ COMPLETED

MILESTONE 3 — ADVANCED AI & INTELLIGENCE
                ✓ COMPLETED
```

BugFlow now provides a complete intelligent defect-management workflow combining full-stack application development, secure APIs, database management, AI-assisted defect analysis, RAG, generative AI, risk intelligence, fix-impact prediction, analytics, and automated CI/CD.

---

# BUGFLOW

## Detect. Debug. Deliver.

An intelligent defect tracking platform for modern software teams.

````

### One important thing amma

Before you push this README, **don't put your actual Gemini key anywhere in it**. Keep only:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
````

Your actual key should stay only in `backend/.env`, and `.env` should be in `.gitignore`.

Then:

```bash
git add .
git commit -m "Update README for completed Milestone 3"
git push origin main
```

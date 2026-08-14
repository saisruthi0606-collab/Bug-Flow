# Intelligent Software Defect Tracking System with Resolution Assistance

An intelligent full-stack software defect tracking platform that manages the complete defect lifecycle while providing AI-assisted defect analysis, duplicate detection, semantic search, debugging guidance, and resolution assistance.

## 📌 Project Overview

The **Intelligent Software Defect Tracking System with Resolution Assistance** extends a traditional defect tracking platform with intelligent capabilities.

The system supports the complete defect lifecycle:

**Report → Assign → Track → Analyze → Assist Resolution → Fix → Verify → Close**

Unlike traditional defect tracking systems, the platform uses AI to help teams:

- Classify software defects
- Suggest severity and priority
- Detect missing information in defect reports
- Identify potentially duplicate defects
- Search for semantically similar historical defects
- Suggest possible root causes
- Provide debugging guidance
- Recommend possible resolutions

The system is designed for collaboration between **Reporters, Developers, QA Testers, Project Managers, and Administrators**.

---

## 🎯 Key Objectives

- Centralize software defect management.
- Provide secure authentication and role-based access control.
- Track defects throughout their complete lifecycle.
- Enable project and sprint management.
- Support developer collaboration through comments and attachments.
- Maintain detailed activity and audit history.
- Provide real-time notifications for important defect events.
- Use AI to assist defect analysis and resolution.
- Reduce duplicate defect reports using semantic similarity.
- Help developers investigate defects using intelligent resolution assistance.

---

# 👥 User Roles

The system supports the following roles:

### 👤 Reporter

Responsible for reporting and tracking defects.

- Create/report defects
- Create projects where permitted
- View available developers
- Assign reported defects to developers
- Track defect progress
- View relevant comments, activities and notifications
- Use AI-assisted features

### 👨‍💻 Developer

Responsible for investigating and fixing assigned defects.

- View assigned defects
- Receive assignment notifications
- Work on defects
- Update defect status
- Add comments and attachments
- Use AI analysis and resolution assistance
- Resolve defects
- Create defects when required

### 🧪 QA Tester

Responsible for testing and verifying resolved defects.

- View defects requiring testing
- Test resolved defects
- Verify successful fixes
- Reopen defects when fixes fail
- Add comments and attachments
- View relevant activities and notifications
- Use existing AI assistance

### 📊 Project Manager

Responsible for project and workflow management.

- Create and manage projects
- Manage sprints
- Assign/reassign defects
- Monitor project progress
- Monitor sprint progress
- View analytics and activity
- Manage the defect workflow

### 🛡️ Admin

Provides system-wide management.

- Manage users and roles
- Manage projects
- Manage defects
- Manage assignments
- Manage sprints
- View system-wide information
- Manage system-level functionality

---

# 🔄 Defect Lifecycle

The system follows a structured defect lifecycle:

```text
Reported
   ↓
Assigned
   ↓
In Progress
   ↓
In Review
   ↓
Resolved
   ↓
Verified
   ↓
Closed



Sure amma ❤️ Here is the **same content in clean plain text/Markdown form**, without the broken formatting and unnecessary escape characters. You can directly paste this into your `README.md`.

````markdown
# 🤖 Intelligent Defect Analysis

The system introduces an intelligent layer on top of traditional defect tracking.

## 1. AI-Assisted Defect Classification

The system analyzes the defect title and description and can suggest:

- Defect category
- Defect type
- Component/module
- Severity
- Priority

### Example

**Input:**

> Payment page crashes when the user clicks Submit.

**AI Suggestion:**

```text
Category: Payment
Type: Functional Defect
Severity: High
Priority: High
````

The user remains responsible for accepting or modifying the suggestion.

---

# 📝 2. Missing Information Detection

The system can identify missing information in a defect report.

It can check for information such as:

* Operating System
* Browser
* Application version
* Reproduction steps
* Expected result
* Actual result
* Error message
* Relevant environment information

### Example

```text
Missing Information:
- Reproduction steps
- Browser
- Application version
```

This helps users create more complete and useful defect reports.

---

# 🔍 3. Duplicate Defect Detection

When a new defect is submitted, the system compares it with existing defects to identify potentially similar issues.

### Example

**New defect:**

> Application crashes when submitting payment.

**Existing defect:**

> Payment submission causes application crash.

The system can warn:

```text
⚠️ Possible Similar Defect Found

DEF-102
Payment submission crash

Similarity: 86%
```

This helps reduce duplicate defect entries.

---

# 🧠 4. Semantic Search

The system supports semantic similarity rather than relying only on exact keyword matching.

### Example

**Search:**

> Payment fails after clicking submit.

**Possible result:**

> Transaction crashes during checkout.

Even though the wording is different, the system can identify that the issues have similar meaning.

The existing implementation uses vector embeddings and similarity comparison for this functionality.

---

# 💡 5. Resolution Assistance

Resolution assistance is the major intelligent feature of the updated project.

When a developer opens a defect, the system can provide:

* Possible root causes
* Suggested investigation areas
* Debugging steps
* Possible resolution
* Recommended next action
* Similar historical defects
* Relevant previous resolution information where available

### Example

**Defect:**

> Payment crashes after clicking Submit.

**Resolution Assistance:**

```text
Possible Investigation Areas:

1. Check payment API response.
2. Check null/undefined handling.
3. Review frontend error handling.
4. Check server logs.
5. Review recent changes to the payment module.

Possible Resolution:

Validate the payment API response before processing
the transaction result and handle unexpected responses.
```

The AI provides **assistance**, not guaranteed automatic fixes.

The developer remains responsible for reviewing and applying the final solution.

---

# 🏃 Sprint Management

The system provides sprint planning and Kanban-based defect tracking.

Issues can be assigned to a specific sprint and managed through the defect lifecycle.

### Example

```text
┌──────────┬─────────────┬────────────┬───────────┐
│ Reported │ In Progress │ In Review  │ Resolved  │
├──────────┼─────────────┼────────────┼───────────┤
│ DEF-101  │ DEF-105     │ DEF-109    │ DEF-102   │
│ DEF-104  │ DEF-107     │            │ DEF-108   │
└──────────┴─────────────┴────────────┴───────────┘
```

---

# 💬 Collaboration

The platform supports collaboration through:

* Comments
* File attachments
* Activity history
* Defect history
* Notifications
* Developer assignment
* Sprint assignment

Important actions are recorded in the activity history.

---

# 🔔 Notifications

Users receive notifications for relevant events such as:

* Defect assignment
* Status changes
* Comments
* Attachments
* Important defect updates
* Other supported workflow events

### Example

```text
🔔 New Defect Assigned

DEF-105 has been assigned to you.
```

---

# 🔐 Authentication & Authorization

The application uses:

* JWT-based authentication
* Role-Based Access Control (RBAC)
* Protected API endpoints
* Role-specific permissions

Users can register and log in according to the available roles.

Backend authorization is used to prevent unauthorized operations.

---

# 🛠️ Technology Stack

## Frontend

* React
* TypeScript
* Tailwind CSS
* Axios
* Modern component-based UI

## Backend

* Python
* FastAPI
* SQLAlchemy
* Pydantic
* JWT Authentication

## Database

* PostgreSQL / SQLAlchemy-compatible relational database

## AI / Intelligent Layer

* Natural Language Processing
* Sentence Transformers
* `all-MiniLM-L6-v2`
* Vector embeddings
* Cosine / inner-product similarity
* Semantic duplicate detection
* AI-based defect analysis
* AI resolution assistance

## Development Tools

* Git
* GitHub
* VS Code
* Cline
* Docker / Docker Compose where configured

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │       Users         │
                    │ Reporter / Developer│
                    │ QA / PM / Admin     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   React Frontend    │
                    │  TypeScript + UI    │
                    └──────────┬──────────┘
                               │ REST API
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │ Authentication/RBAC │
                    └──────────┬──────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                 ▼                 ▼
     ┌──────────────┐  ┌──────────────┐  ┌───────────────┐
     │ PostgreSQL / │  │ AI Services  │  │ Notification  │
     │ SQLAlchemy   │  │ NLP/Embeddings│ │ & Activity    │
     └──────────────┘  └──────────────┘  └───────────────┘
```

---

# 📁 Project Structure

```text
BugFlow/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── db/
│   │   └── main.py
│   │
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── lib/
│   │   └── ...
│   │
│   └── package.json
│
├── scripts/
│
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/saisruthi0606-collab/Bug-Flow.git
cd Bug-Flow
```

---

## 2. Backend Setup

Create and activate a virtual environment.

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

Start the backend:

```powershell
cd backend
python -m uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

---

# 3. Frontend Setup

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL displayed by Vite.

---

# 🧪 Testing

## Backend

```powershell
cd backend
python -m pytest
```

## Frontend Build

```powershell
cd frontend
npm run build
```

---

# 🔄 Example End-to-End Workflow

```text
Reporter
   │
   ├── Create Project
   │
   ├── Report Defect
   │
   ├── AI Analysis
   │
   ├── Duplicate Detection
   │
   └── Assign Developer
          │
          ▼
Developer
   │
   ├── Notification
   ├── Analyze Defect
   ├── Semantic Search
   ├── Resolution Assistance
   ├── Add Comments
   ├── Fix Defect
   └── Mark Resolved
          │
          ▼
QA Tester
   │
   ├── Test Defect
   ├── Verify Fix
   │
   └── Reopen if Failed
          │
          ▼
Project Manager
   │
   └── Monitor Project/Sprint Progress
          │
          ▼
       Closed
```

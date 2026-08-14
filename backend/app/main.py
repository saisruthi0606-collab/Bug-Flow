from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db.migrations import initialize_database
from .models.user import User
from .models.project import Project
from .models.sprint import Sprint
from .models.issue import Issue
from .models.collaboration import AIRecommendation, Activity, Attachment, Comment
from .models.notification import Notification
from .api.routes import auth, projects, issues, users, ai, dashboard, sprints, collaboration, notifications
from .api.routes import uploads

app = FastAPI(title="BugFlow API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
initialize_database()
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(issues.router, prefix="/api/issues", tags=["issues"])
app.include_router(collaboration.router, prefix="/api/issues", tags=["collaboration"])
app.include_router(sprints.router, prefix="/api/sprints", tags=["sprints"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
@app.get("/health")
def health_check(): return {"status": "ok", "version": "2.0.0"}




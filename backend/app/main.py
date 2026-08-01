from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .db.database import Base, engine
from .models.user import User
from .models.project import Project
from .models.issue import Issue
from .api.routes import auth, projects, issues, users, ai, dashboard

app = FastAPI(title="BugFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(issues.router, prefix="/api/issues", tags=["issues"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

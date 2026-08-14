import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
from uuid import uuid4

from ...db.database import get_db
from ...models.issue import Issue
from ...models.user import User
from ...models.collaboration import Activity
from ...services.activity import log_activity
from ...utils.auth import (
    get_current_user,
    get_password_hash,
    verify_password,
)
from ...core.config import settings


router = APIRouter()


DEFAULT_PREFERENCES = {
    "in_app_notifications": True,
    "email_notifications": False,
    "ai_analysis_notifications": True,
    "critical_bug_alerts": True,
    "sprint_deadline_alerts": True,
    "compact_mode": False,
    "auto_refresh_dashboard": True,
    "default_landing_page": "/dashboard",
}


def preferences_for(user):
    try:
        return {
            **DEFAULT_PREFERENCES,
            **(
                json.loads(user.preferences)
                if user.preferences
                else {}
            ),
        }
    except json.JSONDecodeError:
        return DEFAULT_PREFERENCES.copy()


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    avatar_url: str | None = None
    language: str | None = None


class PreferencesUpdate(BaseModel):
    preferences: dict


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


@router.get("")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).filter(User.is_active.is_(True)).order_by(User.full_name.asc()).all()
    return [
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role,
        }
        for user in users
    ]


@router.get("/me")
def me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assigned = (
        db.query(Issue)
        .filter(Issue.assigned_to == current_user.id)
        .count()
    )

    resolved = (
        db.query(Issue)
        .filter(
            Issue.assigned_to == current_user.id,
            Issue.status == "Resolved",
        )
        .count()
    )

    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "avatar_url": current_user.avatar_url,
        "language": current_user.language,
        "preferences": preferences_for(current_user),
        "two_factor_enabled": current_user.two_factor_enabled,
        "last_login_at": current_user.last_login_at,
        "created_at": current_user.created_at,
        "projects": len(current_user.projects),
        "assigned_issues": assigned,
        "resolved_issues": resolved,
    }


@router.put("/me")
def update_me(
    payload: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, key, value)

    log_activity(
        db,
        None,
        current_user.id,
        "Profile Updated",
        "Updated profile information",
    )

    db.commit()
    db.refresh(current_user)

    return me(db, current_user)


@router.get("/activity")
def get_my_activity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activities = (
        db.query(Activity)
        .filter(Activity.actor_id == current_user.id)
        .order_by(Activity.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": activity.id,
            "issue_id": activity.issue_id,
            "actor_id": activity.actor_id,
            "actor_name": current_user.full_name,
            "action": activity.action,
            "details": activity.details,
            "created_at": activity.created_at,
        }
        for activity in activities
    ]


@router.post("/me/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in {".png", ".jpg", ".jpeg", ".gif"}:
        raise HTTPException(
            status_code=422,
            detail="Invalid avatar file",
        )

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    stored = f"{uuid4().hex}{suffix}"
    dest = upload_dir / stored

    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    current_user.avatar_url = f"/api/uploads/{stored}"

    log_activity(
        db,
        None,
        current_user.id,
        "Avatar Updated",
        "Profile avatar uploaded",
    )

    db.commit()
    db.refresh(current_user)

    return {
        "avatar_url": current_user.avatar_url
    }
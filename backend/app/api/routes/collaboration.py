import os
import shutil
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ...core.config import settings
from ...db.database import get_db
from ...models.collaboration import Attachment, Comment, Activity
from ...models.issue import Issue
from ...models.user import User
from ...schemas.issue import ActivityOut, AttachmentOut, CommentCreate, CommentOut, CommentUpdate
from ...services.activity import log_activity
from ...utils.auth import get_current_user

router = APIRouter()
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".pdf", ".txt", ".log", ".docx", ".zip"}

def can_view_issue(issue: Issue, user: User) -> bool:
    if user.role in {"Admin", "Project Manager"}:
        return True
    if user.role == "Reporter":
        return issue.reporter == user.id
    if user.role == "Developer":
        return issue.assigned_to == user.id or issue.reporter == user.id
    if user.role == "QA Tester":
        return issue.status in {"In Review", "Resolved"} or issue.reporter == user.id or issue.assigned_to == user.id
    return False

def get_issue(issue_id: int, db: Session, current_user: User) -> Issue:
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue: raise HTTPException(status_code=404, detail="Issue not found")
    if not can_view_issue(issue, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return issue

@router.get("/{issue_id}/comments", response_model=list[CommentOut])
def list_comments(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user); return db.query(Comment).filter(Comment.issue_id == issue_id).order_by(Comment.created_at.asc()).all()

@router.post("/{issue_id}/comments", response_model=CommentOut)
def add_comment(issue_id: int, payload: CommentCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user)
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Comment cannot be empty")
    comment = Comment(issue_id=issue_id, author_id=current_user.id, body=body); db.add(comment); log_activity(db, issue_id, current_user.id, "Comment Added", "Added a comment"); db.commit(); db.refresh(comment); return comment

@router.put("/{issue_id}/comments/{comment_id}", response_model=CommentOut)
def edit_comment(issue_id: int, comment_id: int, payload: CommentUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user)
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.issue_id == issue_id).first()
    if not comment: raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id and current_user.role != "Admin": raise HTTPException(status_code=403, detail="You can only edit your own comment")
    comment.body = payload.body.strip(); db.commit(); db.refresh(comment); return comment

@router.delete("/{issue_id}/comments/{comment_id}")
def delete_comment(issue_id: int, comment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user)
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.issue_id == issue_id).first()
    if not comment: raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != current_user.id and current_user.role != "Admin": raise HTTPException(status_code=403, detail="You can only delete your own comment")
    db.delete(comment); db.commit(); return {"message": "Comment deleted"}

@router.get("/{issue_id}/attachments", response_model=list[AttachmentOut])
def list_attachments(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user); return db.query(Attachment).filter(Attachment.issue_id == issue_id).order_by(Attachment.created_at.desc()).all()

@router.post("/{issue_id}/attachments", response_model=AttachmentOut)
def upload_attachment(issue_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user); suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS: raise HTTPException(status_code=422, detail="Allowed files: PNG, JPG, JPEG, PDF, TXT, LOG")
    upload_dir = Path(settings.upload_dir); upload_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{suffix}"; destination = upload_dir / stored_name
    with destination.open("wb") as output: shutil.copyfileobj(file.file, output)
    attachment = Attachment(issue_id=issue_id, uploaded_by=current_user.id, original_filename=file.filename or stored_name, stored_filename=stored_name, content_type=file.content_type, size_bytes=destination.stat().st_size)
    db.add(attachment); log_activity(db, issue_id, current_user.id, "Attachment Uploaded", attachment.original_filename); db.commit(); db.refresh(attachment); return attachment

@router.get("/{issue_id}/attachments/{attachment_id}/download")
def download_attachment(issue_id: int, attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user)
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id, Attachment.issue_id == issue_id).first()
    if not attachment: raise HTTPException(status_code=404, detail="Attachment not found")
    path = Path(settings.upload_dir) / attachment.stored_filename
    if not path.is_file(): raise HTTPException(status_code=404, detail="Attachment file not found")
    return FileResponse(path, filename=attachment.original_filename, media_type=attachment.content_type)

@router.delete("/{issue_id}/attachments/{attachment_id}")
def delete_attachment(issue_id: int, attachment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user)
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id, Attachment.issue_id == issue_id).first()
    if not attachment: raise HTTPException(status_code=404, detail="Attachment not found")
    if attachment.uploaded_by != current_user.id and current_user.role != "Admin": raise HTTPException(status_code=403, detail="You can only delete your own attachment")
    path = Path(settings.upload_dir) / attachment.stored_filename
    if path.is_file(): path.unlink()
    db.delete(attachment); log_activity(db, issue_id, current_user.id, "Attachment Deleted", attachment.original_filename); db.commit(); return {"message": "Attachment deleted"}

@router.get("/{issue_id}/activities", response_model=list[ActivityOut])
def list_activities(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue(issue_id, db, current_user); return db.query(Activity).filter(Activity.issue_id == issue_id).order_by(Activity.created_at.desc()).all()

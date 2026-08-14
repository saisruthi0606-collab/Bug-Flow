from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...models.issue import Issue
from ...models.sprint import Sprint
from ...models.user import User
from ...schemas.issue import SprintCreate, SprintOut, SprintUpdate
from ...services.activity import create_notification, log_activity
from ...utils.auth import get_current_user

router = APIRouter()

def get_sprint_or_404(sprint_id: int, db: Session) -> Sprint:
    sprint = db.query(Sprint).filter(Sprint.id == sprint_id).first()
    if not sprint: raise HTTPException(status_code=404, detail="Sprint not found")
    return sprint

@router.post("", response_model=SprintOut)
def create_sprint(payload: SprintCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if payload.end_date < payload.start_date: raise HTTPException(status_code=422, detail="End date must be on or after start date")
    sprint = Sprint(**payload.model_dump(), created_by=current_user.id); db.add(sprint); db.commit(); db.refresh(sprint)
    create_notification(db, current_user.id, None, "Sprint Created", f"Sprint '{sprint.name}' was created")
    db.commit()
    return sprint

@router.get("", response_model=list[SprintOut])
def list_sprints(project_id: int | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Sprint)
    if project_id: query = query.filter(Sprint.project_id == project_id)
    sprints = query.order_by(Sprint.start_date.desc()).all()
    for sprint in sprints: sprint.issue_count = len(sprint.issues)
    return sprints

@router.put("/{sprint_id}", response_model=SprintOut)
def update_sprint(sprint_id: int, payload: SprintUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sprint = get_sprint_or_404(sprint_id, db)
    if sprint.created_by != current_user.id and current_user.role != "Admin": raise HTTPException(status_code=403, detail="Not enough permissions")
    for field, value in payload.model_dump(exclude_unset=True).items(): setattr(sprint, field, value)
    if sprint.end_date < sprint.start_date: raise HTTPException(status_code=422, detail="End date must be on or after start date")
    db.commit(); db.refresh(sprint)
    create_notification(db, current_user.id, None, "Sprint Updated", f"Sprint '{sprint.name}' was updated")
    db.commit()
    sprint.issue_count = len(sprint.issues); return sprint

@router.delete("/{sprint_id}")
def delete_sprint(sprint_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sprint = get_sprint_or_404(sprint_id, db)
    if sprint.created_by != current_user.id and current_user.role != "Admin": raise HTTPException(status_code=403, detail="Not enough permissions")
    for issue in sprint.issues:
        issue.sprint_id = None; log_activity(db, issue.id, current_user.id, "Sprint Removed", f"Removed from {sprint.name}")
    create_notification(db, current_user.id, None, "Sprint Removed", f"Sprint '{sprint.name}' was deleted")
    db.delete(sprint); db.commit(); return {"message": "Sprint deleted"}

@router.post("/{sprint_id}/issues/{issue_id}")
def assign_issue(sprint_id: int, issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sprint = get_sprint_or_404(sprint_id, db); issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue: raise HTTPException(status_code=404, detail="Issue not found")
    if issue.project_id != sprint.project_id: raise HTTPException(status_code=422, detail="Issue must belong to the sprint project")
    issue.sprint_id = sprint.id
    log_activity(db, issue.id, current_user.id, "Sprint Assigned", f"Assigned to {sprint.name}")
    create_notification(db, current_user.id, issue.id, "Sprint Assigned", f"Issue '{issue.title}' was assigned to sprint '{sprint.name}'")
    if issue.assigned_to and issue.assigned_to != current_user.id:
        create_notification(db, issue.assigned_to, issue.id, "Sprint Assigned", f"Issue '{issue.title}' was assigned to sprint '{sprint.name}'")
    db.commit(); return {"message": "Issue assigned"}

@router.delete("/{sprint_id}/issues/{issue_id}")
def remove_issue(sprint_id: int, issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.sprint_id == sprint_id).first()
    if not issue: raise HTTPException(status_code=404, detail="Issue is not assigned to this sprint")
    issue.sprint_id = None; log_activity(db, issue.id, current_user.id, "Sprint Removed", "Removed from sprint"); db.commit(); return {"message": "Issue removed"}

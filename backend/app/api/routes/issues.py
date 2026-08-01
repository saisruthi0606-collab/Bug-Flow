from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...models.issue import Issue
from ...models.user import User
from ...schemas.issue import IssueCreate, IssueOut, IssueUpdate
from ...utils.auth import get_current_user

router = APIRouter()


@router.post("", response_model=IssueOut)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        status=issue.status,
        priority=issue.priority,
        severity=issue.severity,
        assigned_to=issue.assigned_to,
        reporter=current_user.id,
        project_id=issue.project_id,
    )
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.get("", response_model=list[IssueOut])
def get_issues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    page: int = 1,
    size: int = 10,
):
    query = db.query(Issue)
    if search:
        query = query.filter(Issue.title.contains(search))
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    return query.offset((page - 1) * size).limit(size).all()


@router.get("/{issue_id}", response_model=IssueOut)
def get_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.put("/{issue_id}", response_model=IssueOut)
def update_issue(issue_id: int, issue: IssueUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if db_issue.reporter != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    for field, value in issue.dict(exclude_unset=True).items():
        setattr(db_issue, field, value)
    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if db_issue.reporter != current_user.id and current_user.role != "Admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    db.delete(db_issue)
    db.commit()
    return {"message": "Issue deleted"}

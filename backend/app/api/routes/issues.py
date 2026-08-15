from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...models.collaboration import AIRecommendation, Comment
from ...models.issue import Issue
from ...models.user import User
from ...schemas.issue import DuplicateCandidate, DuplicateCheck, IssueCreate, IssueOut, IssueUpdate
from ...services.activity import log_activity
from ...services.duplicate_detection import create_embedding, deserialize_embedding, find_duplicates, serialize_embedding, similarity
from ...utils.auth import get_current_user
from .ai_service import get_ai_suggestions

router = APIRouter()
VALID_TRANSITIONS = {
    "Open": {"Assigned", "In Progress", "In Review", "Resolved"},
    "Assigned": {"Open", "In Progress", "In Review", "Resolved"},
    "In Progress": {"Open", "Assigned", "In Review", "Resolved"},
    "In Review": {"Open", "Assigned", "In Progress", "Resolved", "Verified"},
    "Resolved": {"Open", "In Progress", "In Review", "Verified", "Closed"},
    "Verified": {"Open", "In Progress", "In Review", "Resolved", "Closed"},
    "Closed": {"Open"},
}

# Roles allowed to perform lifecycle actions
MANAGER_ROLES = {"Admin", "Project Manager"}


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


def get_issue_or_404(issue_id: int, db: Session, current_user: User) -> Issue:
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if not can_view_issue(issue, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return issue


def can_manage_issue(issue: Issue, user: User) -> bool:
    return user.role in MANAGER_ROLES or issue.reporter == user.id or issue.assigned_to == user.id


@router.post("/duplicates-check", response_model=list[DuplicateCandidate])
def check_duplicates(payload: DuplicateCheck, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    candidates, _ = find_duplicates(db.query(Issue).all(), payload.title, payload.description, payload.project_id, limit=5)
    return candidates


@router.post("", response_model=IssueOut)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if issue.assigned_to is not None:
        assignee = db.query(User).filter(User.id == issue.assigned_to).first()
        if not assignee:
            raise HTTPException(status_code=422, detail="Assignee not found")
        if assignee.role != "Developer":
            raise HTTPException(status_code=422, detail="Only users with the Developer role can be assigned to issues")
    candidates, embedding = find_duplicates(db.query(Issue).all(), issue.title, issue.description, issue.project_id)
    if candidates and not issue.confirm_duplicate:
        raise HTTPException(status_code=409, detail={"message": "Possible duplicate issues found", "duplicates": candidates})
    analysis = get_ai_suggestions(issue.description or "", title=issue.title)
    duplicate_id = issue.duplicate_of_issue_id or (candidates[0]["id"] if candidates else None)
    db_issue = Issue(
        title=issue.title,
        description=issue.description,
        status="Open",
        priority=issue.priority or analysis["priority"],
        severity=issue.severity or analysis["severity"],
        category=issue.category or analysis["category"],
        assigned_to=issue.assigned_to,
        reporter=current_user.id,
        project_id=issue.project_id,
        sprint_id=issue.sprint_id,
        embedding=serialize_embedding(embedding),
        is_possible_duplicate=bool(candidates),
        duplicate_of_issue_id=duplicate_id,
    )
    db.add(db_issue)
    db.flush()
    db.add(
        AIRecommendation(
            issue_id=db_issue.id,
            category=analysis["category"],
            severity=analysis["severity"],
            priority=analysis["priority"],
            root_cause=analysis["root_cause"],
            suggested_resolution=analysis["resolution"],
            confidence_score=analysis["confidence_score"],
            reasoning=analysis["reasoning"],
        )
    )
    log_activity(db, db_issue.id, current_user.id, "Issue Created", "Created issue")
    if candidates:
        log_activity(db, db_issue.id, current_user.id, "Duplicate Detected", f"Possible duplicate match found for '{db_issue.title}'")
    log_activity(db, db_issue.id, current_user.id, "AI Analysis Completed", f"AI analysis completed for '{db_issue.title}'")
    if db_issue.sprint_id:
        log_activity(db, db_issue.id, current_user.id, "Sprint Assigned", "Assigned during creation")
    if db_issue.assigned_to:
        log_activity(db, db_issue.id, current_user.id, "Issue Assigned", f"Assigned to {db_issue.assignee_name or db_issue.assigned_to}")
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
    severity: str | None = None,
    sprint_id: int | None = None,
    assigned_to: int | None = None,
    project_id: int | None = None,
    category: str | None = None,
    semantic: bool = False,
    sort: str = "newest",
    page: int = 1,
    size: int = 50,
):
    query = db.query(Issue)
    # Role-based visibility filtering
    if current_user.role == "Reporter":
        query = query.filter(Issue.reporter == current_user.id)
    elif current_user.role == "Developer":
        query = query.filter((Issue.assigned_to == current_user.id) | (Issue.reporter == current_user.id))
    elif current_user.role == "QA Tester":
        query = query.filter(
            (Issue.status.in_(["In Review", "Resolved"]))
            | (Issue.reporter == current_user.id)
            | (Issue.assigned_to == current_user.id)
        )
    if search:
        query = query.filter((Issue.title.contains(search)) | (Issue.description.contains(search)))
    for field, value in [
        (Issue.status, status),
        (Issue.priority, priority),
        (Issue.severity, severity),
        (Issue.sprint_id, sprint_id),
        (Issue.assigned_to, assigned_to),
        (Issue.project_id, project_id),
        (Issue.category, category),
    ]:
        if value is not None and value != "":
            query = query.filter(field == value)

    severity_order = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
    priority_order = {"High": 3, "Medium": 2, "Low": 1}

    if sort == "oldest":
        query = query.order_by(Issue.created_at.asc())
    elif sort == "highest_severity":
        query = query.order_by(__import__("sqlalchemy").case(severity_order, value=Issue.severity, else_=0).desc())
    elif sort == "highest_priority":
        query = query.order_by(__import__("sqlalchemy").case(priority_order, value=Issue.priority, else_=0).desc())
    else:
        query = query.order_by(Issue.created_at.desc())

    results = query.offset((max(page, 1) - 1) * min(size, 100)).limit(min(size, 100)).all()

    # Semantic search: combine keyword results with meaning-based matches
    if semantic and search:
        try:
            target = create_embedding(search)
            all_issues = db.query(Issue).all()
            scored = []
            for issue in all_issues:
                if not can_view_issue(issue, current_user):
                    continue
                existing = deserialize_embedding(getattr(issue, "embedding", None)) or create_embedding(f"{issue.title} {issue.description or ''}")
                score = similarity(target, existing)
                if score >= 0.35:
                    scored.append((score, issue))
            scored.sort(key=lambda row: row[0], reverse=True)
            seen = {issue.id for issue in results}
            for score, issue in scored[:20]:
                if issue.id not in seen:
                    results.append(issue)
                    seen.add(issue.id)
        except Exception:
            # fall back to keyword-only results if semantic search fails
            pass

    return results


@router.get("/{issue_id}", response_model=IssueOut)
def get_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_issue_or_404(issue_id, db, current_user)


@router.get("/{issue_id}/recommendation")
def get_recommendation(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_issue_or_404(issue_id, db, current_user)
    recommendation = db.query(AIRecommendation).filter(AIRecommendation.issue_id == issue_id).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="No AI recommendation found")
    return recommendation


@router.get("/{issue_id}/missing-info")
def get_missing_info(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = get_issue_or_404(issue_id, db, current_user)
    from .ai_service import detect_missing_information
    warnings = detect_missing_information(issue.title, issue.description or "")
    return {"issue_id": issue.id, "warnings": warnings}


@router.get("/{issue_id}/ai-investigation")
def get_ai_investigation(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = get_issue_or_404(issue_id, db, current_user)
    comments = db.query(Comment).filter(Comment.issue_id == issue_id).order_by(Comment.created_at.asc()).all()
    comment_texts = [c.body for c in comments]
    from .ai_service import generate_debugging_suggestions
    suggestions = generate_debugging_suggestions(issue, comment_texts)
    # find similar previous issues
    similar = []
    try:
        all_issues = db.query(Issue).filter(Issue.id != issue_id).all()
        candidates, _ = find_duplicates(all_issues, issue.title, issue.description, issue.project_id, threshold=0.35, limit=5)
        similar = candidates
    except Exception:
        similar = []
    suggestions["similar_issues"] = similar
    return suggestions


@router.put("/{issue_id}", response_model=IssueOut)
def update_issue(issue_id: int, issue: IssueUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_issue = get_issue_or_404(issue_id, db, current_user)
    if not can_manage_issue(db_issue, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    changes = issue.model_dump(exclude_unset=True)

    # Validate assignee exists and is a Developer
    if "assigned_to" in changes and changes["assigned_to"] is not None:
        assignee = db.query(User).filter(User.id == changes["assigned_to"]).first()
        if not assignee:
            raise HTTPException(status_code=422, detail="Assignee not found")
        if assignee.role != "Developer":
            raise HTTPException(status_code=422, detail="Only users with the Developer role can be assigned to issues")

    if "status" in changes and changes["status"] != db_issue.status:
        if changes["status"] not in VALID_TRANSITIONS.get(db_issue.status, set()):
            raise HTTPException(status_code=422, detail=f"Invalid transition from {db_issue.status} to {changes['status']}")
        # RBAC for lifecycle actions
        new_status = changes["status"]
        if new_status == "Verified" and current_user.role not in {"Admin", "Project Manager", "QA Tester"}:
            raise HTTPException(status_code=403, detail="Only QA Tester, Project Manager or Admin can verify issues")
        if new_status == "Closed" and current_user.role not in {"Admin", "Project Manager", "QA Tester"}:
            raise HTTPException(status_code=403, detail="Only QA Tester, Project Manager or Admin can close issues")
        if new_status == "Open" and db_issue.status == "Closed" and current_user.role not in {"Admin", "Project Manager", "QA Tester", "Reporter"}:
            raise HTTPException(status_code=403, detail="Not enough permissions to reopen issue")
        log_activity(db, db_issue.id, current_user.id, "Issue Status Changed", f"{db_issue.status} to {changes['status']}")
        log_activity(db, db_issue.id, current_user.id, "Status Changed", f"{db_issue.status} to {changes['status']}")
        # Specific lifecycle activity labels
        lifecycle_actions = {
            "Resolved": "Issue Resolved",
            "Verified": "Issue Verified",
            "Closed": "Issue Closed",
            "Open": "Issue Reopened",
        }
        if new_status in lifecycle_actions:
            log_activity(db, db_issue.id, current_user.id, lifecycle_actions[new_status], f"{db_issue.status} to {new_status}")

    mapping = {
        "priority": "Priority Changed",
        "severity": "Severity Changed",
        "assigned_to": "Issue Assigned",
        "sprint_id": "Sprint Assigned",
    }
    for field, action in mapping.items():
        if field in changes and changes[field] != getattr(db_issue, field):
            log_activity(db, db_issue.id, current_user.id, action, f"Updated {field.replace('_', ' ')}")

    if any(field in changes for field in {"title", "description", "category", "project_id"}):
        log_activity(db, db_issue.id, current_user.id, "Issue Updated", "Updated issue details")
        log_activity(db, db_issue.id, current_user.id, "Issue Edited", "Updated issue details")

    for field, value in changes.items():
        setattr(db_issue, field, value)

    db.commit()
    db.refresh(db_issue)
    return db_issue


@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = get_issue_or_404(issue_id, db, current_user)
    if current_user.role not in MANAGER_ROLES and issue.reporter != current_user.id:
        raise HTTPException(status_code=403, detail="Only Admin, Project Manager or the reporter can delete this issue")
    # Clean up related records safely (only records tied to this issue)
    from ...models.collaboration import Activity, Attachment, Comment
    from ...models.notification import Notification
    db.query(Comment).filter(Comment.issue_id == issue_id).delete()
    db.query(Attachment).filter(Attachment.issue_id == issue_id).delete()
    db.query(Activity).filter(Activity.issue_id == issue_id).delete()
    db.query(Notification).filter(Notification.issue_id == issue_id).delete()
    db.query(AIRecommendation).filter(AIRecommendation.issue_id == issue_id).delete()
    db.delete(issue)
    db.commit()
    return {"message": "Issue deleted"}
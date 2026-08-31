"""Transparent heuristic for individual defect risk; this is not an ML model."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.collaboration import Activity
from ..models.issue import Issue


def risk_for_issue(issue: Issue, db: Session) -> dict:
    score = 0
    reasons: list[str] = []
    severity_points = {"Critical": 30, "High": 20, "Medium": 10, "Low": 3}
    priority_points = {"High": 15, "Medium": 8, "Low": 3}
    score += severity_points.get(issue.severity, 0)
    if severity_points.get(issue.severity, 0): reasons.append(f"{issue.severity} severity")
    score += priority_points.get(issue.priority, 0)
    if priority_points.get(issue.priority, 0) >= 8: reasons.append(f"{issue.priority} priority")
    now = datetime.now(timezone.utc)
    created = issue.created_at.replace(tzinfo=timezone.utc) if issue.created_at and issue.created_at.tzinfo is None else issue.created_at
    age_days = max(0, (now - created).days) if created else 0
    if issue.status not in {"Resolved", "Verified", "Closed"} and age_days >= 7:
        score += min(20, age_days)
        reasons.append(f"Unresolved for {age_days} days")
    if issue.status in {"Open", "Assigned", "In Progress"}:
        score += 8
    if issue.is_possible_duplicate:
        score += 8
        reasons.append("Possible duplicate detected")
    reopened = db.query(Activity).filter(Activity.issue_id == issue.id, Activity.action == "Issue Reopened").count()
    if reopened:
        score += min(10, reopened * 5)
        reasons.append("Previously reopened")
    if issue.sprint and issue.sprint.end_date:
        days_to_deadline = (issue.sprint.end_date - now.date()).days
        if issue.status not in {"Resolved", "Verified", "Closed"} and 0 <= days_to_deadline <= 3:
            score += 12
            reasons.append("Sprint deadline approaching")
    if issue.assigned_to and issue.status not in {"Resolved", "Verified", "Closed"}:
        workload = db.query(Issue).filter(Issue.assigned_to == issue.assigned_to, Issue.status.notin_(["Resolved", "Verified", "Closed"])).count()
        if workload >= 5:
            score += 7
            reasons.append("Assigned developer has high unresolved workload")
    score = min(100, score)
    level = "Critical" if score >= 75 else "High" if score >= 50 else "Medium" if score >= 25 else "Low"
    return {"issue_id": issue.id, "title": issue.title, "severity": issue.severity, "priority": issue.priority, "status": issue.status, "updated_at": issue.updated_at, "risk_score": score, "risk_level": level, "reasons": reasons[:5] or ["No elevated risk factors detected"]}

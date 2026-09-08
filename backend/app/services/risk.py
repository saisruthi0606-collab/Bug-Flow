"""Transparent heuristic for individual defect risk; this is not an ML model."""
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from ..models.collaboration import Activity
from ..models.issue import Issue


def serialize_utc(value: datetime | None) -> str | None:
    if value is None:
        return None
    aware = value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    return aware.isoformat().replace("+00:00", "Z")


def risk_for_issue(issue: Issue, db: Session) -> dict:
    score = 0
    reasons: list[str] = []
    factors = {"severity": 0, "priority": 0, "status": 0, "age": 0, "reopen": 0, "deadline": 0, "workload": 0, "duplicate": 0}
    severity_points = {"Critical": 30, "High": 20, "Medium": 10, "Low": 3}
    priority_points = {"High": 15, "Medium": 8, "Low": 3}
    factors["severity"] = severity_points.get(issue.severity, 0)
    score += factors["severity"]
    if severity_points.get(issue.severity, 0): reasons.append(f"{issue.severity} severity")
    factors["priority"] = priority_points.get(issue.priority, 0)
    score += factors["priority"]
    if priority_points.get(issue.priority, 0) >= 8: reasons.append(f"{issue.priority} priority")
    now = datetime.now(timezone.utc)
    created = issue.created_at.replace(tzinfo=timezone.utc) if issue.created_at and issue.created_at.tzinfo is None else issue.created_at
    age_days = max(0, (now - created).days) if created else 0
    status_points = {
        "Open": 12,
        "Assigned": 10,
        "In Progress": 8,
        "In Review": 5,
        "Resolved": -10,
        "Verified": -14,
        "Closed": -20,
    }
    status_point = status_points.get(issue.status, 0)
    factors["status"] = status_point
    score += factors["status"]
    if issue.status in {"Open", "Assigned", "In Progress"}:
        reasons.append(f"Issue is currently {issue.status}")
    elif issue.status in {"Resolved", "Verified", "Closed"}:
        reasons.append(f"Issue is {issue.status}, reducing active risk")
    if issue.status not in {"Resolved", "Verified", "Closed"} and age_days >= 7:
        factors["age"] = min(20, age_days)
        score += factors["age"]
        reasons.append(f"Unresolved for {age_days} days")
    if issue.is_possible_duplicate:
        factors["duplicate"] = 8
        score += factors["duplicate"]
        reasons.append("Possible duplicate detected")
    reopened = db.query(Activity).filter(Activity.issue_id == issue.id, Activity.action == "Issue Reopened").count()
    if reopened:
        factors["reopen"] = min(10, reopened * 5)
        score += factors["reopen"]
        reasons.append("Previously reopened")
    if issue.sprint and issue.sprint.end_date:
        days_to_deadline = (issue.sprint.end_date - now.date()).days
        if issue.status not in {"Resolved", "Verified", "Closed"} and 0 <= days_to_deadline <= 3:
            factors["deadline"] = 12
            score += factors["deadline"]
            reasons.append("Sprint deadline approaching")
    if issue.assigned_to and issue.status not in {"Resolved", "Verified", "Closed"}:
        workload = db.query(Issue).filter(Issue.assigned_to == issue.assigned_to, Issue.status.notin_(["Resolved", "Verified", "Closed"])).count()
        if workload >= 5:
            factors["workload"] = 7
            score += factors["workload"]
            reasons.append("Assigned developer has high unresolved workload")
    score = max(0, min(100, score))
    level = "Critical" if score >= 75 else "High" if score >= 50 else "Medium" if score >= 25 else "Low"
    if level in {"Critical", "High"}:
        recommendation = "Prioritize this defect for immediate developer attention."
    elif level == "Medium":
        recommendation = "Review this defect during the next triage or sprint planning session."
    else:
        recommendation = "No immediate action required; continue monitoring through the normal workflow."
    return {
        "issue_id": issue.id,
        "title": issue.title,
        "severity": issue.severity,
        "priority": issue.priority,
        "status": issue.status,
        "updated_at": serialize_utc(issue.updated_at),
        "risk_score": score,
        "risk_level": level,
        "reasons": reasons[:5] or ["No elevated risk factors detected"],
        "reopen_count": reopened,
        "age_days": age_days,
        "status_points": status_point,
        "recommendation": recommendation,
        "factors": factors,
    }

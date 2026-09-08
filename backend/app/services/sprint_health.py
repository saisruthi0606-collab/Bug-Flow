"""Deterministic sprint health scoring from persisted sprint and issue data."""
from datetime import date

from sqlalchemy.orm import Session

from ..models.collaboration import Activity
from ..models.issue import Issue
from ..models.sprint import Sprint

HEALTHY_THRESHOLD = 80
AT_RISK_THRESHOLD = 60
COMPLETED_STATUSES = {"Resolved", "Verified", "Closed"}
ACTIVE_STATUSES = {"Open", "Assigned", "In Progress", "In Review"}
SEVERITY_PENALTIES = {"Critical": 15, "High": 8, "Medium": 3, "Low": 1}


def _health_status(score: int | None) -> str:
    if score is None:
        return "No Data"
    if score >= HEALTHY_THRESHOLD:
        return "Healthy"
    if score >= AT_RISK_THRESHOLD:
        return "At Risk"
    return "Critical"


def calculate_sprint_health(sprint: Sprint, db: Session, today: date | None = None) -> dict:
    """Return an explainable score using only issues and activity in this sprint."""
    today = today or date.today()
    issues = db.query(Issue).filter(Issue.sprint_id == sprint.id).all()
    total_issues = len(issues)
    if not total_issues:
        return {
            "sprint_id": sprint.id,
            "score": None,
            "status": "No Data",
            "total_issues": 0,
            "completed_issues": 0,
            "remaining_issues": 0,
            "critical_remaining": 0,
            "high_remaining": 0,
            "reopened_issues": 0,
            "days_remaining": max(0, (sprint.end_date - today).days) if sprint.end_date else None,
            "reasons": ["No issues are assigned to this sprint yet."],
            "recommendation": "Add real sprint issues before evaluating sprint health.",
        }

    completed = [issue for issue in issues if issue.status in COMPLETED_STATUSES]
    remaining = [issue for issue in issues if issue.status in ACTIVE_STATUSES or issue.status not in COMPLETED_STATUSES]
    critical_remaining = sum(issue.severity == "Critical" for issue in remaining)
    high_remaining = sum(issue.severity == "High" for issue in remaining)
    issue_ids = [issue.id for issue in issues]
    reopened_count = db.query(Activity).filter(
        Activity.issue_id.in_(issue_ids), Activity.action == "Issue Reopened"
    ).count()

    score = 45 + round(len(completed) / total_issues * 55)
    reasons: list[str] = []
    completion_percent = round(len(completed) / total_issues * 100)
    if completion_percent >= 75:
        reasons.append(f"{len(completed)} of {total_issues} issues are completed.")
    else:
        score -= min(20, round((100 - completion_percent) * 0.2))
        reasons.append(f"{len(completed)} of {total_issues} issues are completed.")

    severity_penalty = sum(SEVERITY_PENALTIES.get(issue.severity, 0) for issue in remaining)
    score -= min(35, severity_penalty)
    if critical_remaining:
        reasons.append(f"{critical_remaining} critical issue(s) remain unresolved.")
    if high_remaining:
        reasons.append(f"{high_remaining} high-severity issue(s) remain unresolved.")

    days_remaining = (sprint.end_date - today).days if sprint.end_date else None
    if days_remaining is not None and remaining:
        if days_remaining < 0:
            score -= 20
            reasons.append("The sprint deadline has passed with unresolved issues.")
        elif days_remaining <= 3:
            score -= 15
            reasons.append(f"Only {days_remaining} day(s) remain before the sprint deadline.")
        elif days_remaining <= 7:
            score -= 8
            reasons.append(f"The sprint deadline is {days_remaining} day(s) away.")

    unresolved_assigned = {issue.assigned_to for issue in remaining if issue.assigned_to}
    max_workload = max(
        (sum(issue.assigned_to == assignee for issue in remaining) for assignee in unresolved_assigned),
        default=0,
    )
    if max_workload >= 5:
        score -= 7
        reasons.append("One developer has at least five unresolved sprint issues.")
    elif not unresolved_assigned and remaining:
        score -= 5
        reasons.append("Some unresolved sprint issues are unassigned.")
    else:
        reasons.append("Unresolved workload is assigned across the sprint team.")

    if reopened_count:
        score -= min(15, reopened_count * 5)
        reasons.append(f"{reopened_count} issue(s) were reopened.")

    score = max(0, min(100, score))
    status = _health_status(score)
    if status == "Healthy":
        recommendation = "Continue the current sprint plan and monitor remaining issues."
    elif status == "At Risk":
        recommendation = "Prioritize the remaining high-severity defects and review workload distribution."
    else:
        recommendation = "Focus immediately on critical defects, ownership, and the sprint deadline."
    return {
        "sprint_id": sprint.id,
        "score": score,
        "status": status,
        "total_issues": total_issues,
        "completed_issues": len(completed),
        "remaining_issues": len(remaining),
        "critical_remaining": critical_remaining,
        "high_remaining": high_remaining,
        "reopened_issues": reopened_count,
        "days_remaining": days_remaining,
        "reasons": reasons,
        "recommendation": recommendation,
    }
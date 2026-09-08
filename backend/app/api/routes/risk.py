from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.issue import Issue
from ...models.project import Project
from ...models.collaboration import Activity
from ...models.user import User
from ...services.rag import can_view
from ...services.risk import risk_for_issue
from ...utils.auth import get_current_user

router = APIRouter()


def can_access_project(project: Project, user: User) -> bool:
    return user.role in {"Admin", "Project Manager"} or project.created_by == user.id


@router.get("")
def risk_radar(project_id: int | None = Query(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = None
    if project_id is not None:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not can_access_project(project, current_user):
            raise HTTPException(status_code=403, detail="Not enough permissions for this project")
    issue_query = db.query(Issue)
    if project_id is not None:
        issue_query = issue_query.filter(Issue.project_id == project_id)
    risks = [risk_for_issue(issue, db) for issue in issue_query.all() if can_view(issue, current_user)]
    risks.sort(key=lambda item: item["risk_score"], reverse=True)
    if current_user.role in {"Admin", "Project Manager"}:
        role_label, role_issues = "Project Risk", risks
    elif current_user.role == "Developer":
        role_label = "Engineering Risk"
        assigned_ids = {issue.id for issue in db.query(Issue).filter(Issue.assigned_to == current_user.id).all()}
        role_issues = [item for item in risks if item["issue_id"] in assigned_ids]
    elif current_user.role == "QA Tester":
        role_label = "Quality / Verification Risk"
        reopened_ids = {row.issue_id for row in db.query(Activity).filter(Activity.action == "Issue Reopened").all()}
        role_issues = [item for item in risks if item["status"] in {"In Review", "Resolved", "Verified", "Closed"} or item["issue_id"] in reopened_ids]
    else:
        role_label, role_issues = "My Issue Risk", risks
    summary = {level: sum(item["risk_level"] == level for item in risks) for level in ("Critical", "High", "Medium", "Low")}
    overall_score = round(sum(item["risk_score"] for item in risks) / len(risks)) if risks else None
    overall_level = "Critical" if overall_score is not None and overall_score >= 80 else "At Risk" if overall_score is not None and overall_score >= 60 else "Moderate" if overall_score is not None and overall_score >= 40 else "Low" if overall_score is not None else "No Data"
    factor_names = ("severity", "priority", "status", "age", "reopen", "deadline", "workload", "duplicate")
    factor_totals = {factor: sum(item["factors"].get(factor, 0) for item in risks) for factor in factor_names}
    factor_breakdown = {factor: round(value / len(risks), 1) if risks else 0 for factor, value in factor_totals.items()}
    recommendations = []
    if factor_totals["severity"] or factor_totals["priority"]:
        recommendations.append("Prioritize critical and high-priority unresolved defects.")
    if factor_totals["age"]:
        recommendations.append("Resolve overdue high-risk issues.")
    if factor_totals["reopen"]:
        recommendations.append("Review reopened defects and verify their fixes.")
    if factor_totals["workload"]:
        recommendations.append("Review developer workload for high-risk assigned issues.")
    if factor_totals["duplicate"]:
        recommendations.append("Investigate duplicate or regression-prone defects.")
    if not recommendations and risks:
        recommendations.append("Continue monitoring the authorized issue set through the normal workflow.")
    drivers = [name for name, value in (("severity", factor_totals["severity"]), ("priority", factor_totals["priority"]), ("aging", factor_totals["age"]), ("reopened defects", factor_totals["reopen"])) if value]
    explanation = "No current authorized issue data is available." if not risks else "Current engineering risk is primarily driven by " + ", ".join(drivers) + "."
    return {"project_id": project.id if project else None, "project_name": project.project_name if project else None, "role": current_user.role, "role_label": role_label, "issues": risks, "role_issues": role_issues, "summary": summary, "overall": {"score": overall_score, "level": overall_level, "explanation": explanation}, "top_risks": risks[:5], "factor_breakdown": factor_breakdown, "recommendations": recommendations, "risk_trend": {"direction": None, "label": "No history", "message": "Risk history will appear as historical snapshots are collected."}, "methodology": "Transparent weighted heuristic based on severity, priority, age, status, duplicate signal, reopen history, sprint deadline, and workload."}


@router.get("/{issue_id}/explain")
def explain_risk(issue_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    issue = db.query(Issue).filter(Issue.id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    if not can_view(issue, current_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return risk_for_issue(issue, db)

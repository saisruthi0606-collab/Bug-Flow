from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.issue import Issue
from ...models.collaboration import Activity
from ...models.user import User
from ...services.rag import can_view
from ...services.risk import risk_for_issue
from ...utils.auth import get_current_user

router = APIRouter()


@router.get("")
def risk_radar(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    risks = [risk_for_issue(issue, db) for issue in db.query(Issue).all() if can_view(issue, current_user)]
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
    return {"role": current_user.role, "role_label": role_label, "issues": risks, "role_issues": role_issues, "summary": {level: sum(item["risk_level"] == level for item in risks) for level in ("Critical", "High", "Medium", "Low")}, "methodology": "Transparent weighted heuristic based on severity, priority, age, status, duplicate signal, reopen history, sprint deadline, and workload."}

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.issue import Issue
from ...models.user import User
from ...services.rag import can_view
from ...services.risk import risk_for_issue
from ...utils.auth import get_current_user

router = APIRouter()


@router.get("")
def risk_radar(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    risks = [risk_for_issue(issue, db) for issue in db.query(Issue).all() if can_view(issue, current_user)]
    risks.sort(key=lambda item: item["risk_score"], reverse=True)
    return {"issues": risks, "summary": {level: sum(item["risk_level"] == level for item in risks) for level in ("Critical", "High", "Medium", "Low")}, "methodology": "Transparent weighted heuristic based on severity, priority, age, status, duplicate signal, reopen history, sprint deadline, and workload."}

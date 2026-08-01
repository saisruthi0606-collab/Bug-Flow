from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.issue import Issue
from ...models.project import Project
from ...models.user import User
from ...utils.auth import get_current_user

router = APIRouter()

@router.get('', response_model=dict)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_projects = db.query(func.count(Project.id)).filter(Project.created_by == current_user.id).scalar() or 0
    total_issues = db.query(func.count(Issue.id)).scalar() or 0
    open_issues = db.query(func.count(Issue.id)).filter(Issue.status == 'Open').scalar() or 0
    resolved_issues = db.query(func.count(Issue.id)).filter(Issue.status == 'Resolved').scalar() or 0
    critical_issues = db.query(func.count(Issue.id)).filter(Issue.severity == 'Critical').scalar() or 0

    issue_status = [
        {'status': status, 'count': db.query(func.count(Issue.id)).filter(Issue.status == status).scalar() or 0}
        for status in ['Open', 'In Progress', 'Resolved', 'Blocked']
    ]
    priority_distribution = [
        {'priority': priority, 'count': db.query(func.count(Issue.id)).filter(Issue.priority == priority).scalar() or 0}
        for priority in ['High', 'Medium', 'Low']
    ]

    today = datetime.utcnow().date()
    seven_days_ago = today - timedelta(days=6)
    trends_query = (
        db.query(
            func.strftime('%Y-%m-%d', Issue.created_at).label('date'),
            func.count(Issue.id).label('count'),
        )
        .filter(Issue.created_at >= seven_days_ago)
        .group_by('date')
        .order_by('date')
    )
    trend_rows = {row.date: row.count for row in trends_query.all()}

    bug_trends = []
    for i in range(7):
        day = seven_days_ago + timedelta(days=i)
        bug_trends.append({'date': day.isoformat(), 'count': trend_rows.get(day.isoformat(), 0)})

    return {
        'total_projects': total_projects,
        'total_issues': total_issues,
        'open_issues': open_issues,
        'resolved_issues': resolved_issues,
        'critical_issues': critical_issues,
        'issue_status': issue_status,
        'priority_distribution': priority_distribution,
        'bug_trends': bug_trends,
    }

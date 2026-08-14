from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...models.collaboration import Activity
from ...models.issue import Issue
from ...models.project import Project
from ...models.sprint import Sprint
from ...models.user import User
from ...services.duplicate_detection import find_duplicates
from ...utils.auth import get_current_user

router = APIRouter()


@router.get('', response_model=dict)
def get_dashboard(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total_projects = db.query(func.count(Project.id)).filter(Project.created_by == current_user.id).scalar() or 0
    # Role-based issue visibility
    issue_query = db.query(Issue)
    if current_user.role == "Reporter":
        issue_query = issue_query.filter(Issue.reporter == current_user.id)
    elif current_user.role == "Developer":
        issue_query = issue_query.filter((Issue.assigned_to == current_user.id) | (Issue.reporter == current_user.id))
    elif current_user.role == "QA Tester":
        issue_query = issue_query.filter(
            (Issue.status.in_(["In Review", "Resolved"]))
            | (Issue.reporter == current_user.id)
            | (Issue.assigned_to == current_user.id)
        )
    visible_issue_ids = [i.id for i in issue_query.all()]
    total_issues = len(visible_issue_ids)
    statuses = ['Open', 'Assigned', 'In Progress', 'In Review', 'Resolved', 'Verified', 'Closed']
    issue_status = [{'status': s, 'count': db.query(func.count(Issue.id)).filter(Issue.status == s, Issue.id.in_(visible_issue_ids)).scalar() or 0} for s in statuses]
    priority_distribution = [{'priority': p, 'count': db.query(func.count(Issue.id)).filter(Issue.priority == p, Issue.id.in_(visible_issue_ids)).scalar() or 0} for p in ['High','Medium','Low']]
    severity_distribution = [{'severity': s, 'count': db.query(func.count(Issue.id)).filter(Issue.severity == s, Issue.id.in_(visible_issue_ids)).scalar() or 0} for s in ['Critical','High','Medium','Low']]
    sprint_summary = []
    for sprint in db.query(Sprint).order_by(Sprint.start_date.desc()).all():
        issue_count = db.query(func.count(Issue.id)).filter(Issue.sprint_id == sprint.id, Issue.id.in_(visible_issue_ids)).scalar() or 0
        resolved = db.query(func.count(Issue.id)).filter(Issue.sprint_id == sprint.id, Issue.status == 'Resolved', Issue.id.in_(visible_issue_ids)).scalar() or 0
        sprint_summary.append({'id': sprint.id, 'name': sprint.name, 'status': sprint.status, 'issue_count': issue_count, 'resolved_count': resolved, 'progress': round((resolved / issue_count * 100) if issue_count else 0)})
    recent_activity = [{'id': a.id, 'issue_id': a.issue_id, 'action': a.action, 'details': a.details, 'created_at': a.created_at.isoformat(), 'actor_id': a.actor_id} for a in db.query(Activity).filter(Activity.issue_id.in_(visible_issue_ids)).order_by(Activity.created_at.desc()).limit(10).all()]
    today = datetime.utcnow().date(); seven_days_ago = today - timedelta(days=6)
    rows = db.query(func.strftime('%Y-%m-%d', Issue.created_at).label('date'), func.count(Issue.id).label('count')).filter(Issue.created_at >= seven_days_ago, Issue.id.in_(visible_issue_ids)).group_by('date').all(); counts = {r.date:r.count for r in rows}
    open_issues = next(x['count'] for x in issue_status if x['status'] == 'Open')
    resolved_issues = next(x['count'] for x in issue_status if x['status'] == 'Resolved')
    critical_issues = next(x['count'] for x in severity_distribution if x['severity'] == 'Critical')
    duplicate_count = db.query(func.count(Issue.id)).filter(Issue.is_possible_duplicate.is_(True), Issue.id.in_(visible_issue_ids)).scalar() or 0
    all_issues = db.query(Issue).filter(Issue.id.in_(visible_issue_ids)).all()
    similar_issues = []
    for item in all_issues:
        if not item.title:
            continue
        matches, _ = find_duplicates(all_issues, item.title, item.description, item.project_id, threshold=0.25, limit=5)
        for match in matches:
            if match['id'] == item.id:
                continue
            similar_issues.append({
                'issue_id': item.id,
                'title': item.title,
                'similar_issue_id': match['id'],
                'similar_issue_title': next((i.title for i in all_issues if i.id == match['id']), 'Related issue'),
                'similarity': match['similarity'],
            })
    similar_issues = sorted(similar_issues, key=lambda row: row['similarity'], reverse=True)[:5]
    health_score = max(0, min(100, round(100 - (open_issues * 4) - (critical_issues * 6) - (duplicate_count * 3) + (resolved_issues * 2))))
    ai_report = {
        'summary': 'Issue health is stable with a moderate backlog and a manageable duplicate signal.',
        'risk_level': 'Medium' if open_issues > 5 or duplicate_count > 0 else 'Low',
        'insights': [
            f'{open_issues} open issues are currently awaiting action.',
            f'{duplicate_count} issue(s) were flagged as possible duplicates.',
            f'{resolved_issues} issues have already been resolved in the current workflow.'
        ],
        'recommendations': [
            'Prioritize critical and high-severity items before backlog expansion.',
            'Review duplicate candidates before creating additional work.',
            'Keep workflow progression moving to improve resolution throughput.'
        ]
    }
    return {
        'total_projects': total_projects,
        'total_issues': total_issues,
        'open_issues': open_issues,
        'resolved_issues': resolved_issues,
        'critical_issues': critical_issues,
        'issue_status': issue_status,
        'workflow_distribution': issue_status,
        'priority_distribution': priority_distribution,
        'severity_distribution': severity_distribution,
        'sprint_summary': sprint_summary,
        'recent_activity': recent_activity,
        'duplicate_detection': {'flagged_issues': duplicate_count, 'total_issues': total_issues},
        'bug_trends': [{'date': (seven_days_ago + timedelta(days=i)).isoformat(), 'count': counts.get((seven_days_ago + timedelta(days=i)).isoformat(), 0)} for i in range(7)],
        'ai_health_score': health_score,
        'ai_report': ai_report,
        'similar_issues': similar_issues,
    }

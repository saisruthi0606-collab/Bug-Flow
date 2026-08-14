from sqlalchemy.orm import Session
from ..models.collaboration import Activity
from ..models.notification import Notification
from ..models.issue import Issue


def create_notification(
    db: Session,
    user_id: int,
    issue_id: int | None,
    action: str,
    details: str | None = None
) -> None:
    db.add(
        Notification(
            user_id=user_id,
            issue_id=issue_id,
            kind=action,
            title=action,
            message=details or action
        )
    )


def log_activity(
    db: Session,
    issue_id: int | None,
    actor_id: int | None,
    action: str,
    details: str | None = None
) -> None:

    if issue_id is not None:
        db.add(
            Activity(
                issue_id=issue_id,
                actor_id=actor_id,
                action=action,
                details=details
            )
        )

    issue = (
        db.query(Issue)
        .filter(Issue.id == issue_id)
        .first()
        if issue_id is not None
        else None
    )

    targets = set()

    issue_actions = {
        "Issue Created",
        "Issue Updated",
        "Issue Assigned",
        "Issue Status Changed",
        "Comment Added",
        "Attachment Uploaded",
        "Attachment Deleted",
        "AI Analysis Completed",
        "AI Recommendation Generated",
        "Duplicate Detected",
        "Status Changed",
        "Issue Resolved",
        "Issue Verified",
        "Issue Closed",
        "Issue Reopened",
    }

    if issue and action in issue_actions:

        if issue.reporter:
            targets.add(issue.reporter)

        if issue.assigned_to:
            targets.add(issue.assigned_to)

        if action == "Comment Added" and actor_id is not None:
            targets.add(actor_id)

    if action in {
        "Sprint Created",
        "Sprint Updated",
        "Sprint Assigned",
        "Sprint Removed"
    } and actor_id is not None:
        targets.add(actor_id)

    if (
        action == "Issue Assigned"
        and issue
        and issue.assigned_to
        and issue.assigned_to != actor_id
    ):
        targets.add(issue.assigned_to)

    if (
        action == "Sprint Assigned"
        and issue
        and issue.assigned_to
        and issue.assigned_to != actor_id
    ):
        targets.add(issue.assigned_to)

    for uid in sorted(targets):
        create_notification(
            db,
            uid,
            issue_id,
            action,
            details or action
        )
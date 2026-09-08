"""add indexes for common issue, collaboration, and notification queries"""

from alembic import op

revision = "006_milestone4_indexes"
down_revision = "005_impact_prediction_records"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_issues_project_status", "issues", ["project_id", "status"])
    op.create_index("ix_issues_assignee_status", "issues", ["assigned_to", "status"])
    op.create_index("ix_issues_sprint_status", "issues", ["sprint_id", "status"])
    op.create_index("ix_issues_created_at", "issues", ["created_at"])
    op.create_index("ix_comments_issue_created", "comments", ["issue_id", "created_at"])
    op.create_index("ix_activities_issue_created", "activities", ["issue_id", "created_at"])
    op.create_index("ix_notifications_user_read_created", "notifications", ["user_id", "is_read", "created_at"])


def downgrade():
    op.drop_index("ix_notifications_user_read_created", table_name="notifications")
    op.drop_index("ix_activities_issue_created", table_name="activities")
    op.drop_index("ix_comments_issue_created", table_name="comments")
    op.drop_index("ix_issues_created_at", table_name="issues")
    op.drop_index("ix_issues_sprint_status", table_name="issues")
    op.drop_index("ix_issues_assignee_status", table_name="issues")
    op.drop_index("ix_issues_project_status", table_name="issues")
from sqlalchemy import inspect, text
from .database import Base, engine

def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    additions = {
        "users": {"avatar_url": "VARCHAR(500)", "language": "VARCHAR(10) DEFAULT 'en'", "preferences": "TEXT", "two_factor_enabled": "BOOLEAN DEFAULT 0", "last_login_at": "DATETIME"},
        "issues": {"category": "VARCHAR(100)", "sprint_id": "INTEGER", "embedding": "TEXT", "is_possible_duplicate": "BOOLEAN DEFAULT 0", "duplicate_of_issue_id": "INTEGER"},
        "chat_messages": {"conversation_id": "VARCHAR(100)"},
    }
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, columns in additions.items():
            existing = {column['name'] for column in inspector.get_columns(table)}
            for name, definition in columns.items():
                if name not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))
        indexes = (
            "CREATE INDEX IF NOT EXISTS ix_issues_project_status ON issues (project_id, status)",
            "CREATE INDEX IF NOT EXISTS ix_issues_assignee_status ON issues (assigned_to, status)",
            "CREATE INDEX IF NOT EXISTS ix_issues_sprint_status ON issues (sprint_id, status)",
            "CREATE INDEX IF NOT EXISTS ix_issues_created_at ON issues (created_at)",
            "CREATE INDEX IF NOT EXISTS ix_comments_issue_created ON comments (issue_id, created_at)",
            "CREATE INDEX IF NOT EXISTS ix_activities_issue_created ON activities (issue_id, created_at)",
            "CREATE INDEX IF NOT EXISTS ix_notifications_user_read_created ON notifications (user_id, is_read, created_at)",
        )
        for statement in indexes:
            connection.execute(text(statement))

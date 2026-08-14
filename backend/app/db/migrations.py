from sqlalchemy import inspect, text
from .database import Base, engine

def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    additions = {
        "users": {"avatar_url": "VARCHAR(500)", "language": "VARCHAR(10) DEFAULT 'en'", "preferences": "TEXT", "two_factor_enabled": "BOOLEAN DEFAULT 0", "last_login_at": "DATETIME"},
        "issues": {"category": "VARCHAR(100)", "sprint_id": "INTEGER", "embedding": "TEXT", "is_possible_duplicate": "BOOLEAN DEFAULT 0", "duplicate_of_issue_id": "INTEGER"},
    }
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table, columns in additions.items():
            existing = {column['name'] for column in inspector.get_columns(table)}
            for name, definition in columns.items():
                if name not in existing:
                    connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))

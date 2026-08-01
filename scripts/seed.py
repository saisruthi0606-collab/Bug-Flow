from app.db.database import SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.issue import Issue
from app.utils.auth import get_password_hash


def seed():
    db = SessionLocal()
    if db.query(User).count() == 0:
        admin = User(full_name='Admin User', email='admin@bugflow.com', password_hash=get_password_hash('password123'), role='Admin')
        db.add(admin)
        db.commit()
        db.refresh(admin)
        project = Project(project_name='BugFlow MVP', description='Initial milestone project', created_by=admin.id)
        db.add(project)
        db.commit()
        db.refresh(project)
        issue = Issue(title='Login issue', description='User login flow needs polish', status='Open', priority='High', severity='Medium', reporter=admin.id, project_id=project.id)
        db.add(issue)
        db.commit()
    db.close()


if __name__ == '__main__':
    seed()

import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.database import Base
from app.models.issue import Issue
from app.models.notification import Notification
from app.models.project import Project
from app.models.user import User
from app.services.activity import log_activity


class NotificationFlowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(bind=self.engine)
        self.session = Session(bind=self.engine)

        self.reporter = User(full_name='Reporter', email='reporter@test.com', password_hash='x', role='Reporter')
        self.assignee = User(full_name='Assignee', email='assignee@test.com', password_hash='x', role='Developer')
        self.project = Project(project_name='Demo', created_by=1)
        self.session.add_all([self.reporter, self.assignee, self.project])
        self.session.commit()

        self.issue = Issue(
            title='Bug',
            description='Need fix',
            status='Open',
            priority='High',
            severity='Critical',
            project_id=self.project.id,
            reporter=self.reporter.id,
            assigned_to=self.assignee.id,
        )
        self.session.add(self.issue)
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_issue_created_generates_notification(self):
        self.session.query(Notification).delete()
        log_activity(self.session, self.issue.id, self.reporter.id, 'Issue Created', 'Created issue')
        self.session.commit()

        rows = self.session.query(Notification).filter(Notification.issue_id == self.issue.id).all()
        self.assertGreaterEqual(len(rows), 1)
        self.assertTrue(any(row.user_id == self.assignee.id for row in rows))

    def test_comment_added_generates_notification(self):
        self.session.query(Notification).delete()
        log_activity(self.session, self.issue.id, self.reporter.id, 'Comment Added', 'Added a comment')
        self.session.commit()

        rows = self.session.query(Notification).filter(Notification.issue_id == self.issue.id).all()
        self.assertGreaterEqual(len(rows), 1)
        self.assertTrue(any(row.user_id == self.assignee.id for row in rows))


if __name__ == '__main__':
    unittest.main()

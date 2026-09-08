import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.rag import deterministic_bugflow_answer
from app.api.routes.dashboard import serialize_utc


class QueryStub:
    def __init__(self, value=None):
        self.value = value

    def filter(self, *args):
        return self

    def first(self):
        return self.value

    def count(self):
        return 0


class DashboardDataTests(unittest.TestCase):
    def test_naive_database_timestamp_is_serialized_as_explicit_utc(self):
        timestamp = datetime(2026, 8, 27, 11, 29, 0)
        self.assertEqual(serialize_utc(timestamp), "2026-08-27T11:29:00Z")
        aware = datetime(2026, 8, 27, 11, 29, tzinfo=timezone.utc)
        self.assertEqual(serialize_utc(aware), "2026-08-27T11:29:00Z")

    def test_dashboard_returns_unique_real_sprint_rows_and_completed_statuses(self):
        client = TestClient(app)
        email = f"dashboard-{uuid4().hex}@example.com"
        self.assertEqual(client.post("/api/auth/register", json={"full_name": "Dashboard Tester", "email": email, "password": "password123"}).status_code, 200)
        token = client.post("/api/auth/login", json={"email": email, "password": "password123"}).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        project = client.post("/api/projects", json={"project_name": "Dashboard Data Project", "description": "Test"}, headers=headers)
        self.assertEqual(project.status_code, 200, project.text)
        project_id = project.json()["id"]
        sprint = client.post("/api/sprints", json={"name": "Actual Sprint", "goal": "Test", "start_date": "2026-08-01", "end_date": "2026-09-30", "status": "Active", "project_id": project_id}, headers=headers)
        self.assertEqual(sprint.status_code, 200, sprint.text)
        sprint_id = sprint.json()["id"]
        for title, status in (("Completed dashboard issue", "Closed"), ("Open dashboard issue", "Open")):
            issue = client.post("/api/issues", json={"title": title, "description": "Dashboard test", "project_id": project_id, "sprint_id": sprint_id, "status": status, "confirm_duplicate": True}, headers=headers)
            self.assertEqual(issue.status_code, 200, issue.text)
            if status == "Closed":
                updated = client.put(f"/api/issues/{issue.json()['id']}", json={"status": "In Progress"}, headers=headers)
                self.assertEqual(updated.status_code, 200, updated.text)
                updated = client.put(f"/api/issues/{issue.json()['id']}", json={"status": "Resolved"}, headers=headers)
                self.assertEqual(updated.status_code, 200, updated.text)
        dashboard = client.get("/api/dashboard", headers=headers)
        self.assertEqual(dashboard.status_code, 200, dashboard.text)
        rows = [row for row in dashboard.json()["sprint_summary"] if row["id"] == sprint_id]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["total_issues"], 2)
        self.assertEqual(rows[0]["completed_issues"], 1)
        self.assertEqual(rows[0]["progress_percent"], 50)

    def test_direct_risk_answer_does_not_return_greeting(self):
        issue = SimpleNamespace(id=20, title="Login failure", severity="High", priority="High", status="Open", reporter=4, assigned_to=None, created_at=None, updated_at=None, is_possible_duplicate=False, sprint=None)

        class Db:
            def query(self, model):
                return QueryStub(issue)

        answer = deterministic_bugflow_answer("Why is BUG-20 high risk?", Db(), SimpleNamespace(id=4, role="Reporter"))
        self.assertNotIn("Hello!", answer)
        self.assertIn("BUG-20", answer)

    def test_risk_radar_is_project_scoped_and_authorized(self):
        client = TestClient(app)
        first_email = f"risk-project-a-{uuid4().hex}@example.com"
        second_email = f"risk-project-b-{uuid4().hex}@example.com"
        for email in (first_email, second_email):
            self.assertEqual(client.post("/api/auth/register", json={"full_name": "Risk Project Tester", "email": email, "password": "password123"}).status_code, 200)
        first_token = client.post("/api/auth/login", json={"email": first_email, "password": "password123"}).json()["access_token"]
        second_token = client.post("/api/auth/login", json={"email": second_email, "password": "password123"}).json()["access_token"]
        first_headers = {"Authorization": f"Bearer {first_token}"}
        second_headers = {"Authorization": f"Bearer {second_token}"}
        first_project = client.post("/api/projects", json={"project_name": "Risk Project A", "description": "A"}, headers=first_headers).json()
        second_project = client.post("/api/projects", json={"project_name": "Risk Project B", "description": "B"}, headers=second_headers).json()
        scoped = client.get(f"/api/risk?project_id={first_project['id']}", headers=first_headers)
        self.assertEqual(scoped.status_code, 200, scoped.text)
        self.assertEqual(scoped.json()["project_id"], first_project["id"])
        self.assertIsNone(scoped.json()["overall"]["score"])
        denied = client.get(f"/api/risk?project_id={second_project['id']}", headers=first_headers)
        self.assertEqual(denied.status_code, 403)


if __name__ == "__main__":
    unittest.main()

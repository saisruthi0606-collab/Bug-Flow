import unittest
import json
from fastapi.testclient import TestClient
from app.main import app


class ApiFlowTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # register a fresh admin user for testing
        self.email = "apitest@bugflow.com"
        self.password = "password123"
        reg = self.client.post("/api/auth/register", json={"full_name": "API Test Admin", "email": self.email, "password": self.password, "role": "Admin"})
        if reg.status_code == 400:
            # user already exists, that's fine
            pass
        self.token = self.login()
        # ensure the admin has a project for issue tests
        projects = self.client.get("/api/projects", headers=self.auth(self.token)).json()
        if not projects:
            self.client.post("/api/projects", json={"project_name": "API Test Project", "description": "Test project"}, headers=self.auth(self.token))

    def login(self, email=None, password=None):
        email = email or self.email
        password = password or self.password
        res = self.client.post("/api/auth/login", json={"email": email, "password": password})
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()["access_token"]

    def auth(self, token):
        return {"Authorization": f"Bearer {token}"}

    def test_login_and_users_list(self):
        token = self.login()
        res = self.client.get("/api/users", headers=self.auth(token))
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIsInstance(res.json(), list)

    def test_missing_info_endpoint(self):
        token = self.login()
        res = self.client.post("/api/ai/missing-info", json={"title": "Login crash", "description": "App closes"}, headers=self.auth(token))
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIn("warnings", res.json())

    def test_ai_investigation_endpoint(self):
        token = self.login()
        # find an issue
        issues = self.client.get("/api/issues", headers=self.auth(token)).json()
        if not issues:
            self.skipTest("No issues in database")
        issue_id = issues[0]["id"]
        res = self.client.get(f"/api/issues/{issue_id}/ai-investigation", headers=self.auth(token))
        self.assertEqual(res.status_code, 200, res.text)
        data = res.json()
        self.assertIn("root_causes", data)
        self.assertIn("debugging_steps", data)

    def test_semantic_search(self):
        token = self.login()
        res = self.client.get("/api/issues", params={"search": "login", "semantic": True}, headers=self.auth(token))
        self.assertEqual(res.status_code, 200, res.text)
        self.assertIsInstance(res.json(), list)

    def test_full_lifecycle_transitions(self):
        token = self.login()
        # create a fresh issue
        projects = self.client.get("/api/projects", headers=self.auth(token)).json()
        if not projects:
            self.skipTest("No projects in database")
        project_id = projects[0]["id"]
        create = self.client.post("/api/issues", json={"title": "Lifecycle test issue", "description": "Test the full lifecycle flow", "project_id": project_id, "confirm_duplicate": True}, headers=self.auth(token))
        self.assertEqual(create.status_code, 200, create.text)
        issue_id = create.json()["id"]

        # Open -> In Progress
        r = self.client.put(f"/api/issues/{issue_id}", json={"status": "In Progress"}, headers=self.auth(token))
        self.assertEqual(r.status_code, 200, r.text)
        # In Progress -> In Review
        r = self.client.put(f"/api/issues/{issue_id}", json={"status": "In Review"}, headers=self.auth(token))
        self.assertEqual(r.status_code, 200, r.text)
        # In Review -> Resolved
        r = self.client.put(f"/api/issues/{issue_id}", json={"status": "Resolved"}, headers=self.auth(token))
        self.assertEqual(r.status_code, 200, r.text)
        # Resolved -> Verified (admin can verify)
        r = self.client.put(f"/api/issues/{issue_id}", json={"status": "Verified"}, headers=self.auth(token))
        self.assertEqual(r.status_code, 200, r.text)
        # Verified -> Closed
        r = self.client.put(f"/api/issues/{issue_id}", json={"status": "Closed"}, headers=self.auth(token))
        self.assertEqual(r.status_code, 200, r.text)
        # Closed -> Open (reopen)
        r = self.client.put(f"/api/issues/{issue_id}", json={"status": "Open"}, headers=self.auth(token))
        self.assertEqual(r.status_code, 200, r.text)

        # cleanup
        self.client.delete(f"/api/issues/{issue_id}", headers=self.auth(token))

    def test_invalid_transition_rejected(self):
        token = self.login()
        projects = self.client.get("/api/projects", headers=self.auth(token)).json()
        if not projects:
            self.skipTest("No projects in database")
        project_id = projects[0]["id"]
        create = self.client.post("/api/issues", json={"title": "Invalid transition test", "description": "Test", "project_id": project_id, "confirm_duplicate": True}, headers=self.auth(token))
        issue_id = create.json()["id"]
        # Open -> Closed is invalid
        r = self.client.put(f"/api/issues/{issue_id}", json={"status": "Closed"}, headers=self.auth(token))
        self.assertEqual(r.status_code, 422, r.text)
        self.client.delete(f"/api/issues/{issue_id}", headers=self.auth(token))

    def test_assignee_validation(self):
        token = self.login()
        projects = self.client.get("/api/projects", headers=self.auth(token)).json()
        if not projects:
            self.skipTest("No projects in database")
        project_id = projects[0]["id"]
        create = self.client.post("/api/issues", json={"title": "Assignee test", "description": "Test", "project_id": project_id, "confirm_duplicate": True}, headers=self.auth(token))
        issue_id = create.json()["id"]
        # invalid assignee id
        r = self.client.put(f"/api/issues/{issue_id}", json={"assigned_to": 999999}, headers=self.auth(token))
        self.assertEqual(r.status_code, 422, r.text)
        self.client.delete(f"/api/issues/{issue_id}", headers=self.auth(token))


if __name__ == "__main__":
    unittest.main()
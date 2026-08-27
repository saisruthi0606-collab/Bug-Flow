import unittest
from fastapi.testclient import TestClient

from app.main import app
from app.services.risk import risk_for_issue
from app.services.rag import is_bugflow_query


class Milestone3ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.email = "milestone3-admin@bugflow.com"
        self.password = "password123"
        self.client.post("/api/auth/register", json={"full_name": "Milestone Three Admin", "email": self.email, "password": self.password, "role": "Admin"})
        self.token = self.client.post("/api/auth/login", json={"email": self.email, "password": self.password}).json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        projects = self.client.get("/api/projects", headers=self.headers).json()
        if not projects:
            self.client.post("/api/projects", json={"project_name": "Milestone 3 Project", "description": "Test"}, headers=self.headers)
            projects = self.client.get("/api/projects", headers=self.headers).json()
        self.project_id = projects[0]["id"]

    def test_chat_is_authenticated_grounded_and_stores_history(self):
        issue = self.client.post("/api/issues", json={"title": "Login timeout", "description": "Login authentication times out for users", "project_id": self.project_id, "confirm_duplicate": True}, headers=self.headers)
        self.assertEqual(issue.status_code, 200, issue.text)
        denied = self.client.post("/api/chat/ask", json={"message": "login timeout"})
        self.assertEqual(denied.status_code, 401)
        response = self.client.post("/api/chat/ask", json={"message": "How was the login timeout handled?"}, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("answer", response.json())
        self.assertIn("sources", response.json())
        history = self.client.get("/api/chat/history", headers=self.headers)
        self.assertEqual(history.status_code, 200, history.text)
        self.assertTrue(history.json())

    def test_feedback_risk_and_analytics_metrics(self):
        feedback = self.client.post("/api/ai/feedback", json={"feedback_type": "helpful", "source": "chat", "message_ref": "test"}, headers=self.headers)
        self.assertEqual(feedback.status_code, 201, feedback.text)
        invalid = self.client.post("/api/ai/feedback", json={"feedback_type": "maybe", "source": "chat"}, headers=self.headers)
        self.assertEqual(invalid.status_code, 422)
        radar = self.client.get("/api/risk", headers=self.headers)
        self.assertEqual(radar.status_code, 200, radar.text)
        self.assertIn("issues", radar.json())
        analytics = self.client.get("/api/dashboard", headers=self.headers)
        self.assertEqual(analytics.status_code, 200, analytics.text)
        for key in ("closed_issues", "category_distribution", "developer_workload", "average_resolution_time_hours", "ai_feedback"):
            self.assertIn(key, analytics.json())


class RiskHeuristicTests(unittest.TestCase):
    def test_critical_old_duplicate_issue_is_high_risk(self):
        class Issue:
            id = 1; title = "Outage"; severity = "Critical"; priority = "High"; status = "Open"
            created_at = None; is_possible_duplicate = True; sprint = None; assigned_to = None
        class Query:
            def filter(self, *args): return self
            def count(self): return 0
        class DB:
            def query(self, *args): return Query()
        result = risk_for_issue(Issue(), DB())
        self.assertGreaterEqual(result["risk_score"], 50)
        self.assertEqual(result["risk_level"], "High")


class ChatIntentTests(unittest.TestCase):
    def test_general_conversation_bypasses_rag(self):
        for message in ("Hi", "Hello, who are you?", "What is RAG?", "Thank you"):
            self.assertFalse(is_bugflow_query(message))

    def test_bugflow_questions_use_rag(self):
        for message in ("What issues are related to login authentication?", "Show previous resolutions for login bugs.", "What happened to BUG-9?"):
            self.assertTrue(is_bugflow_query(message))

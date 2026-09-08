import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api.routes.risk import explain_risk
from app.main import app
from app.services.rag import deterministic_risk_answer
from app.services.risk import risk_for_issue


class QueryStub:
    def __init__(self, value=None, count_value=0):
        self.value = value
        self.count_value = count_value

    def filter(self, *args):
        return self

    def first(self):
        return self.value

    def count(self):
        return self.count_value


class RiskDatabaseStub:
    def __init__(self, issue, activity_count=0):
        self.issue = issue
        self.activity_count = activity_count

    def query(self, model):
        if getattr(model, "__name__", "") == "Activity":
            return QueryStub(count_value=self.activity_count)
        return QueryStub(value=self.issue)


def make_issue(status: str):
    return SimpleNamespace(
        id=24,
        title="Payment failure",
        severity="Critical",
        priority="High",
        status=status,
        created_at=datetime.now() - timedelta(days=14),
        updated_at=None,
        is_possible_duplicate=False,
        sprint=None,
        assigned_to=None,
        reporter=1,
    )


class ProRiskTests(unittest.TestCase):
    def test_closed_issue_has_lower_risk_than_equivalent_open_issue(self):
        open_result = risk_for_issue(make_issue("Open"), RiskDatabaseStub(make_issue("Open")))
        closed_result = risk_for_issue(make_issue("Closed"), RiskDatabaseStub(make_issue("Closed")))
        self.assertGreater(open_result["risk_score"], closed_result["risk_score"])
        self.assertIn("Issue is currently Open", open_result["reasons"])
        self.assertIn("reducing active risk", " ".join(closed_result["reasons"]))

    def test_reopened_issue_increases_risk_again(self):
        issue = make_issue("Open")
        result = risk_for_issue(issue, RiskDatabaseStub(issue, activity_count=1))
        self.assertEqual(result["reopen_count"], 1)
        self.assertIn("Previously reopened", result["reasons"])

    def test_risk_factors_are_structured_and_deterministic(self):
        result = risk_for_issue(make_issue("Open"), RiskDatabaseStub(make_issue("Open")))
        self.assertEqual(set(result["factors"]), {"severity", "priority", "status", "age", "reopen", "deadline", "workload", "duplicate"})
        self.assertGreater(result["factors"]["severity"], result["factors"]["priority"])

    def test_direct_risk_question_uses_current_data_without_gemini(self):
        issue = make_issue("Open")
        answer = deterministic_risk_answer("Why is BUG-24 high risk?", RiskDatabaseStub(issue), SimpleNamespace(id=1, role="Reporter"))
        self.assertIn("BUG-24 currently has a risk score", answer)
        self.assertIn("Recommended action", answer)

    def test_explain_risk_rejects_issue_outside_reporter_scope(self):
        issue = make_issue("Open")
        user = SimpleNamespace(id=2, role="Reporter")
        with self.assertRaises(Exception) as raised:
            explain_risk(issue.id, RiskDatabaseStub(issue), user)
        self.assertEqual(raised.exception.status_code, 403)


class ProAssistantUploadTests(unittest.TestCase):
    def test_image_assistant_requires_authentication(self):
        response = TestClient(app).post(
            "/api/chat/ask-image",
            files={"image": ("error.png", b"not-an-image", "image/png")},
        )
        self.assertEqual(response.status_code, 401)

    def test_image_assistant_rejects_unsupported_file_type_before_analysis(self):
        client = TestClient(app)
        registration = client.post(
            "/api/auth/register",
            json={"full_name": "PRO Upload Tester", "email": "pro-upload-tester@example.com", "password": "password123", "role": "Reporter"},
        )
        self.assertIn(registration.status_code, {200, 400})
        login = client.post("/api/auth/login", json={"email": "pro-upload-tester@example.com", "password": "password123"})
        self.assertEqual(login.status_code, 200, login.text)
        response = client.post(
            "/api/chat/ask-image",
            headers={"Authorization": f"Bearer {login.json()['access_token']}"},
            files={"image": ("error.txt", b"not-an-image", "text/plain")},
        )
        self.assertEqual(response.status_code, 422)

    def test_image_assistant_rejects_malformed_image_content(self):
        client = TestClient(app)
        login = client.post("/api/auth/login", json={"email": "pro-upload-tester@example.com", "password": "password123"})
        self.assertEqual(login.status_code, 200, login.text)
        response = client.post(
            "/api/chat/ask-image",
            headers={"Authorization": f"Bearer {login.json()['access_token']}"},
            files={"image": ("error.png", b"not-a-png", "image/png")},
        )
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
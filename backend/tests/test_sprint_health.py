import unittest
from datetime import date, timedelta
from types import SimpleNamespace

from fastapi import HTTPException

from app.api.routes.sprints import sprint_health
from app.services.sprint_health import calculate_sprint_health


class FakeQuery:
    def __init__(self, rows=None, count_value=0):
        self.rows = rows or []
        self.count_value = count_value

    def filter(self, *args):
        return self

    def all(self):
        return self.rows

    def first(self):
        return self.rows[0] if self.rows else None

    def count(self):
        return self.count_value


class HealthDb:
    def __init__(self, issues, reopened=0):
        self.issues = issues
        self.reopened = reopened

    def query(self, model):
        name = getattr(model, "__name__", "")
        if name == "Issue":
            return FakeQuery(self.issues)
        return FakeQuery(count_value=self.reopened)


def issue(issue_id, status="Open", severity="Low", assigned_to=None):
    return SimpleNamespace(id=issue_id, status=status, severity=severity, assigned_to=assigned_to)


def sprint(sprint_id=1, days=14):
    return SimpleNamespace(id=sprint_id, end_date=date(2026, 9, 7) + timedelta(days=days), project_id=1)


class SprintHealthCalculationTests(unittest.TestCase):
    today = date(2026, 9, 7)

    def test_healthy_completed_sprint(self):
        issues = [issue(1, "Closed"), issue(2, "Verified"), issue(3, "Resolved")]
        result = calculate_sprint_health(sprint(), HealthDb(issues), self.today)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["status"], "Healthy")
        self.assertEqual(result["remaining_issues"], 0)

    def test_critical_and_high_remaining_issues_reduce_health(self):
        issues = [issue(1, severity="Critical"), issue(2, severity="High"), issue(3, "Closed")]
        result = calculate_sprint_health(sprint(days=14), HealthDb(issues), self.today)
        self.assertEqual(result["critical_remaining"], 1)
        self.assertEqual(result["high_remaining"], 1)
        self.assertLess(result["score"], 80)

    def test_deadline_and_reopened_issue_reduce_health(self):
        issues = [issue(1, severity="High"), issue(2, "Closed")]
        result = calculate_sprint_health(sprint(days=2), HealthDb(issues, reopened=1), self.today)
        self.assertEqual(result["reopened_issues"], 1)
        self.assertEqual(result["days_remaining"], 2)
        self.assertTrue(any("deadline" in reason.lower() for reason in result["reasons"]))

    def test_score_is_bounded_and_empty_sprint_is_honest(self):
        result = calculate_sprint_health(sprint(), HealthDb([issue(1, severity="Critical")]), self.today)
        self.assertGreaterEqual(result["score"], 0)
        self.assertLessEqual(result["score"], 100)
        empty = calculate_sprint_health(sprint(), HealthDb([]), self.today)
        self.assertIsNone(empty["score"])
        self.assertEqual(empty["status"], "No Data")


class SprintHealthAuthorizationTests(unittest.TestCase):
    def test_other_project_health_is_forbidden(self):
        protected_sprint = sprint()
        project = SimpleNamespace(id=1, created_by=1)

        class Db:
            def query(self, model):
                return FakeQuery([protected_sprint] if getattr(model, "__name__", "") == "Sprint" else [project])

        with self.assertRaises(HTTPException) as raised:
            sprint_health(protected_sprint.id, Db(), SimpleNamespace(id=2, role="Reporter"))
        self.assertEqual(raised.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
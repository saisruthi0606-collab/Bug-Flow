import unittest

from app.api.routes.issues import VALID_TRANSITIONS
from app.services.duplicate_detection import find_duplicates


class DummyIssue:
    def __init__(self, id, project_id, title, description, embedding=None):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.embedding = embedding


class Milestone2RegressionTests(unittest.TestCase):
    def test_duplicate_results_are_capped_at_top_five(self):
        issues = [
            DummyIssue(1, 1, "Login page error", "Users cannot log in after password reset", None),
            DummyIssue(2, 1, "Sign in flow failing", "Users cannot sign in after reset", None),
            DummyIssue(3, 1, "Authentication broken", "Password reset login fails", None),
            DummyIssue(4, 1, "Access token expired", "Users are getting invalid token after sign in", None),
            DummyIssue(5, 1, "Session login bug", "Login tilts after resetting session", None),
            DummyIssue(6, 1, "Checkout issue", "The checkout page is freezing", None),
            DummyIssue(7, 1, "Profile page glitch", "Profile images are not aligned", None),
            DummyIssue(8, 1, "Data sync problem", "Records are not updating correctly", None),
            DummyIssue(9, 1, "Reset password bug", "Password issue occurs when resetting account", None),
            DummyIssue(10, 1, "UI display break", "The button is invisible after login", None),
        ]

        candidates, _ = find_duplicates(issues, "User login fails after password reset", "Users cannot login after reset", 1, threshold=0.15)

        self.assertLessEqual(len(candidates), 5)
        self.assertTrue(all(candidate["similarity"] >= 15 for candidate in candidates))

    def test_kanban_status_transitions_support_drag_and_drop(self):
        self.assertIn("In Progress", VALID_TRANSITIONS["Open"])
        self.assertIn("Resolved", VALID_TRANSITIONS["In Progress"])
        self.assertIn("Open", VALID_TRANSITIONS["Resolved"])


if __name__ == "__main__":
    unittest.main()

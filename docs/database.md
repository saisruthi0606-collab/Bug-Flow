# BugFlow Database

BugFlow uses SQLite through SQLAlchemy. The database is created additively by the application bootstrap and can be upgraded with Alembic. Existing data is preserved.

## Tables and relationships

* `users` stores accounts, roles, active state, preferences, and login/profile metadata.
* `projects` belongs to a creating user through `created_by`.
* `issues` belongs to a project, reporter, optional assignee, optional sprint, and optional duplicate issue.
* `sprints` belongs to a project and creator; issues reference a sprint through `sprint_id`.
* `comments`, `attachments`, and `activities` reference an issue and the user who authored, uploaded, or performed the action.
* `notifications` belongs to a user and optionally references an issue.
* `chat_messages` and `ai_feedback` belong to a user; chat records may store retrieved issue IDs.
* `ai_recommendations` and `impact_prediction_records` persist one analysis result per issue.

## Important indexes

Primary keys and unique user email/storage filename indexes are defined on the models. Milestone 4 adds composite indexes for `issues(project_id, status)`, `issues(assigned_to, status)`, `issues(sprint_id, status)`, and issue creation time. Timeline indexes cover `comments(issue_id, created_at)` and `activities(issue_id, created_at)`. Notification inbox reads use `notifications(user_id, is_read, created_at)`. The impact predictor uses a unique issue index.

The most common path is `project -> issues -> optional sprint`, with collaboration and notifications joined by `issue_id`. AI and chat persistence remains linked to the authenticated user and issue IDs rather than storing credentials or provider secrets.
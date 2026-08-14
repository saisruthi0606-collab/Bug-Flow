from random import randint


def get_ai_suggestions(description: str) -> dict:
    text = description.lower(); base = description.strip() or "The issue description is missing important details."
    category = "Security" if any(word in text for word in ["auth", "token", "password", "permission"]) else "Performance" if any(word in text for word in ["slow", "timeout", "load", "performance"]) else "UI" if any(word in text for word in ["screen", "button", "page", "display"]) else "Backend"
    severity = "Critical" if any(word in text for word in ["crash", "data loss", "security", "outage"]) else "High" if any(word in text for word in ["fail", "cannot", "blocked"]) else "Medium"
    priority = "High" if severity in {"Critical", "High"} else "Medium"
    root = "The report indicates an unhandled validation or state-management path." if category != "Performance" else "The report indicates an inefficient operation under load."
    resolution = "Add focused validation, error handling, and regression coverage for the affected path." if category != "Performance" else "Profile the affected operation, remove unnecessary work, and add performance regression coverage."
    confidence = 92 if len(base) > 60 else 76
    title = " ".join(word for word in base.split()[:8])
    if len(title) > 72:
        title = title[:69].rstrip() + "..."
    if not title:
        title = "Issue investigation"
    analysis = (
        f"Detected a {category.lower()} issue with {severity.lower()} impact. "
        f"The likely root cause is that {root.lower()} The suggested path is to {resolution.lower()} "
        f"Confidence is {confidence}% based on the language and urgency in the report."
    )
    return {
        "title": title,
        "enhanced_description": f"{base[0].upper() + base[1:]} Include reproducible steps, expected behavior, and observed behavior.",
        "severity": severity,
        "priority": priority,
        "category": category,
        "component": category,
        "root_cause": root,
        "resolution": resolution,
        "test_cases": "Verify the reported path and relevant error and edge-case behavior.",
        "estimated_time": "1-3 days",
        "confidence": f"{confidence}%",
        "confidence_score": confidence,
        "reasoning": f"Classification is based on issue language indicating {category.lower()} impact and {severity.lower()} user risk.",
        "analysis": analysis,
    }


def detect_missing_information(title: str, description: str) -> list[dict]:
    """Detect missing information in a bug report and return warnings."""
    text = (description or "").lower()
    title_text = (title or "").lower()
    warnings = []

    sections = [
        ("reproducible steps", ["steps to reproduce", "reproduce", "reproducible", "steps:", "1.", "2."]),
        ("expected behavior", ["expected", "should happen", "should work", "expected behavior"]),
        ("observed/actual behavior", ["actual", "observed", "instead", "what happens", "actual behavior"]),
        ("environment", ["environment", "os", "operating system", "windows", "macos", "linux", "browser", "version"]),
        ("browser/device", ["browser", "chrome", "firefox", "safari", "edge", "mobile", "device", "android", "ios"]),
        ("application/version", ["version", "v1.", "v2.", "release", "build"]),
        ("error message/logs", ["error", "exception", "stack trace", "log", "traceback", "failed"]),
    ]

    for label, keywords in sections:
        if not any(keyword in text or keyword in title_text for keyword in keywords):
            warnings.append({
                "field": label,
                "message": f"Missing information: {label.capitalize()} is not provided.",
            })

    return warnings


def generate_debugging_suggestions(issue, comment_texts: list[str]) -> dict:
    """Generate AI debugging/investigation suggestions based on real issue data."""
    title = issue.title or ""
    description = issue.description or ""
    combined = f"{title}. {description} " + " ".join(comment_texts)
    text = combined.lower()

    category = "Security" if any(word in text for word in ["auth", "token", "password", "permission", "login", "session"]) else "Performance" if any(word in text for word in ["slow", "timeout", "load", "performance", "lag"]) else "UI" if any(word in text for word in ["screen", "button", "page", "display", "render", "layout"]) else "Backend"

    # Root cause candidates based on keywords
    root_causes = []
    if any(word in text for word in ["crash", "freeze", "hang", "outage"]):
        root_causes.append("Unhandled exception or resource exhaustion causing the application to crash or hang.")
    if any(word in text for word in ["login", "auth", "token", "session", "password"]):
        root_causes.append("Authentication or session state handling may be failing (token expiry, invalid credentials, or session storage).")
    if any(word in text for word in ["slow", "timeout", "load", "performance"]):
        root_causes.append("Inefficient query, blocking operation, or excessive work on the critical path under load.")
    if any(word in text for word in ["button", "click", "screen", "display", "render"]):
        root_causes.append("UI state or event-handling logic may not be updating correctly (stale state or missing re-render).")
    if any(word in text for word in ["data", "save", "update", "sync", "database"]):
        root_causes.append("Data persistence or synchronization issue (validation, transaction, or race condition).")
    if not root_causes:
        root_causes.append("The report is too general to pinpoint a single root cause; reproduce the issue and capture logs.")

    # Debugging steps
    debugging_steps = [
        "Reproduce the issue in a clean environment and capture the exact steps.",
        "Check application logs and error output for the affected operation.",
        "Inspect the relevant code path and add targeted logging around the failure point.",
        "Verify inputs and state at the point of failure (validation, null/undefined handling).",
        "Test the fix in isolation and add a regression test to prevent recurrence.",
    ]

    # Relevant modules/components
    modules = []
    if category == "Security":
        modules = ["Authentication service", "Session/token management", "Authorization middleware"]
    elif category == "Performance":
        modules = ["Query layer / data access", "Request handling pipeline", "Caching layer"]
    elif category == "UI":
        modules = ["Frontend component", "State management", "Rendering/event handlers"]
    else:
        modules = ["API endpoint", "Business logic layer", "Data validation"]

    # Fix direction
    fix_direction = (
        "Add defensive validation and error handling around the affected path, "
        "then verify with regression coverage."
    )

    # Recommended next action
    next_action = (
        "Assign the issue to a developer, reproduce the failure, and capture logs "
        "before applying a targeted fix."
    )

    return {
        "category": category,
        "root_causes": root_causes,
        "debugging_steps": debugging_steps,
        "modules": modules,
        "fix_direction": fix_direction,
        "next_action": next_action,
        "disclaimer": "These are AI-generated suggestions based on the issue description and comments. They are not guaranteed facts and should be verified by a developer.",
    }
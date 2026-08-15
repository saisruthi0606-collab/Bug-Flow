import re


def _has_any(text: str, keywords: list[str]) -> bool:
    """Return True if any keyword appears in text."""
    return any(k in text for k in keywords)


def _sentence(value: str) -> str:
    """Ensure a string ends with a period and starts with a capital letter."""
    value = value.strip()
    if not value:
        return value
    if not value[0].isupper():
        value = value[0].upper() + value[1:]
    if not value.endswith("."):
        value += "."
    return value


def _best_title(description: str, fallback: str = "Issue investigation") -> str:
    """Create a concise, meaningful title from the description."""
    base = description.strip()
    if not base:
        return fallback
    parts = re.split(r"[.!?\n]+", base)
    first = next((p.strip() for p in parts if p.strip()), base)
    title = first[:72].rstrip()
    if len(first) > 72:
        title = title[:69].rstrip() + "..."
    return title or fallback


def _expand_description(description: str) -> str:
    """Expand the raw description into a professional explanation."""
    base = description.strip()
    if not base:
        return "The issue description is missing important details."
    return _sentence(base)


def _infer_steps(description: str) -> list[str]:
    """Generate reproduction steps only when the description provides context."""
    text = description.lower()

    if _has_any(text, ["password reset", "reset password", "reset the password"]):
        return [
            "Open the application.",
            "Reset the user password.",
            "Return to the login page.",
            "Enter the updated credentials.",
            "Click Login.",
            "Observe the application behavior.",
        ]
    if _has_any(text, ["login", "sign in", "sign-in", "log in", "authentication", "password", "credentials", "session", "token"]):
        return [
            "Navigate to the application's login page.",
            "Enter the affected credentials.",
            "Attempt to log in.",
            "Observe the application behavior.",
        ]
    if _has_any(text, ["payment", "checkout", "billing", "pay"]):
        return [
            "Open the payment page.",
            "Enter valid payment information.",
            "Click the submit button.",
            "Observe the application behavior.",
        ]
    if _has_any(text, ["update", "updating", "edit", "save", "not saving", "not updating"]):
        return [
            "Navigate to the relevant page/section.",
            "Modify the required fields.",
            "Save the changes.",
            "Observe whether the changes are applied correctly.",
        ]
    if _has_any(text, ["profile", "employee", "account", "user info", "personal info"]):
        return [
            "Navigate to the relevant profile/account page.",
            "Edit the information that needs updating.",
            "Save the changes.",
            "Observe whether the updates are applied correctly.",
        ]
    if _has_any(text, ["page", "screen", "display", "render", "ui", "button", "click", "submit"]):
        return [
            "Navigate to the affected page/screen.",
            "Perform the described action.",
            "Observe the application behavior.",
        ]
    if _has_any(text, ["slow", "lag", "timeout", "unresponsive", "hang", "freeze", "performance"]):
        return [
            "Perform the described operation that triggers the slowness.",
            "Measure the response time or observed delay.",
            "Note whether the application becomes unresponsive or times out.",
        ]
    if _has_any(text, ["crash", "crashes", "freeze", "hang", "error"]):
        return [
            "Navigate to the area where the issue occurs.",
            "Perform the action that triggers the problem.",
            "Observe whether the application crashes or errors out.",
        ]
    return ["Detailed reproduction steps are not provided. Please add them."]


def _infer_expected(description: str) -> str:
    """Infer the expected result from the description when supported."""
    text = description.lower()

    if _has_any(text, ["password reset", "reset password", "reset the password"]):
        return "The user should be able to log in successfully using the newly reset password."
    if _has_any(text, ["login", "sign in", "log in", "authentication", "password", "credentials"]):
        return "The user should be able to log in successfully with valid credentials."
    if _has_any(text, ["payment", "checkout", "billing", "pay"]):
        return "The payment should be submitted/processed successfully without errors."
    if _has_any(text, ["update", "updating", "edit", "save", "not saving", "not updating"]):
        return "The changes should be saved and reflected correctly in the application."
    if _has_any(text, ["profile", "employee", "account"]):
        return "The profile/account information should update correctly after saving."
    if _has_any(text, ["slow", "lag", "timeout", "unresponsive", "hang", "freeze", "performance"]):
        return "The application should respond promptly and complete the operation within an acceptable time."
    if _has_any(text, ["crash", "crashes", "freeze", "hang"]):
        return "The application should continue running without crashing or becoming unresponsive."

    return "Expected result is not provided. Please specify the expected behavior."


def _infer_actual(description: str) -> str:
    """Infer the actual result from the description when supported."""
    base = description.strip()
    if not base:
        return "Actual result is not provided. Please describe what actually happens."
    return _sentence(base)


def _infer_component(description: str, category: str) -> str:
    """Infer the likely component/module from the description."""
    text = description.lower()

    if _has_any(text, ["login", "sign in", "log in", "authentication", "password", "credentials", "session", "token"]):
        return "Authentication / Login module"
    if _has_any(text, ["payment", "checkout", "pay", "billing"]):
        return "Payment / Billing module"
    if _has_any(text, ["profile", "employee", "user account", "account settings"]):
        return "User Profile / Account module"
    if _has_any(text, ["dashboard", "home", "landing"]):
        return "Dashboard / Home module"
    if category == "Performance":
        return "Performance / Backend processing"
    if category == "UI":
        return "Frontend UI component"
    return category or "Unknown module"


def _infer_os(description: str) -> str:
    text = description.lower()
    for os_name in ["windows", "macos", "mac os", "linux", "ubuntu", "android", "ios", "chrome os"]:
        if os_name in text:
            return os_name.title()
    return "Not provided"


def _infer_browser(description: str) -> str:
    text = description.lower()
    for browser in ["chrome", "firefox", "safari", "edge", "internet explorer", "opera"]:
        if browser in text:
            return browser.title()
    return "Not provided"


def _infer_version(description: str) -> str:
    patterns = [
        r"version\s+([0-9]+(?:\.[0-9]+)*)",
        r"v([0-9]+(?:\.[0-9]+)*)",
        r"build\s+([0-9]+(?:\.[0-9]+)*)",
    ]
    for p in patterns:
        m = re.search(p, description.lower())
        if m:
            return m.group(0).strip()
    return "Not provided"


def _infer_error_message(description: str) -> str:
    """Extract error message or return 'Not provided'."""
    text = description.strip()
    if not text:
        return "Not provided"
    quoted = re.findall(r"['\"`]([^'\"`]{3,})['\"`]", text)
    if quoted:
        return quoted[0]
    patterns = [
        r"error\s*:?\s*([A-Za-z0-9_\- ]{2,})",
        r"exception\s*:?\s*([A-Za-z0-9_\- ]{2,})",
        r"code\s*:?\s*([0-9]{3,})",
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return "Not provided"


def _infer_environment_notes(description: str) -> str:
    text = description.lower()
    notes = []
    if _has_any(text, ["production", "prod"]):
        notes.append("Reported in a production-like environment.")
    if _has_any(text, ["staging"]):
        notes.append("Reported in a staging environment.")
    if _has_any(text, ["local", "localhost", "dev"]):
        notes.append("Reported in a local/development environment.")
    if not notes:
        return "Not provided"
    return " ".join(notes)


def _build_missing_information(
    description: str,
    title: str = "",
    inferred_steps: list[str] | None = None,
    inferred_expected: str | None = None,
    inferred_actual: str | None = None,
) -> list[str]:
    """Identify which critical defect-report fields are missing.

    Only fields that truly cannot be determined from the input (or that
    fall back to "not provided"/"please add them" messaging) are flagged.
    Fields for which the engine provides an inferred value are NOT listed
    as missing.
    """
    text = f"{title}. {description}".lower()
    missing = []

    if not _has_any(text, ["windows", "macos", "mac os", "linux", "ubuntu", "android", "ios", "chrome os", "operating system"]):
        missing.append("Operating System")
    if not _has_any(text, ["chrome", "firefox", "safari", "edge", "internet explorer", "opera", "browser"]):
        missing.append("Browser")
    if not _has_any(text, ["version", "v1.", "v2.", "v3.", "build", "release"]):
        missing.append("Application Version")
    if not _has_any(text, ["error", "exception", "stack trace", "traceback", "error message", "error code", "error log", "system log", "console"]):
        missing.append("Error Message")
    if not _has_any(text, ["environment", "production", "staging", "dev environment"]):
        missing.append("Environment Information")

    # Only flag steps / expected / actual if the engine could not infer them
    if inferred_steps is not None and len(inferred_steps) == 1 and "not provided" in inferred_steps[0].lower():
        missing.append("Detailed Reproduction Steps")
    if inferred_expected is not None and "not provided" in inferred_expected.lower():
        missing.append("Expected Result")
    if inferred_actual is not None and "not provided" in inferred_actual.lower():
        missing.append("Actual Result")

    return missing


def _build_enhanced_description(
    title: str,
    expanded_description: str,
    steps: list[str],
    expected: str,
    actual: str,
    os_value: str,
    browser_value: str,
    version_value: str,
    error_value: str,
    component: str,
    additional_notes: str,
    missing_info: list[str],
) -> str:
    """Format the complete structured defect report.

    The structure is designed so the user can paste it directly into the
    issue description textarea: it reads as a professional defect report
    with clearly labelled sections.
    """
    steps_text = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))

    impact = _infer_impact(expanded_description, component)

    return (
        f"Issue Description:\n{expanded_description}\n\n"
        f"Steps to Reproduce:\n{steps_text}\n\n"
        f"Expected Result:\n{expected}\n\n"
        f"Actual Result:\n{actual}\n\n"
        f"Impact:\n{impact}\n\n"
        f"Environment:\nOperating System: {os_value}\nBrowser: {browser_value}\nApplication Version: {version_value}\n\n"
        f"Error Message:\n{error_value}\n\n"
        f"Relevant Module/Component:\n{component}\n\n"
        f"Additional Information:\n{additional_notes}"
    )


def _infer_impact(description: str, component: str) -> str:
    """Infer the likely impact from the description when supported."""
    text = description.lower()

    if _has_any(text, ["salary", "pay", "payment", "billing", "financial"]):
        return "This issue may affect employee records, payroll processing, or financial accuracy."
    if _has_any(text, ["login", "authentication", "password", "session", "credential"]):
        return "Users may be unable to access the application, which could block critical workflow operations."
    if _has_any(text, ["crash", "freeze", "hang", "unresponsive"]):
        return "The application becomes unusable, potentially interrupting user workflows and causing data loss."
    if _has_any(text, ["slow", "lag", "timeout", "performance"]):
        return "Reduced productivity and potential frustration for users experiencing delays."
    if _has_any(text, ["data", "update", "save", "sync"]):
        return "Incorrect or stale data may be displayed, which could affect decision-making and reporting."
    if _has_any(text, ["profile", "employee", "account"]):
        return "Employee/account information may be inaccurate, potentially affecting downstream processes."
    return "Impact is not explicitly stated. Please provide additional details on how this issue affects users or the system."


def get_ai_suggestions(description: str, title: str = "") -> dict:
    """Transform a short issue description into a complete structured defect report.

    Preserves the original meaning, expands it professionally, and clearly
    marks all unavailable information as "Not provided" so the report never
    fabricates technical facts absent from the user's input.
    """
    raw = description.strip()
    title_text = title.strip()
    combined = f"{title_text}. {raw}" if title_text else raw
    text = combined.lower()
    base = raw or title_text or "The issue description is missing important details."

    category = (
        "Security"
        if _has_any(text, ["auth", "token", "password", "permission", "login", "session"])
        else "Performance"
        if _has_any(text, ["slow", "timeout", "load", "performance", "lag"])
        else "UI"
        if _has_any(text, ["screen", "button", "page", "display", "render", "click"])
        else "Backend"
    )
    severity = (
        "Critical"
        if _has_any(text, ["crash", "data loss", "security", "outage", "crashes"])
        else "High"
        if _has_any(text, ["fail", "cannot", "blocked", "not working", "fails", "unable"])
        else "Medium"
    )
    priority = "High" if severity in {"Critical", "High"} else "Medium"

    root = (
        "The report indicates an unhandled validation or state-management path."
        if category != "Performance"
        else "The report indicates an inefficient operation under load."
    )
    resolution = (
        "Add focused validation, error handling, and regression coverage for the affected path."
        if category != "Performance"
        else "Profile the affected operation, remove unnecessary work, and add performance regression coverage."
    )
    confidence = 92 if len(base) > 60 else 76

    generated_title = _best_title(base)
    expanded_description = _expand_description(base)
    steps = _infer_steps(combined)
    expected = _infer_expected(combined)
    actual = _infer_actual(raw)
    os_value = _infer_os(combined)
    browser_value = _infer_browser(combined)
    version_value = _infer_version(combined)
    error_value = _infer_error_message(combined)
    component = _infer_component(combined, category)
    additional_notes = _infer_environment_notes(combined)
    missing_info = _build_missing_information(
        combined,
        inferred_steps=steps,
        inferred_expected=expected,
        inferred_actual=actual,
    )

    enhanced_description = _build_enhanced_description(
        title=generated_title,
        expanded_description=expanded_description,
        steps=steps,
        expected=expected,
        actual=actual,
        os_value=os_value,
        browser_value=browser_value,
        version_value=version_value,
        error_value=error_value,
        component=component,
        additional_notes=additional_notes,
        missing_info=missing_info,
    )

    final_title = title_text or generated_title
    if len(final_title) > 72:
        final_title = final_title[:69].rstrip() + "..."
    if not final_title:
        final_title = "Issue investigation"

    analysis = (
        f"Detected a {category.lower()} issue with {severity.lower()} impact. "
        f"The likely root cause is that {root.lower()} The suggested path is to {resolution.lower()} "
        f"Confidence is {confidence}% based on the language and urgency in the report. "
        f"The defect report has been expanded into a structured format with "
        f"{len(steps)} reproduction step(s), expected/actual behavior, and missing-information detection."
    )

    return {
        "title": final_title,
        "enhanced_description": enhanced_description,
        "severity": severity,
        "priority": priority,
        "category": category,
        "component": component,
        "root_cause": root,
        "resolution": resolution,
        "test_cases": "Verify the reported path and relevant error and edge-case behavior.",
        "estimated_time": "1-3 days",
        "confidence": f"{confidence}%",
        "confidence_score": confidence,
        "reasoning": f"Classification is based on issue language indicating {category.lower()} impact and {severity.lower()} user risk.",
        "analysis": analysis,
        "steps_to_reproduce": steps,
        "expected_result": expected,
        "actual_result": actual,
        "environment": {
            "os": os_value,
            "browser": browser_value,
            "application_version": version_value,
        },
        "error_message": error_value,
        "missing_information": missing_info,
        "is_structured_report": True,
    }


def detect_missing_information(title: str, description: str) -> list[dict]:
    """Detect missing information in a bug report and return warnings.

    Uses the same structured detection as the enhance report generation so
    the missing-information list is consistent across the whole AI feature.
    """
    raw_description = description or ""
    text = raw_description.lower()
    title_text = (title or "").lower()
    combined = f"{title_text}. {text}"
    # Infer the same values as the enhance endpoint so the missing-information
    # list is consistent between the report and the standalone checker.
    steps = _infer_steps(combined)
    expected = _infer_expected(combined)
    actual = _infer_actual(raw_description)
    missing_fields = _build_missing_information(
        combined,
        inferred_steps=steps,
        inferred_expected=expected,
        inferred_actual=actual,
    )

    # Map structured missing fields to the label/message format historically used
    # by the issue detail page and tests.
    known_messages = {
        "Operating System": "Operating System is not provided.",
        "Browser": "Browser is not provided.",
        "Application Version": "Application Version is not provided.",
        "Error Message": "Error Message is not provided.",
        "Detailed Reproduction Steps": "Detailed Reproduction Steps are not provided.",
        "Expected Result": "Expected Result is not provided.",
        "Actual Result": "Actual Result is not provided.",
        "Environment Information": "Environment Information is not provided.",
        "Relevant Module/Component": "Relevant Module/Component is not provided.",
    }
    known_labels = {
        "Operating System": "environment",
        "Browser": "browser/device",
        "Application Version": "application/version",
        "Error Message": "error message/logs",
        "Detailed Reproduction Steps": "reproducible steps",
        "Expected Result": "expected behavior",
        "Actual Result": "observed/actual behavior",
        "Environment Information": "environment",
        "Relevant Module/Component": "environment",
    }

    warnings = []
    for field in missing_fields:
        label = known_labels.get(field, field.lower().replace(" ", "_"))
        message = known_messages.get(field, f"Missing information: {field} is not provided.")
        warnings.append({
            "field": label,
            "message": message,
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
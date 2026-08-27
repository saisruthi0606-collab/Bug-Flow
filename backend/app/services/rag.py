"""Grounded BugFlow retrieval and optional Gemini generation for chat."""
import json
import re

from sqlalchemy.orm import Session

try:
    from google import genai
except ImportError:  # Keep retrieval and the rest of BugFlow available without the optional SDK.
    genai = None

from ..core.config import settings
from ..models.collaboration import AIRecommendation, Activity, Comment
from ..models.issue import Issue
from ..models.user import User
from .duplicate_detection import create_embedding, deserialize_embedding, similarity


BUGFLOW_INTENT_TERMS = {
    "issue", "issues", "bug", "bugs", "defect", "defects", "project", "projects", "sprint", "sprints",
    "severity", "critical", "risk", "resolution", "resolved", "verified", "closed", "duplicate", "duplicates",
    "history", "analytics", "dashboard", "workload", "assigned", "authentication", "login",
}


def is_bugflow_query(message: str) -> bool:
    """Classify only clearly BugFlow-specific questions as retrieval requests."""
    lowered = message.lower()
    if re.search(r"\bbug[- ]?\d+\b", lowered):
        return True
    terms = set(re.findall(r"[a-z0-9]+", lowered))
    return bool(terms & BUGFLOW_INTENT_TERMS)


def can_view(issue: Issue, user: User) -> bool:
    if user.role in {"Admin", "Project Manager"}:
        return True
    if user.role == "Reporter":
        return issue.reporter == user.id
    if user.role == "Developer":
        return issue.assigned_to == user.id or issue.reporter == user.id
    if user.role == "QA Tester":
        return issue.status in {"In Review", "Resolved"} or issue.reporter == user.id or issue.assigned_to == user.id
    return False


def _document(issue: Issue, db: Session) -> tuple[str, dict]:
    comments = db.query(Comment).filter(Comment.issue_id == issue.id).order_by(Comment.created_at.desc()).limit(3).all()
    activities = db.query(Activity).filter(Activity.issue_id == issue.id).order_by(Activity.created_at.desc()).limit(3).all()
    recommendation = db.query(AIRecommendation).filter(AIRecommendation.issue_id == issue.id).first()
    resolution = recommendation.suggested_resolution if recommendation else None
    root_cause = recommendation.root_cause if recommendation else None
    text = "\n".join(filter(None, [
        f"Issue #{issue.id}: {issue.title}", issue.description or "", f"Category: {issue.category or 'Unspecified'}",
        f"Severity: {issue.severity}; Priority: {issue.priority}; Status: {issue.status}",
        f"Root cause suggestion: {root_cause}" if root_cause else "",
        f"Resolution suggestion: {resolution}" if resolution else "",
        "Comments: " + " | ".join(c.body for c in comments) if comments else "",
        "Activity: " + " | ".join(f"{a.action}: {a.details or ''}" for a in activities) if activities else "",
    ]))
    return text, {"issue_id": issue.id, "title": issue.title, "status": issue.status, "root_cause": root_cause, "previous_resolution": resolution, "comments": [c.body for c in comments]}


def retrieve(message: str, db: Session, user: User, limit: int = 6) -> list[dict]:
    query_embedding = create_embedding(message)
    ranked: list[tuple[float, dict]] = []
    lexical: list[tuple[float, dict]] = []
    query_terms = {term for term in re.findall(r"[a-z0-9]+", message.lower()) if len(term) > 2 and term not in {"the", "how", "what", "which", "have", "this", "that", "issue", "issues", "previous"}}
    asks_history = any(term in message.lower() for term in ("resolved", "resolution", "previous", "historical", "similar"))
    for issue in db.query(Issue).all():
        if not can_view(issue, user):
            continue
        document, source = _document(issue, db)
        embedding = deserialize_embedding(issue.embedding) or create_embedding(document)
        score = similarity(query_embedding, embedding)
        document_terms = set(re.findall(r"[a-z0-9]+", document.lower()))
        lexical_score = len(query_terms & document_terms) / max(1, len(query_terms))
        if asks_history and issue.status in {"Resolved", "Verified", "Closed"}:
            lexical_score = max(lexical_score, 0.25)
        source["similarity"] = round(max(score, lexical_score) * 100, 1)
        source["context"] = document
        if lexical_score > 0:
            lexical.append((lexical_score, source))
        if score >= 0.18:
            ranked.append((score, source))
    selected = sorted(ranked, key=lambda row: row[0], reverse=True)
    seen = {source["issue_id"] for _, source in selected}
    for score, source in sorted(lexical, key=lambda row: row[0], reverse=True):
        if source["issue_id"] not in seen:
            selected.append((score, source))
            seen.add(source["issue_id"])
        if len(selected) >= limit:
            break
    return [item for _, item in selected[:limit]]


def answer(message: str, sources: list[dict]) -> str:
    if not sources:
        return "I could not find relevant BugFlow issues you are permitted to view. Try including an issue area, project detail, or error symptom."
    context = "\n\n".join(source["context"] for source in sources)
    prompt = f"""You are BugFlow's project assistant. Answer only from the supplied BugFlow context.
Do not invent project facts. Clearly distinguish retrieved facts from suggestions, cite issue numbers, state uncertainty, and never reveal secrets.

Question: {message}

BugFlow context:
{context}
"""
    if not settings.gemini_api_key or genai is None:
        cited = ", ".join(f"#{source['issue_id']} {source['title']}" for source in sources)
        return f"Gemini is not configured. Relevant retrieved BugFlow records: {cited}. Configure GEMINI_API_KEY for a generated grounded summary."
    return _generate(prompt)


def conversational_answer(message: str) -> str:
    """Answer general conversation without exposing or retrieving project records."""
    if not settings.gemini_api_key or genai is None:
        return "Gemini is not configured. Set GEMINI_API_KEY to enable conversational answers."
    prompt = f"""You are BugFlow Assistant. Respond naturally and helpfully to the user's general conversation.
Do not access, infer, or expose private BugFlow database records in this mode. If asked about BugFlow-specific records, explain that the user should ask a specific issue/project question.

User message: {message}
"""
    return _generate(prompt)


def _generate(prompt: str) -> str:
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
        return response.text or "The AI service returned no answer. Please try again."
    except Exception:
        return "AI service is temporarily unavailable. Please try again."


def source_payload(sources: list[dict]) -> list[dict]:
    return [{key: value for key, value in source.items() if key != "context"} for source in sources]

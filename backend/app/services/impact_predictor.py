"""Structured Gemini predictions for the likely impact of fixing an issue."""
import json
import re
import hashlib

from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

try:
    from google import genai
except ImportError:
    genai = None

from ..core.config import settings
from ..models.collaboration import AIRecommendation, Activity, Comment
from ..models.issue import Issue
from ..models.user import User
from .rag import retrieve


class ImpactPrediction(BaseModel):
    impact_level: str
    regression_risk: str
    affected_areas: list[str] = Field(min_length=1)
    expected_effects: list[str] = Field(min_length=1)
    possible_side_effects: list[str] = Field(min_length=1)
    recommended_testing: list[str] = Field(min_length=1)
    recommended_precautions: list[str] = Field(min_length=1)
    confidence: int | None = Field(default=None, ge=0, le=100)
    summary: str = Field(min_length=1)

    @field_validator("impact_level")
    @classmethod
    def valid_impact(cls, value: str) -> str:
        if value not in {"Low", "Medium", "High", "Critical"}:
            raise ValueError("Invalid impact level")
        return value

    @field_validator("regression_risk")
    @classmethod
    def valid_risk(cls, value: str) -> str:
        if value not in {"Low", "Medium", "High"}:
            raise ValueError("Invalid regression risk")
        return value


def _issue_context(issue: Issue, db: Session) -> str:
    comments = db.query(Comment).filter(Comment.issue_id == issue.id).order_by(Comment.created_at.desc()).limit(5).all()
    activities = db.query(Activity).filter(Activity.issue_id == issue.id).order_by(Activity.created_at.desc()).limit(5).all()
    recommendation = db.query(AIRecommendation).filter(AIRecommendation.issue_id == issue.id).first()
    return "\n".join(filter(None, [
        f"Issue #{issue.id}: {issue.title}",
        f"Description: {issue.description or 'Not provided'}",
        f"Status: {issue.status}; Severity: {issue.severity}; Priority: {issue.priority}; Category: {issue.category or 'Not provided'}",
        f"Project: {issue.project_name or 'Not provided'}; Sprint: {issue.sprint_name or 'Not provided'}",
        f"Assignee: {issue.assignee_name or 'Unassigned'}; Reporter: {issue.reporter_name or 'Not provided'}",
        f"Existing AI analysis: {recommendation.reasoning if recommendation else 'Not available'}",
        "Comments: " + " | ".join(comment.body for comment in comments) if comments else "",
        "Activity: " + " | ".join(f"{activity.action}: {activity.details or ''}" for activity in activities) if activities else "",
    ]))


def _parse_response(text: str) -> ImpactPrediction:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.IGNORECASE | re.DOTALL)
    if fenced:
        cleaned = fenced.group(1)
    return ImpactPrediction.model_validate(json.loads(cleaned))


def predictor_signature(issue: Issue, db: Session) -> str:
    comments = db.query(Comment).filter(Comment.issue_id == issue.id).order_by(Comment.created_at.asc()).all()
    activities = db.query(Activity).filter(Activity.issue_id == issue.id).order_by(Activity.created_at.asc()).all()
    source = {
        "title": issue.title, "description": issue.description, "status": issue.status,
        "priority": issue.priority, "severity": issue.severity, "category": issue.category,
        "assigned_to": issue.assigned_to, "project_id": issue.project_id, "sprint_id": issue.sprint_id,
        "comments": [(c.body, c.updated_at.isoformat()) for c in comments],
        "activities": [(a.action, a.details, a.created_at.isoformat()) for a in activities],
    }
    return hashlib.sha256(json.dumps(source, sort_keys=True, default=str).encode()).hexdigest()


def baseline_impact(issue: Issue, db: Session) -> ImpactPrediction:
    severity = issue.severity or "Unknown"
    priority = issue.priority or "Unknown"
    status = issue.status or "Unknown"
    score = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}.get(severity, 0)
    score += {"High": 2, "Medium": 1, "Low": 0}.get(priority, 0)
    impact = "Critical" if score >= 6 else "High" if score >= 4 else "Medium" if score >= 2 else "Low"
    risk = "High" if impact in {"Critical", "High"} else "Medium" if impact == "Medium" else "Low"
    insufficient = not issue.title.strip() or not (issue.description or '').strip()
    summary = ("Impact analysis is limited because insufficient issue information is available."
               if insufficient else f"{severity} severity and {priority} priority indicate {impact.lower()} fix impact.")
    return ImpactPrediction(
        impact_level=impact, regression_risk=risk, affected_areas=[issue.category or "Issue functionality"],
        expected_effects=["Fix the reported behavior"], possible_side_effects=["Related functionality may require regression testing"],
        recommended_testing=["Verify the reported scenario", "Run regression tests for related functionality"],
        recommended_precautions=["Review the change before closure"], confidence=None, summary=summary,
    )


def predict_impact(issue: Issue, db: Session, user: User) -> ImpactPrediction:
    if not settings.gemini_api_key or genai is None:
        raise RuntimeError("AI impact prediction is unavailable because Gemini is not configured.")
    historical = retrieve(f"fix impact and previous resolution for {issue.title} {issue.category or ''}", db, user, limit=5)
    historical_context = "\n\n".join(item["context"] for item in historical if item["issue_id"] != issue.id)
    prompt = f"""You are BugFlow's senior software-impact analyst. Predict the likely consequences of fixing the selected issue.
Use only the supplied issue and permitted historical BugFlow context. Do not invent facts; when details are missing, state an uncertainty in the report.
Return ONLY valid JSON matching this exact shape:
{{"impact_level":"Low|Medium|High|Critical","regression_risk":"Low|Medium|High","affected_areas":["..."],"expected_effects":["..."],"possible_side_effects":["..."],"recommended_testing":["..."],"recommended_precautions":["..."],"confidence":87,"summary":"..."}}
Use concise developer-friendly strings and a confidence integer from 0 to 100.

Selected issue:
{_issue_context(issue, db)}

Permitted related historical context:
{historical_context or 'No related historical issues found.'}
"""
    try:
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
        if not response.text:
            raise ValueError("Gemini returned an empty impact prediction.")
        return _parse_response(response.text)
    except RuntimeError:
        raise
    except Exception as exc:
        raise ValueError("Gemini returned an invalid impact prediction. Please try again.") from exc

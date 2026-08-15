from fastapi import APIRouter, Depends
from pydantic import BaseModel
from .ai_service import detect_missing_information, get_ai_suggestions
from ...db.database import get_db
from ...utils.auth import get_current_user
from ...models.user import User
from sqlalchemy.orm import Session

router = APIRouter()


class AiRequest(BaseModel):
    title: str | None = None
    description: str
    issue_id: int | None = None


class MissingInfoRequest(BaseModel):
    title: str
    description: str | None = None


class AiResponse(BaseModel):
    title: str | None = None
    enhanced_description: str
    severity: str
    priority: str
    category: str
    component: str
    root_cause: str
    resolution: str
    test_cases: str
    estimated_time: str
    confidence: str
    analysis: str | None = None
    steps_to_reproduce: list[str] = []
    expected_result: str = ""
    actual_result: str = ""
    environment: dict[str, str] = {}
    error_message: str = ""
    missing_information: list[str] = []
    is_structured_report: bool = False


@router.post('/enhance', response_model=AiResponse)
def enhance_description(request: AiRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = get_ai_suggestions(request.description, title=request.title or "")
    # log activity and generate notifications if tied to an issue
    if request.issue_id:
        try:
            from ...services.activity import log_activity
            log_activity(db, request.issue_id, current_user.id, 'AI Analysis Completed', 'AI generated analysis')
            log_activity(db, request.issue_id, current_user.id, 'AI Recommendation Generated', 'AI generated analysis')
        except Exception:
            pass
    return res


@router.post('/missing-info')
def missing_info(request: MissingInfoRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    warnings = detect_missing_information(request.title, request.description or "")
    return {"warnings": warnings}
from fastapi import APIRouter
from pydantic import BaseModel
from .ai_service import get_ai_suggestions

router = APIRouter()

class AiRequest(BaseModel):
    description: str

class AiResponse(BaseModel):
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

@router.post('/enhance', response_model=AiResponse)
def enhance_description(request: AiRequest):
    return get_ai_suggestions(request.description)

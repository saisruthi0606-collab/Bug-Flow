from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.milestone3 import AIFeedback
from ...models.user import User
from ...utils.auth import get_current_user

router = APIRouter()


class FeedbackCreate(BaseModel):
    feedback_type: str = Field(pattern="^(helpful|not_helpful)$")
    source: str = Field(pattern="^(chat|investigation|recommendation|analysis)$")
    message_ref: str | None = Field(default=None, max_length=255)


@router.post("/feedback", status_code=201)
def create_feedback(payload: FeedbackCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    feedback = AIFeedback(user_id=current_user.id, **payload.model_dump())
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return {"id": feedback.id, "feedback_type": feedback.feedback_type}

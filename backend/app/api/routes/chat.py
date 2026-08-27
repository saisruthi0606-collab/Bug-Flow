import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.milestone3 import ChatMessage
from ...models.user import User
from ...services.rag import answer, conversational_answer, is_bugflow_query, retrieve, source_payload
from ...utils.auth import get_current_user

router = APIRouter()


class ChatAsk(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)


@router.post("/ask")
def ask(payload: ChatAsk, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")
    try:
        sources = retrieve(message, db, current_user) if is_bugflow_query(message) else []
        response = answer(message, sources) if sources or is_bugflow_query(message) else conversational_answer(message)
        db_message = ChatMessage(user_id=current_user.id, conversation_id=payload.conversation_id, message=message, response=response, retrieved_issue_ids=json.dumps([source["issue_id"] for source in sources]))
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="AI service is temporarily unavailable. Please try again.")
    public_sources = source_payload(sources)
    return {"id": db_message.id, "answer": response, "sources": public_sources, "retrieved_issues": public_sources}


@router.get("/history")
def history(conversation_id: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id)
    if conversation_id:
        query = query.filter(ChatMessage.conversation_id == conversation_id)
    rows = query.order_by(ChatMessage.created_at.desc()).limit(30).all()
    return [{"id": row.id, "message": row.message, "response": row.response, "conversation_id": row.conversation_id, "created_at": row.created_at, "retrieved_issue_ids": json.loads(row.retrieved_issue_ids or "[]")} for row in rows]

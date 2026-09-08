import json
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from ...db.database import get_db
from ...models.milestone3 import ChatMessage
from ...models.user import User
from ...services.rag import answer, conversational_answer, describe_image, deterministic_bugflow_answer, evidence_payload, extract_project_id, is_bugflow_query, multimodal_answer, retrieve, source_payload
from ...utils.auth import get_current_user

router = APIRouter()


class ChatAsk(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=100)


MAX_IMAGE_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def has_image_signature(image_bytes: bytes, content_type: str) -> bool:
    signatures = {
        "image/png": image_bytes.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": image_bytes.startswith(b"\xff\xd8\xff"),
        "image/webp": image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP",
    }
    return signatures.get(content_type, False)


@router.post("/ask")
def ask(payload: ChatAsk, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")
    try:
        bugflow_query = is_bugflow_query(message)
        immediate = deterministic_bugflow_answer(message, db, current_user) if bugflow_query else None
        sources = [] if immediate else (retrieve(message, db, current_user, project_id=extract_project_id(message)) if bugflow_query else [])
        response = immediate or (answer(message, sources) if sources or bugflow_query else conversational_answer(message))
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
    return {"id": db_message.id, "answer": response, "sources": public_sources, "retrieved_issues": public_sources, "evidence": evidence_payload(sources) if bugflow_query else None}


@router.post("/ask-image")
async def ask_image(
    image: UploadFile = File(...),
    message: str = Form("Analyze this screenshot and identify any potential software defect.", max_length=4000),
    conversation_id: str | None = Form(None, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    suffix = Path(image.filename or "").suffix.lower()
    content_type = (image.content_type or "").lower()
    if suffix not in ALLOWED_IMAGE_EXTENSIONS or content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=422, detail="Only PNG, JPG/JPEG, and WEBP images are supported")
    image_bytes = await image.read(MAX_IMAGE_BYTES + 1)
    if len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="Image must be 5 MB or smaller")
    if not has_image_signature(image_bytes, content_type):
        raise HTTPException(status_code=422, detail="The uploaded file is not a valid image")
    question = message.strip() or "Analyze this screenshot and identify any potential software defect."
    try:
        image_description = describe_image(image_bytes, content_type)
        search_message = f"{question}\nVisible screenshot details: {image_description}" if image_description else question
        bugflow_query = is_bugflow_query(question)
        sources = retrieve(search_message, db, current_user) if bugflow_query else []
        response = multimodal_answer(question, image_bytes, content_type, sources)
        stored_message = f"[Image attached] {question}"
        db_message = ChatMessage(user_id=current_user.id, conversation_id=conversation_id, message=stored_message, response=response, retrieved_issue_ids=json.dumps([source["issue_id"] for source in sources]))
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="AI image analysis is temporarily unavailable. Please try again.")
    public_sources = source_payload(sources)
    return {"id": db_message.id, "answer": response, "sources": public_sources, "retrieved_issues": public_sources, "evidence": evidence_payload(sources) if bugflow_query else None}


@router.get("/history")
def history(conversation_id: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(ChatMessage).filter(ChatMessage.user_id == current_user.id)
    if conversation_id:
        query = query.filter(ChatMessage.conversation_id == conversation_id)
    rows = query.order_by(ChatMessage.created_at.desc()).limit(30).all()
    return [{"id": row.id, "message": row.message, "response": row.response, "conversation_id": row.conversation_id, "created_at": row.created_at, "retrieved_issue_ids": json.loads(row.retrieved_issue_ids or "[]")} for row in rows]

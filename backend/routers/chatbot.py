from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlmodel import Session

from database import get_db
from auth import get_current_user
from Models.chat import (
    ChatMessageIn, ChatResponse, ChatSessionOut, ChatMessageOut,
    db_create_session, db_get_session, db_get_user_sessions,
    db_save_message, db_get_session_messages, db_count_user_messages_today
)
from gemini_api import get_ai_response

router = APIRouter()

FREE_TIER_DAILY_LIMIT = 5

@router.post("/chat/session", response_model=ChatSessionOut, status_code=status.HTTP_201_CREATED)
def create_chat_session(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = db_create_session(db, user_id=current_user.id)
    return session

@router.get("/chat/sessions", response_model=List[ChatSessionOut], status_code=status.HTTP_200_OK)
def get_my_sessions(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return db_get_user_sessions(db, user_id=current_user.id)

@router.get("/chat/session/{session_id}/history", status_code=status.HTTP_200_OK)
def get_chat_history(session_id: int, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    session = db_get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
    return db_get_session_messages(db, session_id)

@router.post("/chat/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def send_message(body: ChatMessageIn, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.subscription_tier == 'free':
        count = db_count_user_messages_today(db, current_user.id)
        if count >= FREE_TIER_DAILY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Free tier limit reached ({FREE_TIER_DAILY_LIMIT} messages/day). Please upgrade to Premium!"
            )

    session = db_get_session(db, body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    history = db_get_session_messages(db, body.session_id)
    user_msg = db_save_message(db, body.session_id, sender='user', message=body.message)

    try:
        ai_reply_text = get_ai_response(history, body.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    bot_msg = db_save_message(db, body.session_id, sender='bot', message=ai_reply_text)
    return ChatResponse(
        user_message=ChatMessageOut(**user_msg.model_dump()),
        bot_reply=ChatMessageOut(**bot_msg.model_dump())
    )

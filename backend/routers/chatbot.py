from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from schemas.chat import ChatMessage_in, ChatResponse, ChatSession_out
from Models.chat import (
    db_create_session, db_get_session, db_get_user_sessions,
    db_save_message, db_get_session_messages, db_count_user_messages_today
)
from gemini_api import get_ai_response
from auth import get_current_user

router = APIRouter()

FREE_TIER_DAILY_LIMIT = 5

@router.post("/chat/session", response_model=ChatSession_out, status_code=status.HTTP_201_CREATED)
def create_chat_session(current_user: dict = Depends(get_current_user)):
    """Start a new chat session."""
    session = db_create_session(user_id=current_user['id'])
    return session

@router.get("/chat/sessions", response_model=List[ChatSession_out], status_code=status.HTTP_200_OK)
def get_my_sessions(current_user: dict = Depends(get_current_user)):
    """Get all past chat sessions for the current user."""
    sessions = db_get_user_sessions(user_id=current_user['id'])
    return sessions

@router.get("/chat/session/{session_id}/history", status_code=status.HTTP_200_OK)
def get_chat_history(session_id: int, current_user: dict = Depends(get_current_user)):
    """Get all messages from a specific session."""
    session = db_get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized to view this session")
    messages = db_get_session_messages(session_id)
    return messages

@router.post("/chat/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def send_message(body: ChatMessage_in, current_user: dict = Depends(get_current_user)):
    """Send a message to the AI vet chatbot and get a reply."""

    subscription = current_user.get('subscription_tier', 'free')
    if subscription == 'free':
        count = db_count_user_messages_today(current_user['id'])
        if count >= FREE_TIER_DAILY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Free tier limit reached ({FREE_TIER_DAILY_LIMIT} messages/day). Please upgrade to Premium for unlimited access!"
            )

    session = db_get_session(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="Not authorized")

    history = db_get_session_messages(body.session_id)

    user_msg = db_save_message(body.session_id, sender='user', message=body.message)

    try:
        ai_reply_text = get_ai_response(history, body.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    bot_msg = db_save_message(body.session_id, sender='bot', message=ai_reply_text)

    return ChatResponse(user_message=user_msg, bot_reply=bot_msg)

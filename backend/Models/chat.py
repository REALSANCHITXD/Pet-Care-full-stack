from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Session, select, func


# --- Table Models (DB) ---
class ChatSession(SQLModel, table=True):
    __tablename__ = "chat_sessions"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    started_at: Optional[datetime] = Field(default=None)

class ChatMessage(SQLModel, table=True):
    __tablename__ = "chat_messages"
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="chat_sessions.id")
    sender: str  # "user" or "bot"
    message: str
    sent_at: Optional[datetime] = Field(default=None)


# --- Response Schemas ---
class ChatMessageOut(SQLModel):
    id: int
    session_id: int
    sender: str
    message: str
    sent_at: Optional[datetime] = None

class ChatSessionOut(SQLModel):
    id: int
    user_id: int
    started_at: Optional[datetime] = None

class ChatMessageIn(SQLModel):
    session_id: int
    message: str

class ChatResponse(SQLModel):
    user_message: ChatMessageOut
    bot_reply: ChatMessageOut


# --- CRUD Functions ---
def db_create_session(session: Session, user_id: int) -> ChatSession:
    chat_session = ChatSession(user_id=user_id)
    session.add(chat_session)
    session.commit()
    session.refresh(chat_session)
    return chat_session

def db_get_session(session: Session, session_id: int):
    return session.get(ChatSession, session_id)

def db_get_user_sessions(session: Session, user_id: int):
    return session.exec(
        select(ChatSession).where(ChatSession.user_id == user_id).order_by(ChatSession.started_at.desc())
    ).all()

def db_save_message(session: Session, session_id: int, sender: str, message: str) -> ChatMessage:
    msg = ChatMessage(session_id=session_id, sender=sender, message=message)
    session.add(msg)
    session.commit()
    session.refresh(msg)
    return msg

def db_get_session_messages(session: Session, session_id: int):
    return session.exec(
        select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.sent_at.asc())
    ).all()

def db_count_user_messages_today(session: Session, user_id: int) -> int:
    from datetime import date
    today = date.today()
    result = session.exec(
        select(func.count(ChatMessage.id))
        .join(ChatSession, ChatMessage.session_id == ChatSession.id)
        .where(
            ChatSession.user_id == user_id,
            ChatMessage.sender == "user",
            func.date(ChatMessage.sent_at) == today
        )
    ).one()
    return result or 0

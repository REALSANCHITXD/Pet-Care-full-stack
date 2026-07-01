from pydantic import BaseModel
from typing import List
from datetime import datetime

class ChatMessage_in(BaseModel):
    session_id: int
    message: str

class ChatMessage_out(BaseModel):
    id: int
    session_id: int
    sender: str 
    message: str
    sent_at: datetime

class ChatSession_out(BaseModel):
    id: int
    user_id: int
    started_at: datetime

class ChatResponse(BaseModel):
    user_message: ChatMessage_out
    bot_reply: ChatMessage_out

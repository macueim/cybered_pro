# backend/app/schemas/forum.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class ForumReplyBase(BaseModel):
    content: str

class ForumReplyCreate(ForumReplyBase):
    pass

class ForumReplyResponse(ForumReplyBase):
    id: int
    topic_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    username: Optional[str] = None  # This can be populated from the user relationship

    class Config:
        from_attributes = True

class ForumTopicBase(BaseModel):
    title: str
    content: str
    course_id: Optional[int] = None  # Optional to allow general forum topics

class ForumTopicCreate(ForumTopicBase):
    pass

class ForumTopicResponse(ForumTopicBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: List[ForumReplyResponse] = []
    username: Optional[str] = None  # This can be populated from the user relationship
    reply_count: Optional[int] = None

    class Config:
        from_attributes = True
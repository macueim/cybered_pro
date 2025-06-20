# backend/app/schemas/lesson.py
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel

class LessonBase(BaseModel):
    title: str
    content: str
    order: Optional[int] = None
    estimated_time_minutes: Optional[int] = None

class LessonCreate(LessonBase):
    module_id: int

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = None
    estimated_time_minutes: Optional[int] = None
    is_published: Optional[bool] = None

class LessonResponse(LessonBase):
    id: int
    module_id: int
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # You can include additional fields from relationships if needed
    # e.g., attachments, comments, etc.

    class Config:
        from_attributes = True

# Alias for backward compatibility
Lesson = LessonResponse
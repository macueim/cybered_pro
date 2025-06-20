# backend/app/schemas/module.py
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel

class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order: Optional[int] = None

class ModuleCreate(ModuleBase):
    course_id: int

class ModuleUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    is_published: Optional[bool] = None

class ModuleResponse(ModuleBase):
    id: int
    course_id: int
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    # You could include relationships here if needed
    # lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True

# Alias for backward compatibility
Module = ModuleResponse
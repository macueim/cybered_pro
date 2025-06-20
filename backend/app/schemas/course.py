from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# Lesson schemas
class LessonBase(BaseModel):
    title: str
    content_type: str
    content: str
    order_index: int


class LessonCreate(LessonBase):
    pass


class LessonUpdate(LessonBase):
    title: Optional[str] = None
    content_type: Optional[str] = None
    content: Optional[str] = None
    order_index: Optional[int] = None


class LessonResponse(LessonBase):
    id: int
    module_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Previously from_attributes


# Module schemas
class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(ModuleBase):
    title: Optional[str] = None
    order_index: Optional[int] = None


class ModuleResponse(ModuleBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True  # Previously from_attributes


# Course schemas
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    certification_type: Optional[str] = None
    difficulty_level: str
    estimated_duration: Optional[int] = None
    is_published: bool = False


class CourseCreate(CourseBase):
    pass


class CourseUpdate(CourseBase):
    title: Optional[str] = None
    difficulty_level: Optional[str] = None
    is_published: Optional[bool] = None


class CourseResponse(CourseBase):
    id: int
    instructor_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    modules: List[ModuleResponse] = []

    class Config:
        from_attributes = True  # Previously from_attributes


# Full course details schema for nested display
class CourseDetailResponse(CourseResponse):
    modules: List[ModuleResponse] = []

    class Config:
        from_attributes = True  # Previously from_attributes
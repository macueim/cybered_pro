# backend/app/schemas/progress.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# Lesson Completion Schemas
class LessonCompletionBase(BaseModel):
    notes: Optional[str] = None
    completion_percentage: int = 100  # Default to 100% complete

class LessonCompletionCreate(LessonCompletionBase):
    pass

class LessonCompletionResponse(LessonCompletionBase):
    id: int
    user_id: int
    lesson_id: int
    completed_at: datetime

    class Config:
        from_attributes = True

# Module Progress Schema
class ModuleProgressItem(BaseModel):
    module_id: int
    module_title: str
    total_lessons: int
    completed_lessons: int
    completion_percentage: float

    class Config:
        from_attributes = True

# Course Progress Schemas
class CourseProgressResponse(BaseModel):
    course_id: int
    course_title: str
    total_modules: int
    total_lessons: int
    completed_lessons: int
    overall_completion_percentage: float
    module_progress: List[ModuleProgressItem]

    class Config:
        from_attributes = True

# Assessment Progress Schemas
class AssessmentResult(BaseModel):
    score: float
    max_score: float
    passed: bool
    attempt_number: int
    completed_at: datetime

    class Config:
        from_attributes = True

class UserAssessmentListResponse(BaseModel):
    id: int
    assessment_id: int
    assessment_title: str
    course_title: str
    latest_result: AssessmentResult
    all_attempts: int

    class Config:
        from_attributes = True
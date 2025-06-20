# backend/app/services/progress_service.py
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.course import Course, Module, Lesson
from app.models.progress import LessonCompletion, AssessmentAttempt
from app.schemas.progress import (
    CourseProgressResponse,
    ModuleProgressItem,
    LessonCompletionCreate,
    LessonCompletionResponse,
    UserAssessmentListResponse
)

def get_course_progress(db: Session, user_id: int, course_id: int) -> CourseProgressResponse:
    """
    Get a user's progress in a specific course
    """
    # Get course information
    course = db.query(Course).filter(Course.id == course_id).first()

    # Get all modules in the course
    modules = db.query(Module).filter(Module.course_id == course_id).all()

    # Get count of all lessons in the course
    total_lessons = db.query(func.count(Lesson.id)). \
                        join(Module, Module.id == Lesson.module_id). \
                        filter(Module.course_id == course_id).scalar() or 0

    # Get count of completed lessons by this user in this course
    completed_lessons = db.query(func.count(LessonCompletion.id)). \
                            join(Lesson, Lesson.id == LessonCompletion.lesson_id). \
                            join(Module, Module.id == Lesson.module_id). \
                            filter(
        Module.course_id == course_id,
        LessonCompletion.user_id == user_id
    ).scalar() or 0

    # Calculate overall completion percentage
    overall_completion_percentage = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0

    # Get module-specific progress
    module_progress = []
    for module in modules:
        # Count lessons in this module
        module_lessons = db.query(func.count(Lesson.id)). \
                             filter(Lesson.module_id == module.id).scalar() or 0

        # Count completed lessons in this module
        module_completed = db.query(func.count(LessonCompletion.id)). \
                               join(Lesson, Lesson.id == LessonCompletion.lesson_id). \
                               filter(
            Lesson.module_id == module.id,
            LessonCompletion.user_id == user_id
        ).scalar() or 0

        # Calculate module completion percentage
        module_completion = (module_completed / module_lessons * 100) if module_lessons > 0 else 0

        module_progress.append(ModuleProgressItem(
            module_id=module.id,
            module_title=module.title,
            total_lessons=module_lessons,
            completed_lessons=module_completed,
            completion_percentage=module_completion
        ))

    return CourseProgressResponse(
        course_id=course_id,
        course_title=course.title,
        total_modules=len(modules),
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        overall_completion_percentage=overall_completion_percentage,
        module_progress=module_progress
    )

def mark_lesson_complete(
        db: Session,
        user_id: int,
        lesson_id: int,
        completion_data: LessonCompletionCreate
) -> LessonCompletionResponse:
    """
    Mark a lesson as complete for a user
    """
    # Check if already completed
    existing = db.query(LessonCompletion).filter(
        LessonCompletion.user_id == user_id,
        LessonCompletion.lesson_id == lesson_id
    ).first()

    if existing:
        # Update existing completion record
        update_data = completion_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    # Create new completion record
    completion = LessonCompletion(
        user_id=user_id,
        lesson_id=lesson_id,
        **completion_data.dict()
    )
    db.add(completion)
    db.commit()
    db.refresh(completion)
    return completion

def get_user_assessment_results(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    Get a user's assessment results
    """
    # This function should be implemented based on your assessment model
    # Placeholder implementation
    return []
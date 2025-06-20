# backend/app/api/endpoints/progress.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.progress import (
    CourseProgressResponse,
    LessonCompletionCreate,
    LessonCompletionResponse,
    UserAssessmentListResponse
)
from app.services import progress_service, course_service, assessment_service

router = APIRouter()

@router.get("/courses/{course_id}", response_model=CourseProgressResponse)
def get_course_progress(
        *,
        db: Session = Depends(get_db),
        course_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user progress in a course.
    """
    # Verify course exists
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )

    # Verify user is enrolled in the course or is instructor/admin
    if current_user.role == "student":
        from app.services import enrollment_service
        enrollment = enrollment_service.get_by_user_and_course(
            db, user_id=current_user.id, course_id=course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=403,
                detail="You must be enrolled in this course to track progress",
            )

    progress = progress_service.get_course_progress(
        db, user_id=current_user.id, course_id=course_id
    )
    return progress

@router.post("/lessons/{lesson_id}", response_model=LessonCompletionResponse, status_code=status.HTTP_201_CREATED)
def mark_lesson_complete(
        *,
        db: Session = Depends(get_db),
        lesson_id: int,
        completion_in: LessonCompletionCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark lesson as complete.
    """
    # Verify lesson exists
    lesson = course_service.get_lesson(db, id=lesson_id)
    if not lesson:
        raise HTTPException(
            status_code=404,
            detail="The lesson with this ID does not exist in the system",
        )

    # Get module and course to verify enrollment
    module = course_service.get_module(db, id=lesson.module_id)

    # Verify user is enrolled in the course
    if current_user.role == "student":
        from app.services import enrollment_service
        enrollment = enrollment_service.get_by_user_and_course(
            db, user_id=current_user.id, course_id=module.course_id
        )
        if not enrollment:
            raise HTTPException(
                status_code=403,
                detail="You must be enrolled in this course to mark lessons complete",
            )

    completion = progress_service.mark_lesson_complete(
        db, user_id=current_user.id, lesson_id=lesson_id, completion_data=completion_in
    )
    return completion

@router.get("/assessments", response_model=List[UserAssessmentListResponse])
def get_user_assessment_results(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user assessment results.
    """
    results = assessment_service.get_user_assessment_results(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return results
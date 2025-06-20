# backend/app/api/endpoints/lessons.py
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services import lesson_service, module_service, course_service

router = APIRouter()

@router.get("/modules/{module_id}/lessons", response_model=List[schemas.Lesson])
def read_lessons(
        module_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve lessons for a module.
    """
    module = module_service.get(db=db, module_id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get the course to check permissions
    course = course_service.get(db=db, course_id=module.course_id)

    # Check permissions
    if current_user.role == "student" and not course.is_published:
        raise HTTPException(status_code=403, detail="Access forbidden")

    if (current_user.role == "instructor" and
            current_user.id != course.instructor_id):
        raise HTTPException(status_code=403, detail="Access forbidden")

    return lesson_service.get_multi_by_module(
        db=db, module_id=module_id, skip=skip, limit=limit
    )

@router.post("/lessons", response_model=schemas.Lesson)
def create_lesson(
        *,
        db: Session = Depends(deps.get_db),
        lesson_in: schemas.LessonCreate,
        current_user: models.User = Depends(deps.get_current_instructor),
) -> Any:
    """
    Create new lesson.
    """
    # Check if the module exists
    module = module_service.get(db=db, module_id=lesson_in.module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get the course to check permissions
    course = course_service.get(db=db, course_id=module.course_id)

    if current_user.role == "instructor" and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only add lessons to your own courses"
        )

    return lesson_service.create(db=db, obj_in=lesson_in)

@router.get("/lessons/{lesson_id}", response_model=schemas.Lesson)
def read_lesson(
        *,
        db: Session = Depends(deps.get_db),
        lesson_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get lesson by ID.
    """
    lesson = lesson_service.get(db=db, lesson_id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get the module and course to check permissions
    module = module_service.get(db=db, module_id=lesson.module_id)
    course = course_service.get(db=db, course_id=module.course_id)

    # Check permissions
    if current_user.role == "student" and not course.is_published:
        raise HTTPException(status_code=403, detail="Access forbidden")

    if (current_user.role == "instructor" and
            current_user.id != course.instructor_id):
        raise HTTPException(status_code=403, detail="Access forbidden")

    return lesson

@router.put("/lessons/{lesson_id}", response_model=schemas.Lesson)
def update_lesson(
        *,
        db: Session = Depends(deps.get_db),
        lesson_id: int,
        lesson_in: schemas.LessonUpdate,
        current_user: models.User = Depends(deps.get_current_instructor),
) -> Any:
    """
    Update a lesson.
    """
    lesson = lesson_service.get(db=db, lesson_id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get the module and course to check permissions
    module = module_service.get(db=db, module_id=lesson.module_id)
    course = course_service.get(db=db, course_id=module.course_id)

    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only update lessons in your own courses"
        )

    return lesson_service.update(db=db, db_obj=lesson, obj_in=lesson_in)

@router.delete("/lessons/{lesson_id}")
def delete_lesson(
        *,
        db: Session = Depends(deps.get_db),
        lesson_id: int,
        current_user: models.User = Depends(deps.get_current_instructor),
) -> Any:
    """
    Delete a lesson.
    """
    lesson = lesson_service.get(db=db, lesson_id=lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    # Get the module and course to check permissions
    module = module_service.get(db=db, module_id=lesson.module_id)
    course = course_service.get(db=db, course_id=module.course_id)

    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only delete lessons in your own courses"
        )

    return lesson_service.delete(db=db, lesson_id=lesson_id)
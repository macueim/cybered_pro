# backend/app/api/endpoints/courses.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_current_active_instructor, get_db
from app.models.user import User
from app.models.course import Course, Module, Lesson
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    ModuleCreate, ModuleResponse,
    LessonCreate, LessonResponse
)
from app.services import course_service

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
def read_courses(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve all courses.
    """
    courses = course_service.get_multi(db, skip=skip, limit=limit)
    return courses

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
        *,
        db: Session = Depends(get_db),
        course_in: CourseCreate,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Create new course. Instructor/Admin only.
    """
    course = course_service.create(db, obj_in=course_in, creator_id=current_user.id)
    return course

@router.get("/{course_id}", response_model=CourseResponse)
def read_course(
        *,
        db: Session = Depends(get_db),
        course_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get specific course by ID.
    """
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )
    return course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
        *,
        db: Session = Depends(get_db),
        course_id: int,
        course_in: CourseUpdate,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Update a course. Instructor/Admin only.
    """
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )

    # Ensure the instructor is the creator or an admin
    if course.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this course",
        )

    course = course_service.update(db, db_obj=course, obj_in=course_in)
    return course

@router.delete("/{course_id}", response_model=CourseResponse)
def delete_course(
        *,
        db: Session = Depends(get_db),
        course_id: int,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Delete a course. Instructor/Admin only.
    """
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )

    # Ensure the instructor is the creator or an admin
    if course.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this course",
        )

    course = course_service.delete(db, id=course_id)
    return course

@router.get("/{course_id}/modules", response_model=List[ModuleResponse])
def read_course_modules(
        *,
        db: Session = Depends(get_db),
        course_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all modules for a course.
    """
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )

    modules = course_service.get_course_modules(db, course_id=course_id)
    return modules

@router.post("/{course_id}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(
        *,
        db: Session = Depends(get_db),
        course_id: int,
        module_in: ModuleCreate,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Add a module to a course. Instructor/Admin only.
    """
    course = course_service.get(db, id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )

    # Ensure the instructor is the creator or an admin
    if course.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to add modules to this course",
        )

    module = course_service.create_module(
        db, obj_in=module_in, course_id=course_id
    )
    return module

@router.get("/modules/{module_id}/lessons", response_model=List[LessonResponse])
def read_module_lessons(
        *,
        db: Session = Depends(get_db),
        module_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all lessons for a module.
    """
    module = course_service.get_module(db, id=module_id)
    if not module:
        raise HTTPException(
            status_code=404,
            detail="The module with this ID does not exist in the system",
        )

    lessons = course_service.get_module_lessons(db, module_id=module_id)
    return lessons

@router.post("/modules/{module_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
        *,
        db: Session = Depends(get_db),
        module_id: int,
        lesson_in: LessonCreate,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Add a lesson to a module. Instructor/Admin only.
    """
    module = course_service.get_module(db, id=module_id)
    if not module:
        raise HTTPException(
            status_code=404,
            detail="The module with this ID does not exist in the system",
        )

    course = course_service.get(db, id=module.course_id)

    # Ensure the instructor is the creator or an admin
    if course.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to add lessons to this module",
        )

    lesson = course_service.create_lesson(
        db, obj_in=lesson_in, module_id=module_id
    )
    return lesson
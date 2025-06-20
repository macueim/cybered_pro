# backend/app/api/endpoints/modules.py
from typing import List, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.services import module_service, course_service

router = APIRouter()

@router.get("/courses/{course_id}/modules", response_model=List[schemas.Module])
def read_modules(
        course_id: int,
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve modules for a course.
    """
    course = course_service.get(db=db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check permissions
    if current_user.role == "student" and not course.is_published:
        raise HTTPException(status_code=403, detail="Access forbidden")

    if (current_user.role == "instructor" and
            current_user.id != course.instructor_id):
        raise HTTPException(status_code=403, detail="Access forbidden")

    return module_service.get_multi_by_course(
        db=db, course_id=course_id, skip=skip, limit=limit
    )

@router.post("/modules", response_model=schemas.Module)
def create_module(
        *,
        db: Session = Depends(deps.get_db),
        module_in: schemas.ModuleCreate,
        current_user: models.User = Depends(deps.get_current_instructor),
) -> Any:
    """
    Create new module.
    """
    # Check if the course exists and the user has access
    course = course_service.get(db=db, course_id=module_in.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user.role == "instructor" and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only add modules to your own courses"
        )

    return module_service.create(db=db, obj_in=module_in)

@router.get("/modules/{module_id}", response_model=schemas.Module)
def read_module(
        *,
        db: Session = Depends(deps.get_db),
        module_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get module by ID.
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

    return module

@router.put("/modules/{module_id}", response_model=schemas.Module)
def update_module(
        *,
        db: Session = Depends(deps.get_db),
        module_id: int,
        module_in: schemas.ModuleUpdate,
        current_user: models.User = Depends(deps.get_current_instructor),
) -> Any:
    """
    Update a module.
    """
    module = module_service.get(db=db, module_id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get the course to check permissions
    course = course_service.get(db=db, course_id=module.course_id)

    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only update modules in your own courses"
        )

    return module_service.update(db=db, db_obj=module, obj_in=module_in)

@router.delete("/modules/{module_id}")
def delete_module(
        *,
        db: Session = Depends(deps.get_db),
        module_id: int,
        current_user: models.User = Depends(deps.get_current_instructor),
) -> Any:
    """
    Delete a module.
    """
    module = module_service.get(db=db, module_id=module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")

    # Get the course to check permissions
    course = course_service.get(db=db, course_id=module.course_id)

    if course.instructor_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="You can only delete modules in your own courses"
        )

    return module_service.delete(db=db, module_id=module_id)
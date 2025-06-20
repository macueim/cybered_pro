# backend/app/api/endpoints/enrollments.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_current_active_instructor, get_db
from app.models.user import User
from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate, EnrollmentResponse
from app.services import enrollment_service, course_service

router = APIRouter()

@router.get("/", response_model=List[EnrollmentResponse])
def read_enrollments(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get user enrollments.
    """
    # Regular users can only see their own enrollments
    if current_user.role == "student":
        enrollments = enrollment_service.get_user_enrollments(
            db, user_id=current_user.id, skip=skip, limit=limit
        )
    # Instructors and admins can see all enrollments
    else:
        enrollments = enrollment_service.get_multi(db, skip=skip, limit=limit)

    return enrollments

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(
        *,
        db: Session = Depends(get_db),
        enrollment_in: EnrollmentCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Enroll in a course.
    """
    # Check if course exists
    course = course_service.get(db, id=enrollment_in.course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )

    # Check if already enrolled
    existing_enrollment = enrollment_service.get_by_user_and_course(
        db, user_id=current_user.id, course_id=enrollment_in.course_id
    )
    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="You are already enrolled in this course",
        )

    # For regular users, use their own ID
    user_id = current_user.id

    # For admins/instructors enrolling others
    if enrollment_in.user_id and current_user.role in ["admin", "instructor"]:
        user_id = enrollment_in.user_id

    enrollment = enrollment_service.create(
        db, obj_in=enrollment_in, user_id=user_id
    )
    return enrollment

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def read_enrollment(
        *,
        db: Session = Depends(get_db),
        enrollment_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get enrollment details.
    """
    enrollment = enrollment_service.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="The enrollment with this ID does not exist in the system",
        )

    # Regular users can only see their own enrollments
    if current_user.role == "student" and enrollment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to access this enrollment",
        )

    return enrollment

@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
def update_enrollment(
        *,
        db: Session = Depends(get_db),
        enrollment_id: int,
        enrollment_in: EnrollmentUpdate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update enrollment status.
    """
    enrollment = enrollment_service.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="The enrollment with this ID does not exist in the system",
        )

    # Regular users can only update their own enrollments
    if current_user.role == "student" and enrollment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this enrollment",
        )

    enrollment = enrollment_service.update(
        db, db_obj=enrollment, obj_in=enrollment_in
    )
    return enrollment

@router.delete("/{enrollment_id}", response_model=EnrollmentResponse)
def delete_enrollment(
        *,
        db: Session = Depends(get_db),
        enrollment_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Withdraw from a course.
    """
    enrollment = enrollment_service.get(db, id=enrollment_id)
    if not enrollment:
        raise HTTPException(
            status_code=404,
            detail="The enrollment with this ID does not exist in the system",
        )

    # Regular users can only delete their own enrollments
    if current_user.role == "student" and enrollment.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to withdraw from this course",
        )

    enrollment = enrollment_service.delete(db, id=enrollment_id)
    return enrollment
# backend/app/api/endpoints/assessments.py
from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_current_active_instructor, get_db
from app.models.user import User
from app.models.assessment import Assessment, UserAssessment
from app.schemas.assessment import (
    AssessmentCreate, AssessmentUpdate, AssessmentResponse,
    QuestionCreate, QuestionResponse,
    UserAssessmentCreate, UserAssessmentResponse,
    SubmitAssessmentRequest
)
from app.services import assessment_service, course_service

router = APIRouter()

@router.get("/", response_model=List[AssessmentResponse])
def read_assessments(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all assessments.
    """
    if current_user.role in ["admin", "instructor"]:
        assessments = assessment_service.get_multi(db, skip=skip, limit=limit)
    else:
        # Students only see published assessments
        assessments = assessment_service.get_published_assessments(db, skip=skip, limit=limit)

    return assessments

@router.post("/", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
        *,
        db: Session = Depends(get_db),
        assessment_in: AssessmentCreate,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Create a new assessment. Instructor/Admin only.
    """
    # Verify course exists
    course = course_service.get(db, id=assessment_in.course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="The course with this ID does not exist in the system",
        )

    # Verify module exists if provided
    if assessment_in.module_id:
        module = course_service.get_module(db, id=assessment_in.module_id)
        if not module or module.course_id != assessment_in.course_id:
            raise HTTPException(
                status_code=404,
                detail="The module with this ID does not exist in the specified course",
            )

    assessment = assessment_service.create(db, obj_in=assessment_in)
    return assessment

@router.get("/{assessment_id}", response_model=AssessmentResponse)
def read_assessment(
        *,
        db: Session = Depends(get_db),
        assessment_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get specific assessment.
    """
    assessment = assessment_service.get(db, assessment_id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="The assessment with this ID does not exist in the system",
        )

    # Students can only access published assessments
    if current_user.role == "student" and not assessment.is_published:
        raise HTTPException(
            status_code=403,
            detail="This assessment is not yet published",
        )

    return assessment

@router.put("/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
        *,
        db: Session = Depends(get_db),
        assessment_id: int,
        assessment_in: AssessmentUpdate,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Update assessment. Instructor/Admin only.
    """
    assessment = assessment_service.get(db, assessment_id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="The assessment with this ID does not exist in the system",
        )

    # Verify course exists if updating course_id
    if assessment_in.course_id is not None:
        course = course_service.get(db, id=assessment_in.course_id)
        if not course:
            raise HTTPException(
                status_code=404,
                detail="The course with this ID does not exist in the system",
            )

    # Verify module exists if updating module_id
    if assessment_in.module_id is not None:
        module = course_service.get_module(db, id=assessment_in.module_id)
        if not module or module.course_id != (assessment_in.course_id or assessment.course_id):
            raise HTTPException(
                status_code=404,
                detail="The module with this ID does not exist in the specified course",
            )

    assessment = assessment_service.update(
        db, db_obj=assessment, obj_in=assessment_in
    )
    return assessment

@router.delete("/{assessment_id}", response_model=AssessmentResponse)
def delete_assessment(
        *,
        db: Session = Depends(get_db),
        assessment_id: int,
        current_user: User = Depends(get_current_active_instructor),
) -> Any:
    """
    Delete assessment. Instructor/Admin only.
    """
    assessment = assessment_service.get(db, assessment_id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="The assessment with this ID does not exist in the system",
        )

    assessment = assessment_service.delete(db, assessment_id=assessment_id)
    return assessment

@router.post("/{assessment_id}/take", response_model=UserAssessmentResponse)
def take_assessment(
        *,
        db: Session = Depends(get_db),
        assessment_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Start an assessment.
    """
    assessment = assessment_service.get(db, assessment_id=assessment_id)
    if not assessment:
        raise HTTPException(
            status_code=404,
            detail="The assessment with this ID does not exist in the system",
        )

    if not assessment.is_published:
        raise HTTPException(
            status_code=403,
            detail="This assessment is not yet published",
        )

    # Check if user is enrolled in the course
    from app.services import enrollment_service
    enrollment = enrollment_service.get_by_user_and_course(
        db, user_id=current_user.id, course_id=assessment.course_id
    )
    if not enrollment and current_user.role == "student":
        raise HTTPException(
            status_code=403,
            detail="You must be enrolled in this course to take the assessment",
        )

    user_assessment = assessment_service.start_assessment(
        db, user_id=current_user.id, assessment_id=assessment_id
    )
    return user_assessment

@router.post("/{assessment_id}/submit", response_model=UserAssessmentResponse)
def submit_assessment(
        *,
        db: Session = Depends(get_db),
        assessment_id: int,
        submission: SubmitAssessmentRequest,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Submit assessment answers.
    """
    # Verify that the user has started this assessment
    user_assessment = db.query(UserAssessment).filter(
        UserAssessment.user_id == current_user.id,
        UserAssessment.assessment_id == assessment_id,
        UserAssessment.status == "in_progress"
    ).first()

    if not user_assessment:
        raise HTTPException(
            status_code=404,
            detail="No active assessment found for this user",
        )

    # Submit the assessment
    user_assessment = assessment_service.submit_assessment(
        db, user_assessment_id=user_assessment.id, answers=submission.answers
    )

    return user_assessment
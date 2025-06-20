# backend/app/services/assessment_service.py
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.assessment import Assessment, Question, Answer, UserAssessment, UserAnswer
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate

def get(db: Session, assessment_id: int) -> Optional[Assessment]:
    return db.query(Assessment).filter(Assessment.id == assessment_id).first()

def get_multi_by_course(
        db: Session, *, course_id: int, skip: int = 0, limit: int = 100
) -> List[Assessment]:
    return db.query(Assessment).filter(
        Assessment.course_id == course_id
    ).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: AssessmentCreate) -> Assessment:
    db_obj = Assessment(
        course_id=obj_in.course_id,
        module_id=obj_in.module_id,
        title=obj_in.title,
        description=obj_in.description,
        time_limit_minutes=obj_in.time_limit_minutes,
        passing_score=obj_in.passing_score,
        is_published=obj_in.is_published,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(
        db: Session, *, db_obj: Assessment, obj_in: Union[AssessmentUpdate, Dict[str, Any]]
) -> Assessment:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, *, assessment_id: int) -> Assessment:
    obj = db.query(Assessment).get(assessment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Assessment not found")
    db.delete(obj)
    db.commit()
    return obj

# User assessment functions
def start_assessment(db: Session, *, user_id: int, assessment_id: int) -> UserAssessment:
    # Check if user already has an active assessment
    existing = db.query(UserAssessment).filter(
        UserAssessment.user_id == user_id,
        UserAssessment.assessment_id == assessment_id,
        UserAssessment.status == "in_progress"
    ).first()

    if existing:
        return existing

    # Create new user assessment
    user_assessment = UserAssessment(
        user_id=user_id,
        assessment_id=assessment_id,
        status="in_progress"
    )
    db.add(user_assessment)
    db.commit()
    db.refresh(user_assessment)
    return user_assessment

def submit_assessment(
        db: Session, *, user_assessment_id: int, answers: List[Dict]
) -> UserAssessment:
    # Get the user assessment
    user_assessment = db.query(UserAssessment).get(user_assessment_id)
    if not user_assessment:
        raise HTTPException(status_code=404, detail="Assessment submission not found")

    if user_assessment.status == "completed":
        raise HTTPException(status_code=400, detail="Assessment already submitted")

    # Get the assessment and its questions
    assessment = db.query(Assessment).get(user_assessment.assessment_id)
    questions = db.query(Question).filter(Question.assessment_id == assessment.id).all()

    # Create a dictionary of questions by ID for easy lookup
    questions_dict = {q.id: q for q in questions}

    # Process user answers
    total_points = 0
    earned_points = 0

    for answer_data in answers:
        question_id = answer_data.get("question_id")
        answer_id = answer_data.get("answer_id")
        text_answer = answer_data.get("text_answer")

        if question_id not in questions_dict:
            continue

        question = questions_dict[question_id]
        total_points += question.points

        # Create user answer record
        user_answer = UserAnswer(
            user_assessment_id=user_assessment.id,
            question_id=question_id,
            answer_id=answer_id,
            text_answer=text_answer
        )

        # Grade MCQ and true/false questions automatically
        if question.question_type in ["mcq", "true_false"] and answer_id:
            # Get the selected answer
            answer = db.query(Answer).get(answer_id)
            if answer and answer.question_id == question_id:
                user_answer.is_correct = answer.is_correct
                if answer.is_correct:
                    user_answer.points_earned = question.points
                    earned_points += question.points

        db.add(user_answer)

    # Calculate score as percentage
    score = (earned_points / total_points * 100) if total_points > 0 else 0

    # Update user assessment
    user_assessment.score = score
    user_assessment.end_time = datetime.now()
    user_assessment.status = "completed"

    db.commit()
    db.refresh(user_assessment)
    return user_assessment
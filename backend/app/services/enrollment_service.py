# backend/app/services/enrollment_service.py
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.enrollment import Enrollment
from app.schemas.enrollment import EnrollmentCreate, EnrollmentUpdate

def get(db: Session, enrollment_id: int) -> Optional[Enrollment]:
    return db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()

def get_by_user_and_course(
        db: Session, *, user_id: int, course_id: int
) -> Optional[Enrollment]:
    return db.query(Enrollment).filter(
        Enrollment.user_id == user_id,
        Enrollment.course_id == course_id
    ).first()

def get_multi_by_user(
        db: Session, *, user_id: int, skip: int = 0, limit: int = 100
) -> List[Enrollment]:
    return db.query(Enrollment).filter(
        Enrollment.user_id == user_id
    ).offset(skip).limit(limit).all()

def get_multi_by_course(
        db: Session, *, course_id: int, skip: int = 0, limit: int = 100
) -> List[Enrollment]:
    return db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: EnrollmentCreate) -> Enrollment:
    # Check if enrollment already exists
    existing = get_by_user_and_course(
        db=db, user_id=obj_in.user_id, course_id=obj_in.course_id
    )
    if existing:
        if existing.status == "withdrawn":
            # Reactivate withdrawn enrollment
            existing.status = "active"
            existing.progress = 0.0
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=400,
                detail="User is already enrolled in this course"
            )

    db_obj = Enrollment(
        user_id=obj_in.user_id,
        course_id=obj_in.course_id,
        status=obj_in.status,
        progress=obj_in.progress,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(
        db: Session, *, db_obj: Enrollment, obj_in: Union[EnrollmentUpdate, Dict[str, Any]]
) -> Enrollment:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)

    # If updating to "completed" status, set completion date
    if update_data.get("status") == "completed" and db_obj.status != "completed":
        update_data["completed_at"] = datetime.now()

    for field in update_data:
        setattr(db_obj, field, update_data[field])

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, *, enrollment_id: int) -> Enrollment:
    obj = db.query(Enrollment).get(enrollment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(obj)
    db.commit()
    return obj
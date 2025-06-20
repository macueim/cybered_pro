# backend/app/services/course_service.py
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.course import Course
from app.schemas.course import CourseCreate, CourseUpdate

def get(db: Session, course_id: int) -> Optional[Course]:
    return db.query(Course).filter(Course.id == course_id).first()

def get_multi(
        db: Session, *, skip: int = 0, limit: int = 100, instructor_id: Optional[int] = None
) -> List[Course]:
    query = db.query(Course)
    if instructor_id:
        query = query.filter(Course.instructor_id == instructor_id)
    return query.offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: CourseCreate, instructor_id: int) -> Course:
    db_obj = Course(
        title=obj_in.title,
        description=obj_in.description,
        instructor_id=instructor_id,
        certification_type=obj_in.certification_type,
        difficulty_level=obj_in.difficulty_level,
        estimated_duration=obj_in.estimated_duration,
        is_published=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(
        db: Session, *, db_obj: Course, obj_in: Union[CourseUpdate, Dict[str, Any]]
) -> Course:
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

def delete(db: Session, *, course_id: int) -> Course:
    obj = db.query(Course).get(course_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(obj)
    db.commit()
    return obj
# backend/app/services/course_service.py
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.course import Course, Module, Lesson
from app.schemas.course import CourseCreate, CourseUpdate
from app.schemas.course import ModuleCreate, LessonCreate

def get(db: Session, id: int) -> Optional[Course]:
    return db.query(Course).filter(Course.id == id).first()

def get_multi(
        db: Session, *, skip: int = 0, limit: int = 100, instructor_id: Optional[int] = None
) -> List[Course]:
    query = db.query(Course)
    if instructor_id:
        query = query.filter(Course.instructor_id == instructor_id)
    return query.offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: CourseCreate, creator_id: int) -> Course:
    db_obj = Course(
        title=obj_in.title,
        description=obj_in.description,
        creator_id=creator_id,
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

def delete(db: Session, *, id: int) -> Course:
    obj = db.query(Course).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(obj)
    db.commit()
    return obj

# Module related functions
def get_module(db: Session, id: int) -> Optional[Module]:
    return db.query(Module).filter(Module.id == id).first()

def get_course_modules(db: Session, course_id: int) -> List[Module]:
    return db.query(Module).filter(Module.course_id == course_id).order_by(Module.order_index).all()

def create_module(db: Session, *, obj_in: ModuleCreate, course_id: int) -> Module:
    db_obj = Module(
        title=obj_in.title,
        description=obj_in.description,
        course_id=course_id,
        order_index=obj_in.order_index,
        content=obj_in.content,
        estimated_duration=obj_in.estimated_duration,
        is_published=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

# Lesson related functions
def get_module_lessons(db: Session, module_id: int) -> List[Lesson]:
    return db.query(Lesson).filter(Lesson.module_id == module_id).order_by(Lesson.order).all()

def create_lesson(db: Session, *, obj_in: LessonCreate, module_id: int) -> Lesson:
    db_obj = Lesson(
        title=obj_in.title,
        content=obj_in.content,
        module_id=module_id,
        order=obj_in.order if obj_in.order is not None else 0,
        estimated_time_minutes=obj_in.estimated_time_minutes,
        is_published=False,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

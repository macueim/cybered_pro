# backend/app/services/lesson_service.py
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.course import Lesson
from app.schemas.lesson import LessonCreate, LessonUpdate

def get(db: Session, lesson_id: int) -> Optional[Lesson]:
    return db.query(Lesson).filter(Lesson.id == lesson_id).first()

def get_multi_by_module(
        db: Session, *, module_id: int, skip: int = 0, limit: int = 100
) -> List[Lesson]:
    return db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).order_by(Lesson.order_index).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: LessonCreate) -> Lesson:
    # Find the highest order_index for this module and add 1
    highest_index = db.query(Lesson).filter(
        Lesson.module_id == obj_in.module_id
    ).order_by(Lesson.order_index.desc()).first()

    new_index = 1
    if highest_index:
        new_index = highest_index.order_index + 1

    db_obj = Lesson(
        module_id=obj_in.module_id,
        title=obj_in.title,
        content_type=obj_in.content_type,
        content=obj_in.content,
        order_index=new_index,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(
        db: Session, *, db_obj: Lesson, obj_in: Union[LessonUpdate, Dict[str, Any]]
) -> Lesson:
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

def delete(db: Session, *, lesson_id: int) -> Lesson:
    obj = db.query(Lesson).get(lesson_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db.delete(obj)
    db.commit()
    return obj
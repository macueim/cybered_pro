# backend/app/services/module_service.py
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.course import Module
from app.schemas.module import ModuleCreate, ModuleUpdate

def get(db: Session, module_id: int) -> Optional[Module]:
    return db.query(Module).filter(Module.id == module_id).first()

def get_multi_by_course(
        db: Session, *, course_id: int, skip: int = 0, limit: int = 100
) -> List[Module]:
    return db.query(Module).filter(
        Module.course_id == course_id
    ).order_by(Module.order_index).offset(skip).limit(limit).all()

def create(db: Session, *, obj_in: ModuleCreate) -> Module:
    # Find the highest order_index for this course and add 1
    highest_index = db.query(Module).filter(
        Module.course_id == obj_in.course_id
    ).order_by(Module.order_index.desc()).first()

    new_index = 1
    if highest_index:
        new_index = highest_index.order_index + 1

    db_obj = Module(
        course_id=obj_in.course_id,
        title=obj_in.title,
        description=obj_in.description,
        order_index=new_index,
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(
        db: Session, *, db_obj: Module, obj_in: Union[ModuleUpdate, Dict[str, Any]]
) -> Module:
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

def delete(db: Session, *, module_id: int) -> Module:
    obj = db.query(Module).get(module_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Module not found")
    db.delete(obj)
    db.commit()
    return obj
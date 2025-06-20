# backend/app/services/forum_service.py
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.models.forum import ForumTopic, ForumReply
from app.schemas.forum import ForumTopicCreate, ForumReplyCreate

def get_topics(db: Session, skip: int = 0, limit: int = 100) -> List[ForumTopic]:
    """
    Get all forum topics.
    """
    return db.query(ForumTopic).order_by(ForumTopic.created_at.desc()).offset(skip).limit(limit).all()

def get_topic(db: Session, topic_id: int) -> Optional[ForumTopic]:
    """
    Get a forum topic by ID.
    """
    return db.query(ForumTopic).filter(ForumTopic.id == topic_id).first()

def create_topic(db: Session, obj_in: ForumTopicCreate, user_id: int) -> ForumTopic:
    """
    Create a new forum topic.
    """
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = ForumTopic(**obj_in_data, user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def create_reply(db: Session, obj_in: ForumReplyCreate, topic_id: int, user_id: int) -> ForumReply:
    """
    Create a new forum reply.
    """
    obj_in_data = jsonable_encoder(obj_in)
    db_obj = ForumReply(**obj_in_data, topic_id=topic_id, user_id=user_id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
# backend/app/api/endpoints/forums.py
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.forum import (
    ForumTopicCreate, ForumTopicResponse,
    ForumReplyCreate, ForumReplyResponse
)
from app.services import forum_service

router = APIRouter()

@router.get("/topics", response_model=List[ForumTopicResponse])
def read_forum_topics(
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get all forum topics.
    """
    topics = forum_service.get_topics(db, skip=skip, limit=limit)
    return topics

@router.post("/topics", response_model=ForumTopicResponse, status_code=status.HTTP_201_CREATED)
def create_forum_topic(
        *,
        db: Session = Depends(get_db),
        topic_in: ForumTopicCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new forum topic.
    """
    topic = forum_service.create_topic(
        db, obj_in=topic_in, user_id=current_user.id
    )
    return topic

@router.get("/topics/{topic_id}", response_model=ForumTopicResponse)
def read_forum_topic(
        *,
        db: Session = Depends(get_db),
        topic_id: int,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get specific forum topic with its replies.
    """
    topic = forum_service.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=404,
            detail="The forum topic with this ID does not exist in the system",
        )

    return topic

@router.post("/topics/{topic_id}/replies", response_model=ForumReplyResponse, status_code=status.HTTP_201_CREATED)
def create_forum_reply(
        *,
        db: Session = Depends(get_db),
        topic_id: int,
        reply_in: ForumReplyCreate,
        current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Add reply to a forum topic.
    """
    topic = forum_service.get_topic(db, topic_id=topic_id)
    if not topic:
        raise HTTPException(
            status_code=404,
            detail="The forum topic with this ID does not exist in the system",
        )

    reply = forum_service.create_reply(
        db, obj_in=reply_in, topic_id=topic_id, user_id=current_user.id
    )
    return reply
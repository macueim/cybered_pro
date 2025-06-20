# backend/app/api/api.py
from fastapi import APIRouter

from app.api.endpoints import users, courses, enrollments, assessments, forums, progress

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(forums.router, prefix="/forums", tags=["forums"])
api_router.include_router(progress.router, prefix="/progress", tags=["progress"])
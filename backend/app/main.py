# backend/app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.db.init_db import init_db

# Create FastAPI app
app = FastAPI(
    title="CyberEd Pro",
    description="Cybersecurity Learning Management System",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Basic health check endpoint
@app.get("/")
def read_root():
    return {"status": "healthy", "message": "Welcome to CyberEd Pro API"}

# Create a simple ping endpoint for testing
@app.get("/ping")
def ping():
    return {"ping": "pong"}

@app.on_event("startup")
def startup_db_client():
    """
    Initialize the database with initial data if needed
    """
    try:
        # Create tables and initial data
        init_db()
    except Exception as e:
        print(f"Database initialization error: {e}")

# API endpoints based on the project requirements
# These endpoints are organized in the api_router which is included above,
# but here's a summary of the endpoints that will be available:

# User Management Endpoints:
# POST /api/v1/users/register - Register a new user
# POST /api/v1/users/login - User login
# GET /api/v1/users/me - Get current user profile
# PUT /api/v1/users/me - Update current user profile
# GET /api/v1/users/ - Get all users (admin only)
# GET /api/v1/users/{user_id} - Get specific user (admin only)
# PUT /api/v1/users/{user_id} - Update specific user (admin only)
# DELETE /api/v1/users/{user_id} - Delete user (admin only)

# Course Management Endpoints:
# GET /api/v1/courses/ - Get all courses
# POST /api/v1/courses/ - Create a new course (instructor/admin only)
# GET /api/v1/courses/{course_id} - Get specific course
# PUT /api/v1/courses/{course_id} - Update course (instructor/admin only)
# DELETE /api/v1/courses/{course_id} - Delete course (instructor/admin only)
# GET /api/v1/courses/{course_id}/modules - Get course modules
# POST /api/v1/courses/{course_id}/modules - Add module to course
# GET /api/v1/modules/{module_id}/lessons - Get module lessons
# POST /api/v1/modules/{module_id}/lessons - Add lesson to module

# Enrollment Endpoints:
# GET /api/v1/enrollments/ - Get user enrollments
# POST /api/v1/enrollments/ - Enroll in a course
# GET /api/v1/enrollments/{enrollment_id} - Get enrollment details
# PUT /api/v1/enrollments/{enrollment_id} - Update enrollment status
# DELETE /api/v1/enrollments/{enrollment_id} - Withdraw from a course

# Assessment Endpoints:
# GET /api/v1/assessments/ - Get all assessments
# POST /api/v1/assessments/ - Create a new assessment (instructor/admin only)
# GET /api/v1/assessments/{assessment_id} - Get specific assessment
# PUT /api/v1/assessments/{assessment_id} - Update assessment (instructor/admin only)
# DELETE /api/v1/assessments/{assessment_id} - Delete assessment (instructor/admin only)
# POST /api/v1/assessments/{assessment_id}/take - Start an assessment
# POST /api/v1/assessments/{assessment_id}/submit - Submit assessment answers

# Forum Endpoints:
# GET /api/v1/forums/topics - Get all forum topics
# POST /api/v1/forums/topics - Create a new forum topic
# GET /api/v1/forums/topics/{topic_id} - Get specific forum topic
# POST /api/v1/forums/topics/{topic_id}/replies - Add reply to a forum topic

# User Progress Tracking:
# GET /api/v1/progress/courses/{course_id} - Get user progress in a course
# POST /api/v1/progress/lessons/{lesson_id} - Mark lesson as complete
# GET /api/v1/progress/assessments - Get user assessment results

# Run with: uvicorn app.main:app --reload
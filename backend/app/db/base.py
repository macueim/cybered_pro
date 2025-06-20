# backend/app/db/base.py

# Import the Base class only once
from app.db.base_class import Base  # noqa

# Import all the models here that should be included in the Base metadata
# This is to ensure Alembic sees all models during migration
from app.models.user import User  # noqa
from app.models.course import Course, Module, Lesson  # noqa
from app.models.assessment import Assessment, Question, Answer, UserAssessment, UserAnswer  # noqa
from app.models.enrollment import Enrollment  # noqa
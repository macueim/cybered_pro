# backend/app/models/course.py (updated)
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    certification_type = Column(String, nullable=True)  # Security+, CEH, CISSP, etc.
    difficulty_level = Column(String, nullable=False, default='beginner')
    estimated_duration = Column(Integer, nullable=True)  # in hours
    is_published = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instructor = relationship("User", backref="courses", foreign_keys=[creator_id])
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    forum_topics = relationship("ForumTopic", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id}, title='{self.title}', creator_id={self.creator_id})>"


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    order_index = Column(Integer, nullable=False, default=0)  # For ordering modules within a course
    content = Column(Text, nullable=True)  # Module content/materials
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Module(id={self.id}, title='{self.title}', course_id={self.course_id})>"


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False, index=True)
    order = Column(Integer, nullable=False, default=0)  # For ordering lessons within a module
    estimated_time_minutes = Column(Integer, nullable=True)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    module = relationship("Module", back_populates="lessons")

    def __repr__(self):
        return f"<Lesson(id={self.id}, title='{self.title}', module_id={self.module_id})>"

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EnrollmentBase(BaseModel):
    user_id: int
    course_id: int
    status: str = "active"
    progress: float = 0.0


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    status: Optional[str] = None
    progress: Optional[float] = None
    completed_at: Optional[datetime] = None


class EnrollmentResponse(EnrollmentBase):
    id: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Using Pydantic v2 attribute


# You might also need a more detailed response with related data
class EnrollmentDetailResponse(EnrollmentResponse):
    # Add any additional fields you need for detailed views
    # For example, you might want to include user or course details

    class Config:
        from_attributes = True
# backend/app/schemas/assessment.py
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator

class AnswerBase(BaseModel):
    answer_text: str
    is_correct: bool
    explanation: Optional[str] = None

class AnswerCreate(AnswerBase):
    pass

class AnswerUpdate(BaseModel):
    answer_text: Optional[str] = None
    is_correct: Optional[bool] = None
    explanation: Optional[str] = None

class AnswerResponse(AnswerBase):
    id: int
    question_id: int

    model_config = {
        "from_attributes": True
    }

# Alias for backward compatibility
Answer = AnswerResponse

class QuestionBase(BaseModel):
    question_text: str
    question_type: str
    points: float = 1.0

    @field_validator("question_type")
    def validate_question_type(cls, v):
        allowed_types = ["mcq", "true_false", "short_answer"]
        if v not in allowed_types:
            raise ValueError(f"Question type must be one of {allowed_types}")
        return v

class QuestionCreate(QuestionBase):
    assessment_id: int
    answers: Optional[List[AnswerCreate]] = None

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    points: Optional[float] = None

class QuestionResponse(QuestionBase):
    id: int
    assessment_id: int
    answers: List[AnswerResponse] = []

    model_config = {
        "from_attributes": True
    }

# Alias for backward compatibility
Question = QuestionResponse

class AssessmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    passing_score: float = 70.0
    is_published: bool = False

class AssessmentCreate(AssessmentBase):
    course_id: int
    module_id: Optional[int] = None

class AssessmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    time_limit_minutes: Optional[int] = None
    passing_score: Optional[float] = None
    is_published: Optional[bool] = None
    module_id: Optional[int] = None
    course_id: Optional[int] = None  # Added course_id as it's used in the API

class AssessmentResponse(AssessmentBase):
    id: int
    course_id: int
    module_id: Optional[int] = None
    created_at: datetime
    questions: List[QuestionResponse] = []

    model_config = {
        "from_attributes": True
    }

# Alias for backward compatibility
Assessment = AssessmentResponse

class UserAnswerBase(BaseModel):
    question_id: int
    answer_id: Optional[int] = None
    text_answer: Optional[str] = None

class UserAnswerCreate(UserAnswerBase):
    pass

class UserAnswerResponse(UserAnswerBase):
    id: int
    user_assessment_id: int
    is_correct: Optional[bool] = None
    points_earned: Optional[float] = None

    model_config = {
        "from_attributes": True
    }

# Alias for backward compatibility
UserAnswer = UserAnswerResponse

class UserAssessmentBase(BaseModel):
    assessment_id: int

class UserAssessmentCreate(UserAssessmentBase):
    pass

class UserAssessmentUpdate(BaseModel):
    status: Optional[str] = None
    end_time: Optional[datetime] = None
    score: Optional[float] = None

class UserAssessmentSubmit(BaseModel):
    answers: List[UserAnswerCreate]

class UserAssessmentResponse(UserAssessmentBase):
    id: int
    user_id: int
    score: Optional[float] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    answers: List[UserAnswerResponse] = []

    model_config = {
        "from_attributes": True
    }

# Alias for backward compatibility
UserAssessment = UserAssessmentResponse

# Adding missing class referenced in the assessment endpoints
class SubmitAssessmentRequest(BaseModel):
    answers: List[UserAnswerCreate]
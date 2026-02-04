from datetime import datetime
from pydantic import BaseModel, field_validator
from typing import Optional, List

# ================= USERS =================
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# ================= EXAMS =================
class ExamCreate(BaseModel):
    title: str
    description: str
    duration_minutes: int


class ExamOut(BaseModel):
    id: int
    title: str
    description: str
    duration_minutes: int

    class Config:
        from_attributes = True


# ================= QUESTIONS =================
class QuestionCreate(BaseModel):
    exam_id: int
    question_text: str
    type: str  # mcq | text | code
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None

    @field_validator("options")
    @classmethod
    def validate_options(cls, value):
        if value is not None and len(value) != 4:
            raise ValueError("MCQ must have exactly 4 options")
        return value


class QuestionOut(BaseModel):
    id: int
    text: str
    question_type: str
    options: Optional[List[str]] = None


# ================= SUBMISSIONS =================
class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str


class ExamSubmit(BaseModel):
    exam_id: int
    answers: List[AnswerSubmit]


class AnswerSave(BaseModel):
    exam_id: int
    question_id: int
    selected_option: str


class SubmissionSubmit(BaseModel):
    exam_id: int


class SubmissionOut(BaseModel):
    id: int
    exam_id: int
    user_id: int
    score: float
    submitted_at: datetime

    class Config:
        from_attributes = True

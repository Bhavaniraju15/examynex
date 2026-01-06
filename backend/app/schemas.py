from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "student"

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ExamCreate(BaseModel):
    title: str
    description: str | None = None
    duration: int = 60  # Default to 60 minutes


class AnswerSubmit(BaseModel):
    question_id: int
    answer_text: str


class ExamSubmit(BaseModel):
    exam_id: int
    answers: list[AnswerSubmit]
class QuestionCreate(BaseModel):
    text: str
    exam_id: int
    correct_answer: str | None = None
    is_mcq: bool = False

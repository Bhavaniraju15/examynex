from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    Boolean,
    Float
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# ==================== USER ====================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="student")

    submissions = relationship("ExamSubmission", back_populates="user")


# ==================== EXAM ====================
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    duration_minutes = Column(Integer, default=60)

    questions = relationship("Question", back_populates="exam", cascade="all, delete")
    submissions = relationship("ExamSubmission", back_populates="exam")


# ==================== QUESTION ====================

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)

    text = Column(String, nullable=False)
    question_type = Column(String, nullable=False)  # mcq | text | code

    # MCQ options (used only if type == mcq)
    option_a = Column(String, nullable=True)
    option_b = Column(String, nullable=True)
    option_c = Column(String, nullable=True)
    option_d = Column(String, nullable=True)

    correct_answer = Column(String, nullable=True)  # optional (for auto-eval)

    exam = relationship("Exam", back_populates="questions")
    answers = relationship("Answer", back_populates="question")


# ==================== EXAM SUBMISSION ====================
class ExamSubmission(Base):
    __tablename__ = "exam_submissions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    score = Column(Float, default=0.0)
    is_finalized = Column(Boolean, default=False)

    exam = relationship("Exam", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    answers = relationship("Answer", back_populates="submission")


# ==================== ANSWER ====================
class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("exam_submissions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(String)
    ai_score = Column(Float)

    submission = relationship("ExamSubmission", back_populates="answers")
    question = relationship("Question", back_populates="answers")

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
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="student")

    submissions = relationship("ExamSubmission", back_populates="user")


# ==================== EXAM ====================
class Exam(Base):
    __tablename__ = "exams"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    duration = Column(Integer, nullable=False)  # ⬅️ minutes

    questions = relationship("Question", back_populates="exam")
    submissions = relationship("ExamSubmission", back_populates="exam")


# ==================== QUESTION ====================
class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    exam_id = Column(Integer, ForeignKey("exams.id"), nullable=False)

    correct_answer = Column(String, nullable=True)
    is_mcq = Column(Boolean, default=False)

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

    ai_score = Column(Float, nullable=True)

    submission = relationship("ExamSubmission", back_populates="answers")
    question = relationship("Question", back_populates="answers")

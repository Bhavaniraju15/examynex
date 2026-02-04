from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    LargeBinary
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# ===================== PROCTOR SESSION =====================
class ProctorSession(Base):
    __tablename__ = "proctor_sessions"

    id = Column(Integer, primary_key=True, index=True)
    exam_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    # 🔐 FACE IDENTITY VERIFICATION (STEP 8)
    # Stores face embedding (128-d vector as bytes)
    face_embedding = Column(LargeBinary, nullable=True)

    started_at = Column(DateTime, default=datetime.utcnow)

    violations = relationship(
        "ProctorViolation",
        back_populates="session",
        cascade="all, delete-orphan"
    )


# ===================== PROCTOR VIOLATION =====================
class ProctorViolation(Base):
    __tablename__ = "proctor_violations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer,
        ForeignKey("proctor_sessions.id", ondelete="CASCADE"),
        nullable=False
    )

    # Violation types:
    # NO_FACE, LEFT_SEAT, MULTIPLE_FACES,
    # CAMERA_COVERED, TALKING_DETECTED,
    # TAB_SWITCH, WINDOW_BLUR,
    # 🔥 IMPERSONATION
    violation_type = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)

    session = relationship("ProctorSession", back_populates="violations")

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user

router = APIRouter(prefix="/exams", tags=["Exams"])

@router.post("/")
def create_exam(
    exam: schemas.ExamCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Allow both faculty and admin to create exams
    if user["role"] not in ["admin", "faculty"]:
        raise HTTPException(status_code=403, detail="Only faculty and admins can create exams")

    db_exam = models.Exam(
        title=exam.title,
        description=exam.description,
        duration=exam.duration
    )

    db.add(db_exam)
    db.commit()
    db.refresh(db_exam)

    return {
        "id": db_exam.id,
        "title": db_exam.title,
        "description": db_exam.description
    }


@router.get("/")
def list_exams(db: Session = Depends(get_db)):
    exams = db.query(models.Exam).all()

    return [
        {
            "id": exam.id,
            "title": exam.title,
            "description": exam.description
        }
        for exam in exams
    ]

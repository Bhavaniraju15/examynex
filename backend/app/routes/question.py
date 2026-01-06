from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/questions", tags=["Questions"])

@router.post("/")
def add_question(
    question: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Allow both faculty and admin to add questions
    if user["role"] not in ["admin", "faculty"]:
        raise HTTPException(status_code=403, detail="Only faculty and admins can add questions")

    db_question = models.Question(
        text=question.text,
        exam_id=question.exam_id,
        correct_answer=question.correct_answer,
        is_mcq=question.is_mcq
    )

    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    return {
        "id": db_question.id,
        "text": db_question.text,
        "exam_id": db_question.exam_id,
        "is_mcq": db_question.is_mcq,
        "correct_answer": db_question.correct_answer
    }

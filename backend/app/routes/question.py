from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/questions", tags=["Questions"])


# =========================
# ADD QUESTION (ADMIN ONLY)
# =========================
@router.post("/", status_code=201)
def add_question(
    payload: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    exam = db.query(models.Exam).filter(models.Exam.id == payload.exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if payload.type == "mcq":
        if not payload.options or len(payload.options) != 4:
            raise HTTPException(
                status_code=400,
                detail="MCQ must have exactly 4 options",
            )
        if not payload.correct_answer:
            raise HTTPException(
                status_code=400,
                detail="MCQ must have correct answer",
            )

    q = models.Question(
        exam_id=payload.exam_id,
        text=payload.question_text,
        question_type=payload.type,
        option_a=payload.options[0] if payload.type == "mcq" else None,
        option_b=payload.options[1] if payload.type == "mcq" else None,
        option_c=payload.options[2] if payload.type == "mcq" else None,
        option_d=payload.options[3] if payload.type == "mcq" else None,
        correct_answer=payload.correct_answer if payload.type == "mcq" else None,
    )

    db.add(q)
    db.commit()
    db.refresh(q)

    return {
        "message": "Question added successfully",
        "question_id": q.id,
    }


# =========================
# GET QUESTIONS BY EXAM (STUDENT)
# =========================
@router.get("/{exam_id}", response_model=List[schemas.QuestionOut])
def get_questions(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    questions = (
        db.query(models.Question)
        .filter(models.Question.exam_id == exam_id)
        .all()
    )

    result = []

    for q in questions:
        options = None
        if q.question_type == "mcq":
            options = [
                q.option_a,
                q.option_b,
                q.option_c,
                q.option_d,
            ]

        result.append({
            "id": q.id,
            "text": q.text,
            "question_type": q.question_type,
            "options": options,
        })

    return result

# =========================
# UPDATE QUESTION (ADMIN ONLY)
# =========================
@router.put("/{question_id}")
def update_question(
    question_id: int,
    payload: schemas.QuestionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question.text = payload.question_text
    question.question_type = payload.type
    
    if payload.type == "mcq":
        if not payload.options or len(payload.options) != 4:
            raise HTTPException(status_code=400, detail="MCQ must have exactly 4 options")
        if not payload.correct_answer:
            raise HTTPException(status_code=400, detail="MCQ must have correct answer")
        
        question.option_a = payload.options[0]
        question.option_b = payload.options[1]
        question.option_c = payload.options[2]
        question.option_d = payload.options[3]
        question.correct_answer = payload.correct_answer

    db.commit()
    db.refresh(question)

    return {
        "message": "Question updated successfully",
        "question_id": question.id,
    }


# =========================
# DELETE QUESTION (ADMIN ONLY)
# =========================
@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()

    return {"message": "Question deleted successfully"}
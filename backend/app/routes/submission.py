from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/submissions", tags=["Exam Submission"])


# =========================
# GET OR CREATE ACTIVE SUBMISSION
# =========================
def _get_or_create_active_submission(
    db: Session,
    *,
    user_id: int,
    exam_id: int,
):
    submission = (
        db.query(models.ExamSubmission)
        .filter(
            models.ExamSubmission.exam_id == exam_id,
            models.ExamSubmission.user_id == user_id,
            models.ExamSubmission.is_finalized == False,  # noqa
        )
        .first()
    )

    if submission:
        return submission

    submission = models.ExamSubmission(
        exam_id=exam_id,
        user_id=user_id,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


# =========================
# SAVE ANSWER (STUDENT)
# =========================
@router.post("/answer")
def save_answer(
    payload: schemas.AnswerSave,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can save answers")

    submission = (
        db.query(models.ExamSubmission)
        .filter(
            models.ExamSubmission.exam_id == payload.exam_id,
            models.ExamSubmission.user_id == user["user_id"],
        )
        .first()
    )

    # 🔒 BLOCK answer saving after submission
    if submission and submission.is_finalized:
        raise HTTPException(
            status_code=400,
            detail="Exam already submitted. Answers are locked.",
        )

    question = (
        db.query(models.Question)
        .filter(
            models.Question.id == payload.question_id,
            models.Question.exam_id == payload.exam_id,
        )
        .first()
    )

    if not question:
        raise HTTPException(status_code=404, detail="Question not found for exam")

    submission = _get_or_create_active_submission(
        db,
        user_id=user["user_id"],
        exam_id=payload.exam_id,
    )

    answer = (
        db.query(models.Answer)
        .filter(
            models.Answer.submission_id == submission.id,
            models.Answer.question_id == payload.question_id,
        )
        .first()
    )

    if answer:
        answer.answer_text = payload.selected_option
    else:
        db.add(
            models.Answer(
                submission_id=submission.id,
                question_id=payload.question_id,
                answer_text=payload.selected_option,
            )
        )

    db.commit()
    return {"message": "Answer saved"}


# =========================
# SUBMIT EXAM (FINAL)
# =========================
@router.post("/submit", response_model=schemas.SubmissionOut)
def submit_exam(
    payload: schemas.SubmissionSubmit,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit exams")

    submission = (
        db.query(models.ExamSubmission)
        .filter(
            models.ExamSubmission.exam_id == payload.exam_id,
            models.ExamSubmission.user_id == user["user_id"],
        )
        .first()
    )

    # 🔒 BLOCK double submit
    if submission and submission.is_finalized:
        raise HTTPException(
            status_code=400,
            detail="Exam already submitted",
        )

    submission = _get_or_create_active_submission(
        db,
        user_id=user["user_id"],
        exam_id=payload.exam_id,
    )

    answers = (
        db.query(models.Answer)
        .filter(models.Answer.submission_id == submission.id)
        .all()
    )

    if not answers:
        raise HTTPException(status_code=400, detail="No answers saved for this exam")

    score = 0
    total_mcq = 0

    for ans in answers:
        question = (
            db.query(models.Question)
            .filter(models.Question.id == ans.question_id)
            .first()
        )

        # ✅ CORRECT CHECK (matches your schema)
        if not question or question.question_type != "mcq":
            continue

        total_mcq += 1
        if (
            question.correct_answer
            and ans.answer_text
            and ans.answer_text.strip().lower()
            == question.correct_answer.strip().lower()
        ):
            score += 1

    submission.score = (score / total_mcq) * 100 if total_mcq > 0 else 0
    submission.is_finalized = True
    submission.submitted_at = datetime.utcnow()

    db.commit()
    db.refresh(submission)

    return submission


# =========================
# GET SUBMISSION RESULT (STUDENT)
# =========================
@router.get("/{exam_id}/result", response_model=schemas.SubmissionOut)
def get_submission_result(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can view results")

    submission = (
        db.query(models.ExamSubmission)
        .filter(
            models.ExamSubmission.exam_id == exam_id,
            models.ExamSubmission.user_id == user["user_id"],
            models.ExamSubmission.is_finalized == True,
        )
        .first()
    )

    if not submission:
        raise HTTPException(
            status_code=404,
            detail="No submitted exam found",
        )

    return submission

# =========================
# GET ALL SUBMISSIONS (ADMIN)
# =========================
@router.get("/admin/all", response_model=list[schemas.SubmissionOut])
def get_all_submissions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view all submissions")

    submissions = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.is_finalized == True
    ).all()

    return submissions


# =========================
# GET SUBMISSIONS BY EXAM (ADMIN)
# =========================
@router.get("/admin/exam/{exam_id}")
def get_exam_submissions(
    exam_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view submissions")

    submissions = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.exam_id == exam_id,
        models.ExamSubmission.is_finalized == True
    ).all()

    result = []
    for sub in submissions:
        user_obj = db.query(models.User).filter(models.User.id == sub.user_id).first()
        result.append({
            "id": sub.id,
            "exam_id": sub.exam_id,
            "user_id": sub.user_id,
            "user_name": user_obj.name if user_obj else "Unknown",
            "score": sub.score,
            "submitted_at": sub.submitted_at
        })

    return result
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas

router = APIRouter(prefix="/submit", tags=["Exam Submission"])

@router.get("/")
def get_my_submissions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get all submissions for the current user"""
    submissions = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.user_id == user["user_id"]
    ).all()
    
    return [{
        "id": sub.id,
        "exam_id": sub.exam_id,
        "score": sub.score,
        "submitted_at": sub.submitted_at.isoformat()
    } for sub in submissions]

@router.post("/")
def submit_exam(
    data: schemas.ExamSubmit,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # 🔒 Role check
    if user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can submit exams")

    # 📝 Create submission
    submission = models.ExamSubmission(
        exam_id=data.exam_id,
        user_id=user["user_id"]
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    score = 0
    total_mcq = 0

    # 📊 Process answers
    for ans in data.answers:
        question = db.query(models.Question).filter(
            models.Question.id == ans.question_id
        ).first()

        if not question:
            continue

        # Auto-grading for MCQs
        if question.is_mcq:
            total_mcq += 1
            if (
                question.correct_answer
                and ans.answer_text.strip().lower()
                == question.correct_answer.strip().lower()
            ):
                score += 1

        db.add(models.Answer(
            submission_id=submission.id,
            question_id=ans.question_id,
            answer_text=ans.answer_text
        ))

    # 🧮 Final score
    if total_mcq > 0:
        submission.score = (score / total_mcq) * 100

    db.commit()

    return {
        "message": "Exam submitted & auto-graded",
        "submission_id": submission.id,
        "score": submission.score
    }

@router.get("/{submission_id}")
def get_submission_results(
    submission_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Get submission
    submission = db.query(models.ExamSubmission).filter(
        models.ExamSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Verify ownership (students can only see their own)
    if user["role"] == "student" and submission.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get exam details
    exam = db.query(models.Exam).filter(models.Exam.id == submission.exam_id).first()
    
    # Get all answers with questions
    answers = db.query(models.Answer).filter(
        models.Answer.submission_id == submission_id
    ).all()
    
    results = []
    for answer in answers:
        question = db.query(models.Question).filter(
            models.Question.id == answer.question_id
        ).first()
        
        if question:
            is_correct = False
            if question.is_mcq and question.correct_answer:
                is_correct = (
                    answer.answer_text.strip().lower() 
                    == question.correct_answer.strip().lower()
                )
            
            results.append({
                "question_id": question.id,
                "question_text": question.text,
                "your_answer": answer.answer_text,
                "correct_answer": question.correct_answer,
                "is_mcq": question.is_mcq,
                "is_correct": is_correct
            })
    
    return {
        "submission_id": submission.id,
        "exam_title": exam.title if exam else "Unknown Exam",
        "score": submission.score,
        "submitted_at": submission.submitted_at.isoformat(),
        "results": results
    }


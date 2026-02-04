from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
import os
from sqlalchemy.orm import Session
from collections import defaultdict
import cv2
import numpy as np
import time

from app.database import get_db
from app.dependencies import get_current_user
from app import models_proctor

router = APIRouter(prefix="/proctor", tags=["Proctoring"])

# Feature flag to disable server-side proctoring for lightweight deployments
PROCTOR_ENABLED = os.getenv("PROCTOR_ENABLED", "1") == "1"

# ===================== STATE =====================
proctor_state = defaultdict(lambda: {
    "no_face_since": None,
    "multi_face_count": 0,
    "dark_frame_count": 0,
    "low_motion_streak": 0,
    "blur_streak": 0,
    "total_violations": 0
})

last_frame_time = defaultdict(lambda: 0)
previous_frames = {}

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ===================== CONFIDENCE SCORE CONFIG =====================
VIOLATION_PENALTY = {
    "TAB_SWITCH": 5,
    "WINDOW_BLUR": 5,
    "RIGHT_CLICK": 5,
    "LEFT_SEAT": 15,
    "MULTIPLE_FACES": 20,
    "CAMERA_COVERED": 20,
    "SPOOF_ATTACK": 30,
}

# ===================== IMAGE METRICS =====================
def _brightness(img):
    return float(img.mean())


def _motion_score(session_id, gray):
    prev = previous_frames.get(session_id)
    previous_frames[session_id] = gray
    if prev is None:
        return 255.0
    diff = cv2.absdiff(prev, gray)
    return float(diff.mean())


def _blur_score(gray):
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def detect_spoof(session_id, gray, state):
    motion = _motion_score(session_id, gray)
    blur = _blur_score(gray)

    # Low motion or very blurry frames over consecutive checks indicate static replay
    if motion < 0.5:
        state["low_motion_streak"] += 1
    else:
        state["low_motion_streak"] = 0

    if blur < 15:
        state["blur_streak"] += 1
    else:
        state["blur_streak"] = 0

    return state["low_motion_streak"] >= 5 or state["blur_streak"] >= 5


# ===================== START SESSION =====================
@router.post("/start")
async def start_proctor_session(
    exam_id: int = Form(...),
    frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not PROCTOR_ENABLED:
        raise HTTPException(501, "Proctoring disabled on this deployment")
    data = await frame.read()
    if not data:
        raise HTTPException(400, "Empty frame")

    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(400, "Invalid image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))

    if len(faces) == 0:
        raise HTTPException(400, "Face not detected. Please ensure your face is visible and the room is well-lit.")

    session = models_proctor.ProctorSession(
        exam_id=exam_id,
        user_id=user["user_id"],
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    proctor_state.pop(session.id, None)
    previous_frames.pop(session.id, None)
    last_frame_time.pop(session.id, None)

    return {"session_id": session.id}


# ===================== ANALYZE FRAME =====================
@router.post("/frame")
async def analyze_frame(
    session_id: int = Form(...),
    frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if not PROCTOR_ENABLED:
        raise HTTPException(501, "Proctoring disabled on this deployment")
    session = db.query(models_proctor.ProctorSession).filter(
        models_proctor.ProctorSession.id == session_id,
        models_proctor.ProctorSession.user_id == user["user_id"]
    ).first()

    if not session:
        raise HTTPException(404, "Invalid session")

    now = time.time()
    if now - last_frame_time[session_id] < 2:
        return {"status": "SKIPPED"}
    last_frame_time[session_id] = now

    data = await frame.read()
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        return {"violation": "INVALID_FRAME"}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))
    faces_count = len(faces)

    state = proctor_state[session_id]
    violation = None

    brightness = _brightness(img)
    if brightness < 10:
        state["dark_frame_count"] += 1
        if state["dark_frame_count"] >= 5:
            violation = "CAMERA_COVERED"
    else:
        state["dark_frame_count"] = 0

    # No face
    if faces_count == 0:
        if state["no_face_since"] is None:
            state["no_face_since"] = now
        elif now - state["no_face_since"] >= 15:
            violation = "LEFT_SEAT"
    else:
        state["no_face_since"] = None

    # Multiple faces
    if faces_count > 1:
        state["multi_face_count"] += 1
        if state["multi_face_count"] >= 4:
            violation = "MULTIPLE_FACES"
    else:
        state["multi_face_count"] = 0

    # Spoof detection using motion + blur streaks
    if detect_spoof(session_id, gray, state):
        violation = "SPOOF_ATTACK"
        state["total_violations"] += 2

    if violation:
        state["total_violations"] += 1
        db.add(models_proctor.ProctorViolation(
            session_id=session.id,
            violation_type=violation
        ))
        db.commit()

    return {
        "faces_detected": faces_count,
        "violation": violation,
        "total_violations": state["total_violations"]
    }


# ===================== CONFIDENCE SCORE ENDPOINT =====================
@router.get("/confidence/{exam_id}")
def get_proctor_confidence(
    exam_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    session = db.query(models_proctor.ProctorSession).filter(
        models_proctor.ProctorSession.exam_id == exam_id,
        models_proctor.ProctorSession.user_id == user["user_id"]
    ).first()

    if not session:
        raise HTTPException(404, "Proctor session not found")

    violations = db.query(models_proctor.ProctorViolation).filter(
        models_proctor.ProctorViolation.session_id == session.id
    ).all()

    score = 100
    breakdown = []

    for v in violations:
        penalty = VIOLATION_PENALTY.get(v.violation_type, 5)
        score -= penalty
        breakdown.append({
            "type": v.violation_type,
            "penalty": penalty
        })

    score = max(0, min(100, score))

    return {
        "confidence_score": score,
        "total_violations": len(violations),
        "violations": breakdown
    }

@router.get("/admin/report/{exam_id}")
def admin_exam_report(
    exam_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    if user["role"] != "admin":
        raise HTTPException(403, "Admin only")

    sessions = db.query(models_proctor.ProctorSession).filter(
        models_proctor.ProctorSession.exam_id == exam_id
    ).all()

    report = []

    for session in sessions:
        violations = db.query(models_proctor.ProctorViolation).filter(
            models_proctor.ProctorViolation.session_id == session.id
        ).all()

        score = 100
        for v in violations:
            score -= VIOLATION_PENALTY.get(v.violation_type, 5)

        score = max(0, min(100, score))

        report.append({
            "user_id": session.user_id,
            "confidence_score": score,
            "total_violations": len(violations),
            "violations": [v.violation_type for v in violations],
        })

    return report


# ===================== LOG EVENTS =====================
@router.post("/event")
def record_event(payload: dict, user=Depends(get_current_user)):
    print("PROCTOR EVENT:", payload)
    return {"status": "logged"}

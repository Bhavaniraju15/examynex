from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import models_proctor

import cv2
import numpy as np
import time
from collections import defaultdict
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import FileResponse
import tempfile
import os

router = APIRouter(prefix="/proctor", tags=["Proctoring"])

# ===================== GLOBAL STATE =====================
proctor_state = defaultdict(lambda: {
    "no_face_since": None,
    "multi_face_count": 0,
    "dark_frame_count": 0,
    "total_violations": 0,
    "identity_check_count": 0,
    "ref_face_area": None,
})

last_frame_time = defaultdict(lambda: 0)
previous_frames = {}

# ===================== FACE DETECTOR =====================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ===================== UTILS =====================
def decode_image(file: UploadFile):
    img = cv2.imdecode(
        np.frombuffer(file, np.uint8),
        cv2.IMREAD_COLOR
    )
    return img

def detect_faces(gray):
    return face_cascade.detectMultiScale(gray, 1.3, 5)

# ===================== SPOOF DETECTION =====================
def detect_spoof(session_id, gray):
    prev = previous_frames.get(session_id)
    previous_frames[session_id] = gray

    if prev is None:
        return False

    diff = cv2.absdiff(prev, gray)
    motion_score = diff.mean()

    # Very low motion → printed photo / replay
    return motion_score < 1.5

# ===================== START SESSION =====================
@router.post("/start")
async def start_proctor_session(
    exam_id: int = Form(...),
    frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    img = decode_image(await frame.read())
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray)

    if len(faces) != 1:
        raise HTTPException(status_code=400, detail="Exactly one face required")

    x, y, w, h = faces[0]
    face_area = w * h

    session = models_proctor.ProctorSession(
        exam_id=exam_id,
        user_id=user["user_id"]
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    proctor_state[session.id]["ref_face_area"] = face_area

    # Reset memory
    previous_frames.pop(session.id, None)
    last_frame_time.pop(session.id, None)

    return {
        "session_id": session.id,
        "message": "Proctoring started"
    }

# ===================== ANALYZE FRAME =====================
@router.post("/frame")
async def analyze_frame(
    session_id: int,
    frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    session = db.query(models_proctor.ProctorSession).filter(
        models_proctor.ProctorSession.id == session_id,
        models_proctor.ProctorSession.user_id == user["user_id"]
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    now = time.time()
    if now - last_frame_time[session_id] < 2:
        return {"status": "SKIPPED"}
    last_frame_time[session_id] = now

    state = proctor_state[session_id]
    violation = None
    action = None

    img = decode_image(await frame.read())
    if img is None:
        return {"faces_detected": 0, "violation": "INVALID_FRAME"}

    small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(gray)
    faces_count = len(faces)

    # CAMERA COVERED
    if img.mean() < 30:
        state["dark_frame_count"] += 1
        if state["dark_frame_count"] >= 3:
            violation = "CAMERA_COVERED"
    else:
        state["dark_frame_count"] = 0

    # NO FACE
    if faces_count == 0:
        if state["no_face_since"] is None:
            state["no_face_since"] = now
        elif now - state["no_face_since"] >= 10:
            violation = "LEFT_SEAT"
    else:
        state["no_face_since"] = None

    # MULTIPLE FACES
    if faces_count > 1:
        state["multi_face_count"] += 1
        if state["multi_face_count"] >= 3:
            violation = "MULTIPLE_FACES"
    else:
        state["multi_face_count"] = 0

    # IDENTITY CONSISTENCY CHECK
    if faces_count == 1:
        x, y, w, h = faces[0]
        area = w * h
        ref_area = state["ref_face_area"]

        if ref_area:
            diff_ratio = abs(area - ref_area) / ref_area
            if diff_ratio > 0.6:
                violation = "IMPERSONATION"

    # ANTI-SPOOF
    if detect_spoof(session_id, gray):
        violation = "SPOOF_ATTACK"

    # ESCALATION
    if violation:
        state["total_violations"] += 1

        db.add(models_proctor.ProctorViolation(
            session_id=session.id,
            violation_type=violation
        ))
        db.commit()

        if state["total_violations"] >= 5:
            action = "TERMINATE_EXAM"
        elif state["total_violations"] >= 3:
            action = "FINAL_WARNING"
        else:
            action = "WARNING"

        if action == "TERMINATE_EXAM":
            proctor_state.pop(session_id, None)
            previous_frames.pop(session_id, None)
            last_frame_time.pop(session_id, None)

    return {
        "faces_detected": faces_count,
        "violation": violation,
        "total_violations": state["total_violations"],
        "action": action
    }

# ===================== AUDIO =====================
@router.post("/audio")
async def audio_violation(
    session_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    state = proctor_state[session_id]
    state["total_violations"] += 1

    db.add(models_proctor.ProctorViolation(
        session_id=session_id,
        violation_type="TALKING_DETECTED"
    ))
    db.commit()

    action = "WARNING"
    if state["total_violations"] >= 5:
        action = "TERMINATE_EXAM"
    elif state["total_violations"] >= 3:
        action = "FINAL_WARNING"

    return {"status": "LOGGED", "action": action}

# ===================== UI EVENTS =====================
@router.post("/ui")
async def ui_violation(
    session_id: int,
    violation: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    state = proctor_state[session_id]
    state["total_violations"] += 1

    db.add(models_proctor.ProctorViolation(
        session_id=session_id,
        violation_type=violation
    ))
    db.commit()

    action = "WARNING"
    if state["total_violations"] >= 5:
        action = "TERMINATE_EXAM"
    elif state["total_violations"] >= 3:
        action = "FINAL_WARNING"

    return {"status": "LOGGED", "action": action}

# ===================== PDF REPORT =====================
@router.get("/report/{session_id}/pdf")
def generate_report(session_id: int, db: Session = Depends(get_db)):
    violations = db.query(models_proctor.ProctorViolation).filter(
        models_proctor.ProctorViolation.session_id == session_id
    ).all()

    pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(pdf.name, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Proctoring Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Session ID: {session_id}")
    c.drawString(50, height - 100, f"Total Violations: {len(violations)}")

    y = height - 140
    for v in violations:
        c.drawString(50, y, f"- {v.timestamp} : {v.violation_type}")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    pdf.close()

    return FileResponse(
        pdf.name,
        media_type="application/pdf",
        filename=f"proctor_report_{session_id}.pdf"
    )

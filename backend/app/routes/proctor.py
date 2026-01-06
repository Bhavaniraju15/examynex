from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app import models_proctor

import cv2
import numpy as np
import face_recognition
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
    "identity_check_count": 0
})

# 🔥 FPS + MEMORY CONTROL
last_frame_time = defaultdict(lambda: 0)

# 🔥 STEP 9: Anti-spoof memory
previous_frames = {}

# ===================== FACE DETECTOR =====================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# ===================== FACE UTILS =====================
def extract_face_embedding(image):
    rgb = image[:, :, ::-1]
    encodings = face_recognition.face_encodings(rgb)
    return encodings[0] if encodings else None

def is_same_person(ref, live, threshold=0.6):
    distance = np.linalg.norm(ref - live)
    return distance < threshold, distance

# ===================== STEP 9: SPOOF DETECTION =====================
def detect_spoof(session_id, gray):
    prev = previous_frames.get(session_id)
    previous_frames[session_id] = gray

    if prev is None:
        return False

    diff = cv2.absdiff(prev, gray)
    motion_score = diff.mean()

    # 🔥 Very low motion = printed photo / replay
    return motion_score < 1.5

# ===================== START SESSION =====================
@router.post("/start")
async def start_proctor_session(
    exam_id: int = Form(...),
    frame: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    img = cv2.imdecode(
        np.frombuffer(await frame.read(), np.uint8),
        cv2.IMREAD_COLOR
    )

    embedding = extract_face_embedding(img)
    if embedding is None:
        raise HTTPException(status_code=400, detail="Face not detected")

    session = models_proctor.ProctorSession(
        exam_id=exam_id,
        user_id=user["user_id"],
        face_embedding=embedding.tobytes()
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # 🔥 MEMORY RESET
    proctor_state.pop(session.id, None)
    previous_frames.pop(session.id, None)
    last_frame_time.pop(session.id, None)

    return {
        "session_id": session.id,
        "message": "Proctoring started with identity verification"
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

    # 🔥 FPS LIMIT (1 frame / 2 sec)
    now = time.time()
    if now - last_frame_time[session_id] < 2:
        return {"status": "SKIPPED"}
    last_frame_time[session_id] = now

    state = proctor_state[session_id]
    violation = None
    action = None

    img = cv2.imdecode(
        np.frombuffer(await frame.read(), np.uint8),
        cv2.IMREAD_COLOR
    )

    if img is None:
        return {"faces_detected": 0, "violation": "INVALID_FRAME"}

    # 🔥 CPU OPTIMIZATION (resize)
    small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    faces_count = len(faces)

    # -------- CAMERA COVERED --------
    if img.mean() < 30:
        state["dark_frame_count"] += 1
        if state["dark_frame_count"] >= 3:
            violation = "CAMERA_COVERED"
    else:
        state["dark_frame_count"] = 0

    # -------- NO FACE --------
    if faces_count == 0:
        if state["no_face_since"] is None:
            state["no_face_since"] = now
        elif now - state["no_face_since"] >= 10:
            violation = "LEFT_SEAT"
    else:
        state["no_face_since"] = None

    # -------- MULTIPLE FACES --------
    if faces_count > 1:
        state["multi_face_count"] += 1
        if state["multi_face_count"] >= 3:
            violation = "MULTIPLE_FACES"
    else:
        state["multi_face_count"] = 0

    # -------- FACE IDENTITY (EVERY 5 FRAMES ONLY) --------
    state["identity_check_count"] += 1
    if state["identity_check_count"] % 5 == 0:
        ref = np.frombuffer(session.face_embedding, dtype=np.float64)
        live = extract_face_embedding(img)

        if live is not None:
            same, _ = is_same_person(ref, live)
            if not same:
                violation = "IMPERSONATION"
                state["total_violations"] += 2

    # -------- ANTI-SPOOF --------
    if detect_spoof(session_id, gray):
        violation = "SPOOF_ATTACK"
        state["total_violations"] += 2

    # -------- ESCALATION --------
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

        # 🔥 MEMORY CLEANUP ON TERMINATION
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


# ===================== AUDIO MONITORING =====================
@router.post("/audio")
async def audio_violation(
    session_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    session = db.query(models_proctor.ProctorSession).filter(
        models_proctor.ProctorSession.id == session_id,
        models_proctor.ProctorSession.user_id == user["user_id"]
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    state = proctor_state[session_id]
    state["total_violations"] += 1

    db.add(models_proctor.ProctorViolation(
        session_id=session.id,
        violation_type="TALKING_DETECTED"
    ))
    db.commit()

    action = "WARNING"
    if state["total_violations"] >= 5:
        action = "TERMINATE_EXAM"
    elif state["total_violations"] >= 3:
        action = "FINAL_WARNING"

    if action == "TERMINATE_EXAM":
        proctor_state.pop(session_id, None)
        last_frame_time.pop(session_id, None)

    return {"status": "LOGGED", "action": action}


# ===================== UI / BROWSER MONITORING =====================
@router.post("/ui")
async def ui_violation(
    session_id: int,
    violation: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    session = db.query(models_proctor.ProctorSession).filter(
        models_proctor.ProctorSession.id == session_id,
        models_proctor.ProctorSession.user_id == user["user_id"]
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    state = proctor_state[session_id]
    state["total_violations"] += 1

    db.add(models_proctor.ProctorViolation(
        session_id=session.id,
        violation_type=violation
    ))
    db.commit()

    action = "WARNING"
    if state["total_violations"] >= 5:
        action = "TERMINATE_EXAM"
    elif state["total_violations"] >= 3:
        action = "FINAL_WARNING"

    if action == "TERMINATE_EXAM":
        proctor_state.pop(session_id, None)
        last_frame_time.pop(session_id, None)

    return {"status": "LOGGED", "action": action}


# ===================== REPORT GENERATION =====================
@router.get("/report/{session_id}/pdf")
def generate_report(
    session_id: int,
    db: Session = Depends(get_db)
):
    session = db.query(models_proctor.ProctorSession).filter(
        models_proctor.ProctorSession.id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    violations = db.query(models_proctor.ProctorViolation).filter(
        models_proctor.ProctorViolation.session_id == session_id
    ).all()

    # Create PDF
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(pdf_file.name, pagesize=letter)
    width, height = letter

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Proctoring Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Session ID: {session_id}")
    c.drawString(50, height - 100, f"Total Violations: {len(violations)}")

    y = height - 140
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Violation Log:")
    
    c.setFont("Helvetica", 10)
    y -= 20

    for v in violations:
        c.drawString(50, y, f"- {v.timestamp}: {v.violation_type}")
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    pdf_file.close()

    return FileResponse(
        pdf_file.name, 
        media_type="application/pdf", 
        filename=f"proctor_report_{session_id}.pdf"
    )

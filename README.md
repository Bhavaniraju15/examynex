# 🚀 Examynex

### AI-Powered Online Examination System with Real-Time Proctoring

**Examynex** is an AI-driven online examination platform designed to ensure exam integrity through real-time **webcam**, **microphone**, and **user activity** monitoring.
It detects suspicious behavior such as impersonation, talking, tab switching, and leaving the exam environment—making online exams **secure, reliable, and scalable**.



## 📌 Key Highlights

* Real-time AI-based proctoring
* Secure role-based authentication
* Automated violation detection & escalation
* Admin live monitoring dashboard
* Detailed post-exam proctoring reports

---

## ✨ Features

### 🎥 Webcam Proctoring

* Face detection using OpenCV
* Multiple face detection
* Left-seat detection
* Camera covered detection
* Identity verification (anti-impersonation)

### 🎙️ Audio Monitoring

* Real-time microphone monitoring
* Talking detection during exams

### 🖥️ Browser & UI Monitoring

* Tab switch detection
* Window blur detection
* Fullscreen exit detection

### ⚠️ Violation Escalation System

* Progressive warnings
* Final warning mechanism
* Automatic exam termination after repeated violations

### 📄 Proctoring Reports

* Detailed violation logs
* Auto-generated reports
* Cheating score & risk-level assessment

### 🔐 Secure Backend

* JWT-based authentication
* Role-based access (Admin / Student)
* HTTPS-ready deployment
* WebSocket support for real-time admin monitoring

---

## 🛠️ Tech Stack

### Backend

* **FastAPI**
* **Python**
* **SQLAlchemy**
* **SQLite / PostgreSQL**
* **JWT Authentication**

### AI & Computer Vision

* **OpenCV**
* **face_recognition**
* **NumPy**

### Real-Time Communication

* **WebSockets**

### Frontend

* HTML, CSS, JavaScript
* Browser APIs (Webcam, Microphone, Fullscreen)

### Deployment

* Render (Free Tier)
* Railway / Docker
* Cloudflare Tunnel (for HTTPS webcam & mic access)

---

## 📂 Project Structure

```text
examynex/
├── Documentation & Config Files/
│   ├── ARCHITECTURE.md
│   ├── PROJECT_OVERVIEW.md
│   ├── SETUP_GUIDE.md
│   ├── STARTUP_GUIDE.md
│   ├── QUICKSTART.md
│   ├── docker-compose.yml
│   └── render.yaml
│
├── .github/
│   └── copilot-instructions.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── start_server.sh
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── models.py
│       ├── schemas.py
│       ├── routes/
│       │   ├── user.py
│       │   ├── exam.py
│       │   ├── question.py
│       │   ├── submission.py
│       │   └── proctor.py
│       └── services/
│           └── face_utils.py
│
└── frontend/
    ├── index.html
    ├── login.html
    ├── register.html
    ├── admin-dashboard.html
    ├── exam-taking.html
    ├── student-dashboard.html
    └── styles.css
```

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/hima-manikanta/examynex.git
cd examynex
```

### 2️⃣ Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3️⃣ Frontend

Open `frontend/index.html` in a browser
(or serve using Live Server / any static server)

---

## 🔐 Authentication & Roles

* **Admin**: Create exams, monitor students live, view reports
* **Student**: Take exams under AI proctoring

---

## 📊 Use Cases

* Online universities & colleges
* Certification platforms
* Remote hiring assessments
* Secure online quizzes & tests

---

## 🧠 Future Enhancements

* Emotion & gaze tracking
* AI-based cheating score prediction
* Cloud-based video evidence storage
* Mobile support

---

## 👨‍💻 Author

**Manu (Hima Manikanta Vasamsetti)**
Final Year B.Tech – CSE (AI & ML)

---

## 📜 License

This project is for **academic & learning purposes**.
Feel free to fork and enhance.

---
## links
-  backend: https://examynex-backend.up.railway.app/
-  frontend: https://bvcexamynex.netlify.app/

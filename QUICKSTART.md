# Examynex Setup & Run Guide

## 📋 Prerequisites
- Python 3.8+ (for backend)
- Node.js 18+ (for frontend)
- Git (optional)

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create and activate virtual environment:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirments.txt
```

4. **Run FastAPI server:**
```bash
uvicorn app.main:app --reload
```
Backend runs on: `http://localhost:8000`
API docs available at: `http://localhost:8000/docs`

---

### Frontend Setup

1. **Navigate to frontend directory (in a new terminal):**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Configure backend URL (optional):**
Edit `.env.local`:
```bash
# For local development:
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# For remote development:
# NEXT_PUBLIC_BACKEND_URL=http://192.168.31.72:8000
```

4. **Run development server:**
```bash
npm run dev
```
Frontend runs on: `http://localhost:3000`

---

## 🎯 Usage

### 1. Register Account
- Navigate to `http://localhost:3000/register`
- Enter email, password, select role (Student or Admin)
- Click "Register"

### 2. Login
- Navigate to `http://localhost:3000/login`
- Enter credentials
- **Admins** are redirected to `/admin`
- **Students** are redirected to `/dashboard`

### 3. Admin: Create Exam
- Go to Admin Dashboard (`/admin`)
- Click "Create New Exam"
- Fill in title, description, duration (minutes)
- Click "Create Exam"

### 4. Admin: Add Questions
- Use API or create UI for adding questions to exams
- Questions need: text, is_mcq (true/false), correct_answer (for MCQ)

### 5. Student: Take Exam
- Go to Dashboard (`/dashboard`)
- Click "Start Exam" on desired exam
- Answer questions (answers auto-save)
- Click "Submit Exam" when done
- View score immediately

---

## 📡 API Endpoints

### Authentication
- `POST /users/register` - Register new user
- `POST /users/login` - Login and get JWT token

### Exams
- `GET /exams` - List all exams
- `POST /exams` - Create exam (admin only)

### Questions
- `GET /questions/{exam_id}` - Get questions for exam
- `POST /questions` - Add question (admin only)

### Submissions
- `POST /submissions/answer` - Save answer
- `POST /submissions/submit` - Submit and grade exam
- `GET /submissions/{submission_id}` - Get submission score

### Proctoring (Future)
- `POST /proctor/start` - Start proctoring session
- `POST /proctor/frame` - Upload webcam frame
- `WS /ws/admin` - WebSocket admin monitoring

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Clear database and restart
rm exam.db
uvicorn app.main:app --reload
```

### CORS errors
Make sure backend and frontend URLs are configured correctly in:
- Frontend: `.env.local` - `NEXT_PUBLIC_BACKEND_URL`
- Backend: `app/main.py` - CORS allow_origins

### Questions not loading
- Ensure questions were created via `/questions` endpoint
- Check exam_id is correct
- Verify token is valid (not expired)

### Answers not saving
- Check browser console for errors
- Verify submission exists (created via first answer)
- Check token authorization

---

## 🗄️ Database

SQLite database is stored at: `backend/exam.db`

To reset database:
```bash
cd backend
rm exam.db
python -c "from app.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

---

## 📝 Key Features Implemented

✅ User registration & login with JWT
✅ Role-based access (Admin/Student)
✅ Exam creation & management
✅ Question bank system
✅ Real-time answer saving
✅ Auto-grading for MCQ
✅ Submission tracking
✅ Responsive UI with Tailwind CSS
✅ Configurable backend URL
✅ CORS support for cross-origin requests

---

## 🚧 Next Steps

- [ ] Add question editing/deletion for admins
- [ ] Implement webcam proctoring UI
- [ ] Add real-time proctor monitoring dashboard
- [ ] Generate PDF reports
- [ ] Add user activity logs
- [ ] Implement exam timer with warnings

---

## 📞 Support

For issues or questions:
1. Check the API docs at `http://localhost:8000/docs`
2. Review console logs in browser (F12)
3. Check backend terminal for errors
4. Verify `.env.local` configuration

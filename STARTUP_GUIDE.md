# ExamyNex - Complete Startup & Testing Guide

## Changes Made in This Session

### Backend Updates
1. ✅ **Password Hashing Fixed**: Switched from bcrypt to pbkdf2_sha256 to fix 72-byte password limit and backend version errors
   - File: [backend/app/auth.py](backend/app/auth.py)

2. ✅ **Proctor Frame Detection Improved**: Added motion, blur, and brightness metrics for better spoof detection
   - File: [backend/app/routes/proctor.py](backend/app/routes/proctor.py)
   - Detects: Low-motion replays, heavy blur, dark camera covers

3. ✅ **User Model Updated**: Added `name` field to User table
   - File: [backend/app/models.py](backend/app/models.py)
   - Includes: id, name, email, password, role

4. ✅ **Auth Routes Updated**: `/auth/register` now captures user name
   - File: [backend/app/routes/user.py](backend/app/routes/user.py)
   - Schemas: `UserCreate` (with name), `UserOut` (with name)

5. ✅ **Admin Endpoints Added**:
   - `GET /submissions/admin/all` - List all submissions
   - `GET /submissions/admin/exam/{exam_id}` - List submissions per exam
   - `PUT /exams/{exam_id}` - Update exam
   - `DELETE /exams/{exam_id}` - Delete exam
   - `PUT /questions/{question_id}` - Update question
   - `DELETE /questions/{question_id}` - Delete question

---

## Step-by-Step Startup Guide

### 1. Reset Database (Fresh Start)
Since we added a new `name` column to users, delete the old database:

**Windows (PowerShell):**
```powershell
cd c:\Users\himam\Desktop\examynex\backend
Remove-Item exam.db -ErrorAction SilentlyContinue
```

**macOS/Linux:**
```bash
cd ~/Desktop/examynex/backend
rm -f exam.db
```

### 2. Start Backend Server

**Windows (PowerShell):**
```powershell
cd c:\Users\himam\Desktop\examynex\backend
.\#\Scripts\activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 3. Start Frontend Server

**Option A: Using Live Server (VS Code)**
- Install "Live Server" extension
- Right-click `frontend/index.html` → Open with Live Server
- URL: http://127.0.0.1:5500

**Option B: Using Python**
```powershell
cd c:\Users\himam\Desktop\examynex\frontend
python -m http.server 8080
```
- URL: http://localhost:8080

**Option C: Using Node.js**
```bash
cd frontend
npx http-server -p 8080
```

---

## Testing Checklist

### Authentication
- [ ] **Register** with name, email, password
  - URL: http://localhost:5500/register.html
  - Test: Valid name (2+ chars), valid email, password (8+ chars)
  - Expected: Redirect to login

- [ ] **Login** with credentials
  - URL: http://localhost:5500/login.html
  - Expected: Store token in localStorage, redirect to dashboard

- [ ] **Get Current User** (/users/me)
  - Expected: Return user name, email, role

### Exams (Admin Flow)
- [ ] **Create Exam** (admin-create-exam.html)
  - Title, description, duration
  - Expected: Exam appears in student dashboard

- [ ] **Add Questions** (admin-add-question.html)
  - Select exam, add MCQ question (4 options, 1 correct)
  - Expected: Question saves successfully

- [ ] **Update Question** (new endpoint)
  - PUT /questions/{question_id} with updated text
  - Expected: Question text changes

- [ ] **Delete Question** (new endpoint)
  - DELETE /questions/{question_id}
  - Expected: Question removed

- [ ] **Update Exam** (new endpoint)
  - PUT /exams/{exam_id} with new title/duration
  - Expected: Exam details update

- [ ] **Delete Exam** (new endpoint)
  - DELETE /exams/{exam_id}
  - Expected: Exam removed from list

### Exams (Student Flow)
- [ ] **List Exams** (student-dashboard.html)
  - Login as student
  - Expected: See all available exams

- [ ] **Start Exam** (exam-taking.html)
  - Click exam card
  - Expected: Questions load, timer starts

- [ ] **Answer Questions**
  - Select MCQ options
  - Expected: Auto-saved after 2 seconds

- [ ] **Submit Exam**
  - Click submit button
  - Expected: Score calculated, redirect to results

- [ ] **View Results** (exam-results.html)
  - Expected: Show score, violations, confidence

### Proctoring
- [ ] **Start Proctor Session**
  - Exam page → Webcam capture
  - POST /proctor/start
  - Expected: Face detected, session created

- [ ] **Frame Analysis**
  - Send frames while taking exam
  - POST /proctor/frame
  - Expected: Check for violations

- [ ] **Detect Violations**
  - Cover camera → CAMERA_COVERED violation
  - Look away → LEFT_SEAT violation (10s timeout)
  - Multiple faces → MULTIPLE_FACES violation
  - Expected: Violations logged in database

- [ ] **Confidence Score**
  - GET /proctor/confidence/{exam_id}
  - Expected: Score 0-100 based on violations

### Admin Features
- [ ] **Admin Dashboard** (admin-dashboard.html)
  - Links to create exam, add question, monitor, submissions
  
- [ ] **Live Monitor** (admin-monitor.html)
  - WebSocket connection to /ws/admin
  - Expected: Real-time exam sessions

- [ ] **View Submissions** (admin-submissions.html)
  - GET /submissions/admin/all
  - Expected: List all submitted exams with scores

- [ ] **Proctor Report** (/proctor/admin/report/{exam_id})
  - Expected: Violations breakdown per student

### User Profiles
- [ ] **Student Profile** (student-profile.html)
  - GET /users/me
  - Expected: Show name, email, role

- [ ] **Update Profile** (if implemented)
  - PUT /users/me with new name
  - Expected: Profile updates

---

## API Documentation

### Base URL
- Backend: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Key Endpoints

#### Authentication
```
POST /auth/register
POST /auth/login
GET  /users/me
```

#### Exams
```
POST /exams/
GET  /exams/
GET  /exams/{exam_id}
PUT  /exams/{exam_id}          (NEW)
DELETE /exams/{exam_id}        (NEW)
GET  /exams/{exam_id}/questions
POST /exams/{exam_id}/start
```

#### Questions
```
POST /questions/
GET  /questions/{exam_id}
PUT  /questions/{question_id}  (NEW)
DELETE /questions/{question_id}(NEW)
```

#### Submissions
```
POST /submissions/answer
POST /submissions/submit
GET  /submissions/{exam_id}/result
GET  /submissions/admin/all      (NEW)
GET  /submissions/admin/exam/{exam_id} (NEW)
```

#### Proctoring
```
POST /proctor/start
POST /proctor/frame
GET  /proctor/confidence/{exam_id}
GET  /proctor/admin/report/{exam_id}
WS   /ws/admin
```

---

## Database Tables

```sql
-- Users
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  name VARCHAR NOT NULL,        -- NEW FIELD
  email VARCHAR UNIQUE NOT NULL,
  password VARCHAR NOT NULL,
  role VARCHAR DEFAULT 'student'
);

-- Exams
CREATE TABLE exams (
  id INTEGER PRIMARY KEY,
  title VARCHAR NOT NULL,
  description VARCHAR NOT NULL,
  duration_minutes INTEGER DEFAULT 60
);

-- Questions
CREATE TABLE questions (
  id INTEGER PRIMARY KEY,
  exam_id INTEGER FOREIGN KEY,
  text VARCHAR NOT NULL,
  question_type VARCHAR NOT NULL,
  option_a VARCHAR, option_b VARCHAR, option_c VARCHAR, option_d VARCHAR,
  correct_answer VARCHAR
);

-- Submissions
CREATE TABLE exam_submissions (
  id INTEGER PRIMARY KEY,
  exam_id INTEGER FOREIGN KEY,
  user_id INTEGER FOREIGN KEY,
  score FLOAT DEFAULT 0,
  is_finalized BOOLEAN DEFAULT FALSE,
  submitted_at DATETIME
);

-- Answers
CREATE TABLE answers (
  id INTEGER PRIMARY KEY,
  submission_id INTEGER FOREIGN KEY,
  question_id INTEGER FOREIGN KEY,
  answer_text VARCHAR,
  ai_score FLOAT
);

-- Proctor Sessions & Violations
CREATE TABLE proctor_sessions (...);
CREATE TABLE proctor_violations (...);
```

---

## Troubleshooting

### Backend Issues

**Error: ModuleNotFoundError: No module named 'app'**
- Solution: Run from `backend/` directory
- Verify `app/__init__.py` exists

**Error: password cannot be longer than 72 bytes**
- ✅ FIXED: Using pbkdf2_sha256 now (no 72-byte limit)

**Error: ImportError: cannot import name 'X'**
- Solution: Check all route imports in main.py
- Verify: `from app.routes import user, exam, question, submission, proctor`

**Database Locked**
- Solution: Delete `exam.db` and restart
- SQLite allows one writer; uvicorn reload might cause conflicts

### Frontend Issues

**CORS Error: Access denied**
- Check: Backend CORS origins in [backend/app/main.py](backend/app/main.py)
- Add: http://localhost:5500 if using Live Server
- Verify: Frontend URL matches CORS whitelist

**Token Not in LocalStorage**
- Check: Login endpoint returns `access_token`
- Verify: Token is stored: `localStorage.setItem('token', data.access_token)`

**404 on API Calls**
- Check: config.js BASE_URL = http://localhost:8000
- Verify: Endpoint exists and method is correct (GET vs POST)

**WebSocket Not Connecting**
- Check: Browser console for ws:// errors
- Verify: Backend WebSocket route: `@app.websocket("/ws/admin")`
- Check: Admin is connected before monitor page loads

---

## Configuration Files

### Frontend Config
File: [frontend/config.js](frontend/config.js)
```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:8000',  // Change if backend host differs
    ENDPOINTS: { ... }
};
```

### Backend Config
File: [backend/app/auth.py](backend/app/auth.py)
```python
SECRET_KEY = "examynex_super_secret_key"  # Change for production
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
```

### CORS Config
File: [backend/app/main.py](backend/app/main.py)
```python
allow_origins=[
    "http://localhost:5500",    # Live Server
    "http://127.0.0.1:8080",    # Python HTTP server
    ...
]
```

---

## Performance Tips

1. **Use Lazy Loading**: Frontend loads exams on demand
2. **Frame Rate**: Proctoring sends frames every 2 seconds (configurable)
3. **Database Indexes**: email, exam_id, user_id already indexed
4. **Caching**: Consider caching exam questions (won't change during exam)

---

## Security Notes

- ✅ Passwords hashed with pbkdf2_sha256
- ✅ JWT tokens with 24-hour expiry
- ✅ Role-based access control (admin-only endpoints)
- ✅ CORS configured to prevent cross-origin abuse
- ⚠️ TODO: Add rate limiting on auth endpoints
- ⚠️ TODO: Add HTTPS in production
- ⚠️ TODO: Use environment variables for SECRET_KEY

---

## Next Features to Add

1. User profile update endpoint (PUT /users/me)
2. Exam PDF export
3. Plagiarism detection for text answers
4. AI-powered answer grading (currently only MCQ)
5. Email notifications
6. Leaderboards
7. Question bank/categories
8. Time extension requests
9. Practice mode vs real exams
10. Analytics dashboard

---

## Support

**API Docs**: http://localhost:8000/docs (Swagger UI)
**Database**: SQLite at `backend/exam.db`
**Logs**: Console output from uvicorn

For detailed feature mapping, see [FEATURE_MAPPING.md](FEATURE_MAPPING.md)


# Examynex Architecture

## 1. System Overview
Examynex is an AI-assisted exam platform composed of two deployable services:

- **Backend (FastAPI + SQLAlchemy):** Exposes REST and WebSocket endpoints for authentication, exam and question management, exam submissions, and real-time proctoring events. Persistence relies on SQLite by default (upgradeable to PostgreSQL).
- **Frontend (Next.js App Router):** Provides the admin and student experiences, calling the backend through an Axios client with automatic bearer-token injection.
- **Realtime & Proctoring:** The backend maintains in-memory proctor session state, processes webcam frames with OpenCV, and relays status updates to connected admin dashboards over WebSockets.

## 2. Runtime Components
### Backend Service
- `app/main.py` boots FastAPI, configures CORS, registers REST routers, and exposes `/ws/admin` for admin monitoring.
- `app/database.py` defines the SQLAlchemy engine, `SessionLocal`, and declarative `Base` bound to `exam.db`.
- `app/models.py` contains relational tables for `User`, `Exam`, `Question`, `Submission`, and `Answer`. `models_proctor.py` extends this with `ProctorSession` and `ProctorViolation`.
- `app/schemas.py` carries the Pydantic models shared across routes, keeping request/response payloads consistent.
- `app/auth.py` handles password hashing (PBKDF2-SHA256), JWT creation, and validation utilities. `app/dependencies.py` turns these into FastAPI dependencies for role-aware access control.
- `app/routes/*.py` files encapsulate domain-specific routers (users, exams, questions, submissions, proctoring). Each endpoint follows the `Depends(get_db)` and `Depends(get_current_user)` patterns for DB sessions and auth.
- `app/services/face_utils.py` centralizes OpenCV helpers such as Haar cascade detection, spoof heuristics, and frame preprocessing.

### Frontend Web App
- `app/layout.tsx` defines the global shell, fonts, and metadata; `app/globals.css` applies Tailwind and custom tokens.
- `app/login`, `app/register` (to be implemented), and `app/dashboard` house the primary routes for authentication, admin dashboards, and student flows.
- Nested segments under `app/admin` and `app/exams` provide the multi-step UX for creating exams, browsing questions, and starting attempts.
- `components/` hosts shared UI widgets (`NavBar`, `TopNav`, `ExamCard`), while `hooks/useAuthGuard.ts` enforces client-side redirects based on auth state.
- `lib/api.ts` wraps Axios with a fixed `baseURL` (`http://192.168.31.72:8000`) and attaches JWT tokens from `localStorage`. `lib/auth.ts` abstracts token storage helpers.

### Persistence Layer
- SQLite database file `exam.db` resides in the backend root by default. Migrations are manual; schema evolves through SQLAlchemy models.
- ORM relationships:
  - `Exam` ←→ `Question` (one-to-many)
  - `Submission` ←→ `Answer` (one-to-many)
  - Proctor entities link sessions to submissions via foreign keys when violations are logged.

### Proctoring Pipeline
1. **Session Start:** `POST /proctor/start` creates a `ProctorSession`, caches it in memory, and responds with a session token.
2. **Frame Upload:** `POST /proctor/frame` accepts base64 frames, runs face detection, spoof checks, and seat-presence heuristics through OpenCV utilities.
3. **Escalation Logic:** Per-frame signals update a violation counter (warning → final warning → terminate). Violations are inserted into the DB and broadcast to admins via `/ws/admin`.
4. **Session Cleanup:** Termination removes the in-memory session entry to prevent stale state.

## 3. Request & Data Flows
### Authentication Flow
1. User registers via `POST /users/register`; passwords are hashed with PBKDF2-SHA256 before storage.
2. Login (`POST /users/login`) verifies credentials and issues a JWT containing `user_id` and `role`.
3. Frontend stores the token in `localStorage` and injects it through Axios interceptors for every protected call.
4. Backend dependencies decode the token, attach `CurrentUser` to the request, and enforce role checks (admin vs student).

### Exam Lifecycle
1. **Creation (Admin):** `POST /exams/` and `POST /questions/` build the exam catalog. There is currently no GET-by-exam question endpoint; frontend expectations may require adding `/questions/{exam_id}`.
2. **Listing:** `GET /exams/` returns available exams for both roles.
3. **Attempt (Student):** Frontend pages under `app/exams/[id]/start` and `app/exams/[id]/attempt` fetch exam metadata, render questions, and prepare submission payloads.

### Submission & Grading
1. `POST /submission/submit` accepts `{ exam_id, answers: [...] }`. Each answer references a `question_id` and the student's response.
2. Auto-grading currently supports MCQs only, using a case-insensitive string comparison between `Answer.response` and `Question.correct_answer`.
3. Scores are persisted on the `Submission` record; non-MCQ answers remain stored but ungraded.

### WebSocket Monitoring
- Admin panels connect to `ws://<backend>/ws/admin` to receive JSON payloads whenever the proctoring service detects a violation or status change.
- The backend maintains a shared list of active WebSocket connections and broadcasts to all listeners.

## 4. Code Organization Snapshot
```
examynex/
├─ backend/
│  ├─ app/
│  │  ├─ auth.py
│  │  ├─ database.py
│  │  ├─ dependencies.py
│  │  ├─ main.py
│  │  ├─ models.py
│  │  ├─ models_proctor.py
│  │  ├─ schemas.py
│  │  ├─ proctor.py
│  │  └─ routes/
│  │     ├─ user.py
│  │     ├─ exam.py
│  │     ├─ question.py
│  │     ├─ submission.py
│  │     └─ proctor.py
│  ├─ Dockerfile
│  └─ requirments.txt
├─ frontend/
│  ├─ app/
│  │  ├─ admin/
│  │  ├─ dashboard/
│  │  ├─ exams/
│  │  └─ login/
│  ├─ components/
│  ├─ hooks/
│  ├─ lib/
│  └─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
└─ README.md
```

## 5. Key Files Reference
- Backend entrypoint: `backend/app/main.py`
- Database/session wiring: `backend/app/database.py`
- Auth helpers: `backend/app/auth.py`
- Shared schemas: `backend/app/schemas.py`
- Proctor utilities: `backend/app/services/face_utils.py`
- Axios client & auth helpers: `frontend/lib/api.ts`, `frontend/lib/auth.ts`
- Shared UI components: `frontend/components/`

## 6. Deployment & Ops Notes
- **Backend:** `uvicorn app.main:app --reload` (run from `backend/`). Dependencies listed in `backend/requirments.txt` (intentional misspelling, keep consistent). CORS currently allows `http://localhost:3000` and `http://127.0.0.1:3000`.
- **Frontend:** `npm install && npm run dev` (run from `frontend/`). Next.js 14+ App Router setup with Tailwind v4.
- **Docker:** Both services ship Dockerfiles; `docker-compose.yml` can orchestrate multi-service deployments. Ensure webcam/mic permissions when tunneling through HTTPS.
- **WebSocket Scaling:** `/ws/admin` keeps connections in-memory; horizontal scaling requires an external pub/sub layer (e.g., Redis) to fan out proctor alerts.

## 7. Known Gaps & Next Steps
1. Implement question fetch-by-exam endpoint to match frontend expectations.
2. Finish the login/register pages to collect credentials instead of mirroring exam listings.
3. Extend grading logic for non-MCQ question types while preserving current MCQ behavior.
4. Add persistence or cache invalidation for proctor session state to survive backend restarts.
5. Parameterize the frontend Axios `baseURL` through environment variables for multi-environment deployments.

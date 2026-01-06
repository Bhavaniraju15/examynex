# Frontend-Backend Connection Guide

This document explains how the frontend and backend are connected in the ExamyNex project.

## Overview

The project consists of:
- **Backend**: FastAPI server running on `http://localhost:8000`
- **Frontend**: Static HTML/JavaScript files in `newexamplatformfrontend/`

## Backend Configuration

### API Base URL
All backend routes are prefixed with `/api`:
- User routes: `/api/users/`
- Exam routes: `/api/exams/`
- Question routes: `/api/questions/`
- Submission routes: `/api/submit/`
- Proctor routes: `/api/proctor/`

### CORS Configuration
The backend is configured to accept requests from any origin (for development):
```python
allow_origins=["*"]
```

## Frontend Configuration

### API Base URL
The frontend API base URL is configured in `newexamplatformfrontend/static/js/utils.js`:
```javascript
const API_BASE = 'http://localhost:8000/api';
```

**To change the backend URL**, update this constant in `utils.js`.

### Authentication
- Tokens are stored in `localStorage` as `access_token`
- Tokens are automatically included in API requests via the `Authorization: Bearer <token>` header
- Use `Utils.setAuthToken(token)` to store tokens after login
- Use `Utils.clearAuth()` to logout and clear tokens

## Connected Endpoints

### Authentication
- **Login**: `POST /api/users/login`
  - Request: `{ email, password }`
  - Response: `{ access_token }`
  - Frontend: `templates/auth/login.html`

- **Register**: `POST /api/users/register`
  - Request: `{ email, password, role }`
  - Response: `{ message }`
  - Frontend: `templates/auth/register.html`

### Exams
- **Create Exam**: `POST /api/exams/`
  - Request: `{ title, description }`
  - Response: `{ id, title, description }`
  - Frontend: `templates/faculty/create-exam.html`

- **List Exams**: `GET /api/exams/`
  - Response: `[{ id, title, description }, ...]`
  - Frontend: `templates/student/exams.html`

### Questions
- **Add Question**: `POST /api/questions/`
  - Request: `{ text, exam_id, correct_answer, is_mcq }`
  - Response: `{ id, text, exam_id, is_mcq, correct_answer }`
  - Frontend: `templates/faculty/create-exam.html`

## Running the Application

### 1. Start the Backend

Navigate to the `backend` folder and run:
```bash
# Option 1: Use the batch file (Windows)
run.bat

# Option 2: Manual command
python -m uvicorn app.main:app --reload
```

The backend will start on `http://localhost:8000`

### 2. Serve the Frontend

**Option A: Serve from Backend (Recommended)**
The backend is configured to serve static files. Simply access:
- Frontend: `http://localhost:8000/` (redirects to login page)
- Static files: `http://localhost:8000/static/...`
- Templates: `http://localhost:8000/templates/...`

**Option B: Separate HTTP Server**
If you prefer to serve the frontend separately:
```bash
cd newexamplatformfrontend
python -m http.server 8080
```
Then open `http://localhost:8080/templates/auth/login.html`
**Note**: You'll need to update `API_BASE` in `utils.js` if using a different port.

**Option C: Use a simple web server**
- VS Code Live Server extension
- Any static file server

## Testing the Connection

1. Start the backend server
2. Serve the frontend files
3. Open the login page
4. Register a new user or login with existing credentials
5. The token will be stored automatically and used for subsequent API calls

## Troubleshooting

### CORS Errors
- Ensure the backend is running and CORS is enabled
- Check that `API_BASE` in `utils.js` matches your backend URL

### Authentication Errors
- Verify the token is being stored: Check browser localStorage for `access_token`
- Ensure the token is included in requests (check browser Network tab)

### Connection Refused
- Verify the backend is running on the correct port
- Check firewall settings
- Ensure `API_BASE` URL is correct

## Notes

- The backend currently has basic schemas. Additional fields (like name, rollNumber, branch, etc.) would require backend schema/model updates.
- Some frontend features may still have placeholder API calls that need to be connected.
- For production, update CORS settings to only allow specific origins.


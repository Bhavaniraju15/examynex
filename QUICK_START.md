# 🚀 Quick Start Guide - ExamyNex

## ✅ Pre-Flight Check

The app is **READY TO RUN**! Here's what's been set up:

### ✅ Backend
- FastAPI server configured
- All routes prefixed with `/api`
- CORS enabled for frontend
- Database (SQLite) ready
- Static file serving enabled

### ✅ Frontend
- API connection configured
- Authentication token handling
- Login/Register connected
- Exam creation connected
- Exam listing connected

## 🏃 How to Run

### Step 1: Install Dependencies (First Time Only)

```bash
cd backend
pip install -r requirements.txt
```

### Step 1.5: Setup Environment Variables (Optional but Recommended)

The app works without a `.env` file (uses defaults), but it's recommended for security:

```bash
cd backend
# Copy the example file
copy .env.example .env
# (On Linux/Mac: cp .env.example .env)
```

**Important:** Edit `.env` and change `SECRET_KEY` to a random value for production!

See `backend/ENV_SETUP.md` for details.

**Note:** Some packages (like `face_recognition`, `opencv-python`) may take a few minutes to install.

### Step 2: Start the Backend

**Option A: Use the batch file (Windows)**
```bash
cd backend
run.bat
```

**Option B: Manual command**
```bash
cd backend
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Access the Application

Open your browser and go to:
- **Frontend**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **API Status**: http://localhost:8000/api/

## 🧪 Test the Connection

1. **Register a new user:**
   - Go to http://localhost:8000/
   - Click "Register here"
   - Fill in the registration form
   - You should see "Registration successful!"

2. **Login:**
   - Use the email and password you just registered
   - You should be redirected to the dashboard

3. **Create an Exam (as Admin/Faculty):**
   - Navigate to create exam page
   - Fill in exam details
   - Add questions
   - Click "Create Exam"
   - You should see "Exam created successfully!"

4. **View Exams (as Student):**
   - Login as a student
   - Go to "My Exams"
   - You should see the list of available exams

## ⚠️ Troubleshooting

### Issue: "Module not found" errors
**Solution:** Make sure all dependencies are installed:
```bash
cd backend
pip install -r requirements.txt
```

### Issue: Port 8000 already in use
**Solution:** Change the port:
```bash
python -m uvicorn app.main:app --reload --port 8001
```
Then update `API_BASE` in `newexamplatformfrontend/static/js/utils.js` to `http://localhost:8001/api`

### Issue: Frontend not loading
**Solution:** The backend serves the frontend automatically. If it doesn't work:
- Check that `newexamplatformfrontend` folder exists
- Or serve the frontend separately using a simple HTTP server

### Issue: CORS errors in browser console
**Solution:** The backend has CORS enabled. If you still see errors:
- Make sure the backend is running
- Check that `API_BASE` in `utils.js` matches your backend URL

### Issue: Database errors
**Solution:** The database is created automatically. If you see errors:
- Check that you have write permissions in the `backend` folder
- Delete `exam.db` and restart the server to recreate it

## 📝 Important Notes

1. **First User:** You'll need to register the first user. The system doesn't have a default admin account.

2. **Roles:** Currently, roles are detected from email patterns:
   - Email containing "admin" → Admin role
   - Email containing "faculty" → Faculty role
   - Otherwise → Student role

3. **Exam Creation:** Only users with "admin" role can create exams (as per backend logic).

4. **Token Storage:** Authentication tokens are stored in browser localStorage. Clear it to logout.

## 🎯 What Works Now

✅ User Registration  
✅ User Login  
✅ Token-based Authentication  
✅ Exam Creation (Admin/Faculty)  
✅ Exam Listing (Students)  
✅ Question Creation  
✅ Static File Serving  
✅ API Documentation (at /docs)

## 🔄 Next Steps (Optional Enhancements)

- Add role management in backend
- Decode JWT tokens properly to get user role
- Add more exam fields (duration, dates, etc.)
- Connect exam submission
- Connect proctoring features
- Add user profile management

---

**The app is ready! Just run `backend/run.bat` and open http://localhost:8000/**


from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import Base, engine
from app import models, models_proctor
from app.routes import user, exam, question, submission, proctor

# Request logging middleware
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        return response

# =====================================================
# CREATE APP
# =====================================================
app = FastAPI(title="AI Proctored Exam Backend")

# =====================================================
# MIDDLEWARES
# =====================================================

# Request logging (for debugging)
app.add_middleware(RequestLoggingMiddleware)

# ✅ CORS (MANDATORY FOR BROWSER / WEBCAM)
cors_origins = os.getenv("CORS_ORIGINS", "*")
if cors_origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ GZIP (Performance optimization – Step 10)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =====================================================
# DATABASE INIT
# =====================================================
Base.metadata.create_all(bind=engine)

# =====================================================
# API ROUTER (with /api prefix)
# =====================================================
api_router = APIRouter(prefix="/api")

# Include all routes under /api prefix
api_router.include_router(user.router)
api_router.include_router(exam.router)
api_router.include_router(question.router)
api_router.include_router(submission.router)
api_router.include_router(proctor.router)

# Mount the API router
app.include_router(api_router)

# =====================================================
# WEBSOCKET MANAGER (ADMIN LIVE MONITORING)
# =====================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/api/ws/admin")
async def admin_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# =====================================================
# FAVICON HANDLER (Prevents 405 errors)
# =====================================================
@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)  # No Content - browser will use default

# =====================================================
# OPTIONS HANDLER (FIXES 400/405 PREFLIGHT ERRORS)
# =====================================================
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    return Response(status_code=200)

# =====================================================
# STATIC FILES (Frontend) - Optional
# =====================================================
# Get the path to the frontend directory
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "newexamplatformfrontend")
frontend_path = os.path.abspath(frontend_path)

if os.path.exists(frontend_path):
    # Mount static files (CSS, JS, images)
    static_path = os.path.join(frontend_path, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")
    
    # Serve HTML files - only for non-API paths
    @app.get("/templates/{file_path:path}")
    async def serve_template(file_path: str):
        full_path = os.path.join(frontend_path, "templates", file_path)
        if os.path.exists(full_path) and os.path.isfile(full_path):
            return FileResponse(full_path)
        return Response(status_code=404, content="File not found")
    
    # Root redirects to login
    @app.get("/", response_class=FileResponse)
    async def serve_root():
        login_path = os.path.join(frontend_path, "templates", "auth", "login.html")
        if os.path.exists(login_path):
            return FileResponse(login_path)
        return {"message": "Frontend files not found. Please serve them separately."}
    
    # =====================================================
    # DYNAMIC CATCH-ALL ROUTE FOR ALL HTML PAGES
    # =====================================================
    # This handles all HTML pages from student, faculty, admin, and auth directories
    # Examples: /student/exams.html, /faculty/create-exam.html, /admin/dashboard.html
    @app.get("/{role}/{page_name}")
    async def serve_role_page(role: str, page_name: str):
        """
        Dynamic route handler for all role-based HTML pages.
        Supports: student, faculty, admin, auth directories
        """
        # Security: Only allow specific role directories
        allowed_roles = ["student", "faculty", "admin", "auth"]
        if role not in allowed_roles:
            return Response(status_code=404, content="Page not found")
        
        # Construct the file path
        file_path = os.path.join(frontend_path, "templates", role, page_name)
        
        # Check if file exists and is actually a file (not a directory)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        return Response(status_code=404, content=f"{role.capitalize()} page not found")

# =====================================================
# ROOT (API status)
# =====================================================
@app.get("/api/")
def api_root():
    return {"status": "Backend API running successfully", "docs": "/docs"}

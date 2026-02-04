from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.middleware.gzip import GZipMiddleware

from app.database import Base, engine
from app import models  # ⬅️ keep only this
from app.routes import user, exam, question, submission, proctor

# =====================================================
# CREATE APP
# =====================================================
app = FastAPI(title="Examnex Backend")

# =====================================================
# MIDDLEWARES
# =====================================================

# ✅ CORS (MANDATORY FOR BROWSER / WEBCAM)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",  # Live Server default
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://*.onrender.com",
        "https://bvcexamynex.netlify.app",
        "https://*.vercel.app",
        "https://*.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ GZIP (Performance optimization)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# =====================================================
# DATABASE INIT
# =====================================================
Base.metadata.create_all(bind=engine)

# =====================================================
# ROUTERS
# =====================================================
app.include_router(user.router)
app.include_router(user.auth_router)  # Add auth router
app.include_router(exam.router)
app.include_router(question.router)
app.include_router(submission.router)
app.include_router(proctor.router)

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

@app.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# =====================================================
# OPTIONS HANDLER (FIXES PREFLIGHT ISSUES)
# =====================================================
@app.options("/{path:path}")
async def options_handler(path: str, request: Request):
    return Response(status_code=200)

# =====================================================
# ROOT
# =====================================================
@app.get("/")
def root():
    return {"status": "Backend running successfully"}


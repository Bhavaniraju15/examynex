from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas, auth

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register")
def register(user: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = models.User(
        email=user.email,
        password=auth.hash_password(user.password),
        role=user.role
    )
    db.add(db_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not auth.verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({
        "user_id": user.id,
        "role": user.role
    })
    return {"access_token": token}

@router.get("/")
def list_users(role: str = None, db: Session = Depends(get_db)):
    """
    List all users, optionally filtered by role.
    Query params: ?role=student (or faculty, admin)
    """
    query = db.query(models.User)
    
    if role:
        query = query.filter(models.User.role == role)
    
    users = query.all()
    
    return [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]

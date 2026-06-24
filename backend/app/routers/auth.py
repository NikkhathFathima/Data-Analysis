from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from ..database import get_db, User
from ..auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterIn(BaseModel):
    email: str
    name: str
    password: str

class LoginIn(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # First user becomes admin
    role = "admin" if db.query(User).count() == 0 else "user"
    user = User(email=data.email, name=data.name,
                hashed_password=hash_password(data.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token({"sub": user.id})
    return {"token": token, "user": {"id": user.id, "name": user.name,
                                      "email": user.email, "role": user.role}}

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token({"sub": user.id})
    return {"token": token, "user": {"id": user.id, "name": user.name,
                                      "email": user.email, "role": user.role}}

@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "name": current_user.name,
            "email": current_user.email, "role": current_user.role}

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from app.database import get_db
from app.models.user import User
from app.schemas.auth import PasswordResetRequest, PasswordResetSubmit
from app.core.security import (
    get_current_user,
    create_access_token,
    verify_password,
    hash_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
def read_me(user: User = Depends(get_current_user)):
    return {
        "email": user.email,
        "is_admin": user.is_admin,
    }


@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.get("/whoami")
def who_am_i(user: User = Depends(get_current_user)):
    return {
        "email": user.email,
        "role": user.role,
    }


@router.post("/request-password-reset")
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == data.email).first()

    # altijd OK teruggeven (security best practice)
    if not user:
        return {"result": "ok"}

    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_expires = datetime.utcnow() + timedelta(minutes=30)

    db.commit()

    # later: mailservice
    print("RESET LINK:")
    print(f"http://localhost:3000/reset-password/{token}")

    return {"result": "ok"}


@router.post("/reset-password")
def reset_password(
    data: PasswordResetSubmit,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.reset_token == data.token).first()

    if not user:
        raise HTTPException(400, "Invalid token")

    if not user.reset_expires or user.reset_expires < datetime.utcnow():
        raise HTTPException(400, "Token expired")

    user.password_hash = hash_password(data.password)
    user.reset_token = None
    user.reset_expires = None

    db.commit()
    return {"result": "password changed"}

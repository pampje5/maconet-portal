from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserRoleUpdate
from app.core.security import (
    hash_password,
    require_min_role,
    UserRole,
)
from app.core.mail import send_email
import secrets
import os

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create", response_model=UserOut)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(400, "User already exists")

    # 🔐 tijdelijk wachtwoord
    temp_password = secrets.token_urlsafe(10)

    user = User(
        email=data.email,
        password_hash=hash_password(temp_password),
        role=data.role,
    )

    # 🔁 force reset
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_expires = datetime.utcnow() + timedelta(hours=24)

    db.add(user)
    db.commit()
    db.refresh(user)

    reset_url = f"{os.getenv('FRONTEND_URL')}/reset-password/{reset_token}"

    send_email(
        to=user.email,
        subject="Je account voor het portal",
        html=f"""
        <h2>Welkom</h2>
        <p>Er is een account voor je aangemaakt.</p>

        <p>
        <strong>Gebruikersnaam:</strong> {user.email}<br/>
        <strong>Tijdelijk wachtwoord:</strong> {temp_password}
        </p>

        <p>
        <a href="{reset_url}">
            Klik hier om je wachtwoord te wijzigen
        </a>
        <br/>
        (geldig tot {user.reset_expires.strftime('%d-%m-%Y %H:%M')} UTC)
        </p>

        <p>Wijzig je wachtwoord direct na het inloggen.</p>
        """,
    )


    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ❌ jezelf niet verwijderen
    if current_user.id == user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete yourself"
        )

    # ❌ developer mag alleen door developer worden verwijderd
    if (
        user.role == UserRole.developer
        and current_user.role != UserRole.developer
    ):
        raise HTTPException(
            status_code=403,
            detail="Only developer can delete a developer"
        )

    db.delete(user)
    db.commit()

    return {
        "status": "deleted",
        "user_id": user_id,
        "email": user.email,
    }

# ============================
# GET /users
# ============================
@router.get("", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    return db.query(User).order_by(User.email.asc()).all()


# ============================
# POST /users/{id}/set-role
# ============================
@router.post("/{user_id}/set-role")
def set_user_role(
    user_id: int,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    if user.id == current_user.id:
        raise HTTPException(400, "You cannot change your own role")

    user.role = data.role
    db.commit()

    return {
        "status": "ok",
        "user_id": user.id,
        "new_role": user.role,
    }
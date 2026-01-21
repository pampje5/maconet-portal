# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
import enum

from fastapi import Depends, Header, HTTPException
from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from app.core.config import JWT_SECRET, JWT_ALG
from app.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    developer = "developer"

ROLE_LEVEL = {
    UserRole.user: 1,
    UserRole.admin: 5,
    UserRole.developer: 10,
}

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)

def create_access_token(user: User) -> str:
    payload = {
        "sub": user.email,
        "role": user.role.value,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db),
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise HTTPException(401, "Invalid token")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(401, "User not found")

        return user
    except JWTError:
        raise HTTPException(401, "Invalid token")

def require_min_role(min_role: UserRole):
    def _guard(user: User = Depends(get_current_user)):
        if ROLE_LEVEL[user.role] < ROLE_LEVEL[min_role]:
            raise HTTPException(403, "Insufficient permissions")
        return user
    return _guard

def get_user_from_jwt_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

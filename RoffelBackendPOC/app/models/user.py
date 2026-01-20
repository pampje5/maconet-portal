from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from datetime import datetime
import enum

from app.database import Base

class UserRole(str, enum.Enum):
    user = "user"
    designer = "designer"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(
        Enum(UserRole),
        default=UserRole.user,
        nullable=False
    )

    is_admin = Column(Boolean, default=False)

    reset_token = Column(String, nullable = True)
    reset_expires = Column(DateTime, nullable = True)

    created_at = Column(DateTime, default=datetime.utcnow)
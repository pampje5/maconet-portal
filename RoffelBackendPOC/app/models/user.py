from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from datetime import datetime
import enum

from app.database import Base

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    developer = "developer"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    function = Column(String, nullable=True)

    role = Column(
        Enum(UserRole),
        default=UserRole.user,
        nullable=False
    )

    is_admin = Column(Boolean, default=False)

    reset_token = Column(String, nullable = True)
    reset_expires = Column(DateTime, nullable = True)

    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def full_name(self):
        return " ".join(filter(None, [self.first_name, self.last_name]))

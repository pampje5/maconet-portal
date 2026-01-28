import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import hash_password

load_dotenv()

def create_initial_admin(db: Session):
    user_exists = db.query(User).first()
    if user_exists:
        return  # database is al geïnitialiseerd

    admin = User(
        email=os.getenv("INITIAL_ADMIN_EMAIL"),
        password_hash=hash_password(
            os.getenv("INITIAL_ADMIN_PASSWORD")
        ),
        role="developer",
        
    )

    db.add(admin)
    db.commit()

from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash

def create_initial_admin(db: Session):
    user_exists = db.query(User).first()
    if user_exists:
        return  # database is al geïnitialiseerd

    admin = User(
        email=os.getenv("INITIAL_ADMIN_EMAIL"),
        hashed_password=get_password_hash(
            os.getenv("INITIAL_ADMIN_PASSWORD")
        ),
        role="developer",
        is_active=True,
    )

    db.add(admin)
    db.commit()

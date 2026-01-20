from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import SullairSettings
from app.schemas.customer import (
    SullairSettingsIn,
    SullairSettingsOut,
)
from app.models.user import User
from app.core.security import require_min_role, UserRole

router = APIRouter(tags=["Sullair"])




@router.get("/sullair/settings", response_model=SullairSettingsOut)
def get_sullair_settings(db: Session = Depends(get_db)):
    rec = db.query(SullairSettings).first()
    if not rec:
        # nog nooit ingesteld → leeg object terug
        return SullairSettingsOut(contact_name="", email="")
    return rec


@router.post("/sullair/settings", response_model=SullairSettingsOut)
def save_sullair_settings(
    data: SullairSettingsIn, 
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin))
    ):
    rec = db.query(SullairSettings).first()

    if not rec:
        rec = SullairSettings()

    rec.contact_name = data.contact_name
    rec.email = data.email

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return rec
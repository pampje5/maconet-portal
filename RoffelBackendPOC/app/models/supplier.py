from sqlalchemy import Column, String, Integer, DateTime, Boolean
from datetime import datetime, timezone

from app.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    id= Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    email_general = Column(String, nullable=True)
    supplier_contact = Column(String, nullable=True)
    supplier_contact_mail = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

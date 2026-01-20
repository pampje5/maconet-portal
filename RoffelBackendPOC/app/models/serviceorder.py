from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.database import Base

class ServiceOrder(Base):
    __tablename__ = "serviceorders"

    id = Column(Integer, primary_key=True, index=True)
    so = Column(String, unique=True, index=True, nullable=False)
    supplier = Column(String)
    customer_ref = Column(String)
    po = Column(String)
    status = Column(String)
    price_type = Column(String)
    employee = Column(String)
    remarks = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
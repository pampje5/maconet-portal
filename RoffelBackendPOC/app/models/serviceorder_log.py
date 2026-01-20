from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from app.database import Base


class ServiceOrderLog(Base):
    __tablename__ = "serviceorder_logs"

    id = Column(Integer, primary_key=True)
    serviceorder_id = Column(Integer, ForeignKey("serviceorders.id"))

    action = Column(String, nullable=False)
    message = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

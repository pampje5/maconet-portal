from sqlalchemy import (
    Column, Integer, String, Float,
    Boolean, DateTime, ForeignKey
)
from datetime import datetime

from app.database import Base

class ServiceOrderItem(Base):
    __tablename__ = "serviceorder_items"

    id = Column(Integer, primary_key=True)
    serviceorder_id = Column(Integer, ForeignKey("serviceorders.id"))

    part_no = Column(String, nullable=False)
    description = Column(String)
    qty = Column(Integer)

    list_price = Column(Float)
    price_bruto = Column(Float)
    price_wvk = Column(Float)
    price_edmac = Column(Float)
    price_purchase = Column(Float)

    leadtime = Column(String)
    bestellen = Column(Boolean, default=False)

    ontvangen = Column(Boolean, default=False)
    received_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
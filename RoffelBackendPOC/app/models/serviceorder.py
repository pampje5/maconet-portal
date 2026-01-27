from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base

class ServiceOrder(Base):
    __tablename__ = "serviceorders"

    id = Column(Integer, primary_key=True, index=True)

    so = Column(String, unique=True, index=True, nullable=False)

    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    # relaties
    supplier = relationship("Supplier")
    customer = relationship("Customer")

    customer_ref = Column(String)
    po = Column(String)
    status = Column(String)
    price_type = Column(String)
    employee = Column(String)
    remarks = Column(String)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

from sqlalchemy import (
    Column, Integer, String, DateTime,
    Boolean, Float, Enum, ForeignKey, UniqueConstraint
)
from datetime import datetime
import enum

from app.database import Base

class ServiceOrderNrStatus(str, enum.Enum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class ServiceOrderNumber(Base):
    __tablename__ = "service_order_numbers"

    id = Column(Integer, primary_key=True)

    so_number = Column(String, nullable=False, unique=True, index=True)

    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    sequence = Column(Integer, nullable=False)

    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name_free = Column(String, nullable=True)

    supplier = Column(String, nullable=True)
    description = Column(String, nullable=True)
    type = Column(String(2), nullable=True)

    offer = Column(Boolean, default=False)
    offer_amount = Column(Float, nullable=True)

    status = Column(
        Enum(ServiceOrderNrStatus),
        nullable=False,
        default=ServiceOrderNrStatus.FREE,
        index=True,
    )

    reserved_by = Column(String, nullable=True)
    reserved_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("year", "sequence", name="uq_so_year_sequence"),
    )
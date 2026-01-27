from sqlalchemy import (
    Column, Integer, String, DateTime,
    Boolean, Float, Enum, UniqueConstraint, ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class PurchaseOrderNrStatus(str, enum.Enum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class PurchaseOrderNumber(Base):
    __tablename__ = "purchase_order_numbers"

    id = Column(Integer, primary_key=True)

    po_number = Column(String, nullable=False, unique=True, index=True)

    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    sequence = Column(Integer, nullable=False)

    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    # 👇 KLANT
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name_free = Column(String, nullable=True)

    # 👇 LEVERANCIER
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    supplier_name_free = Column(String, nullable=True)

    description = Column(String, nullable=True)

    order_total = Column(Float, nullable=True)

    status = Column(
        Enum(PurchaseOrderNrStatus),
        nullable=False,
        default=PurchaseOrderNrStatus.FREE,
        index=True,
    )

    reserved_by = Column(String, nullable=True)
    reserved_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    serviceorders = relationship(
        "PurchaseOrderServiceOrderLink",
        back_populates="purchase_order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("year", "month", "sequence", name="uq_po_year_month_sequence"),
    )



class PurchaseOrderServiceOrderLink(Base):
    __tablename__ = "purchase_order_serviceorders"

    id = Column(Integer, primary_key=True)

    purchase_order_id = Column(
        Integer,
        ForeignKey("purchase_order_numbers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # we koppelen op so string (so_number), omdat dat jullie leidende sleutel is
    so_number = Column(String, nullable=False, index=True)

    purchase_order = relationship("PurchaseOrderNumber", back_populates="serviceorders")

    __table_args__ = (
        UniqueConstraint("purchase_order_id", "so_number", name="uq_po_so_link"),
    )

from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class PurchaseOrderNrStatusEnum(str, Enum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class PurchaseOrderServiceOrderLinkOut(BaseModel):
    so_number: str

    class Config:
        from_attributes = True


class PurchaseOrderNumberOut(BaseModel):
    id: int
    po_number: str

    year: int
    month: int
    sequence: int
    date: datetime

    # 👇 KLANT
    customer_id: Optional[int]
    customer_name_free: Optional[str]

    # 👇 LEVERANCIER
    supplier_id: Optional[int]
    supplier_name_free: Optional[str]

    description: Optional[str]
    order_total: Optional[float]

    status: PurchaseOrderNrStatusEnum

    reserved_by: Optional[str]
    reserved_at: Optional[datetime]
    confirmed_at: Optional[datetime]

    serviceorders: List[PurchaseOrderServiceOrderLinkOut] = []

    class Config:
        from_attributes = True



class PurchaseOrderNumberUpdate(BaseModel):
    customer_id: int | None = None
    customer_name_free: str | None = None

    supplier_id: int | None = None
    supplier_name_free: str | None = None

    description: str | None = None
    order_total: float | None = None



class PurchaseOrderNumberReserveOut(BaseModel):
    po_number: str
    status: PurchaseOrderNrStatusEnum


class PurchaseOrderServiceOrdersUpdate(BaseModel):
    so_numbers: List[str]

class PurchaseOrderServiceOrdersUpdate(BaseModel):
    so_numbers: List[str]


class PurchaseOrderPlaceRequest(BaseModel):
    force: bool = False


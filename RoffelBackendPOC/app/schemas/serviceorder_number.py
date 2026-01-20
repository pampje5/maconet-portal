from enum import Enum as PyEnum
from pydantic import BaseModel
from datetime import datetime

class ServiceOrderNrStatusEnum(str, PyEnum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class ServiceOrderNumberOut(BaseModel):
    id: int
    so_number: str

    year: int
    month: int
    sequence: int
    date: datetime

    customer_id: int | None = None
    customer_name_free: str | None = None

    supplier: str | None = None
    description: str | None = None
    type: str | None = None
    offer: bool = False
    offer_amount: float | None = None
    status: ServiceOrderNrStatusEnum

    reserved_by: str | None = None
    reserved_at: datetime | None = None
    confirmed_at: datetime | None = None

    class Config:
        from_attributes = True

class ServiceOrderNumberUpdate(BaseModel):
    customer_id: int | None = None
    customer_name_free: str | None = None

    supplier: str | None = None
    description: str | None = None
    type: str | None = None  # VO / OH

    offer: bool | None = None
    offer_amount: float | None = None

class ServiceOrderNumberReserveOut(BaseModel):
    so_number: str
    status: ServiceOrderNrStatusEnum
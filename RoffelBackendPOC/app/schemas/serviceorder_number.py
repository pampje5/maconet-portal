from enum import Enum 
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ServiceOrderNrStatusEnum(str, Enum):
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

    customer_id: Optional[int]
    customer_name_free: Optional[str] 

    supplier_id: Optional[int]
    supplier_name_free: Optional[str] 

    description: Optional[str]
    type: Optional[str]
    offer: bool 
    offer_amount: Optional[float] 

    status: ServiceOrderNrStatusEnum

    reserved_by: Optional[str]
    reserved_at: Optional[datetime] 
    confirmed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ServiceOrderNumberUpdate(BaseModel):
    customer_id: int | None = None
    customer_name_free: str | None = None

    supplier_id: int | None = None
    supplier_name_free: str | None = None

    description: str | None = None
    type: str | None = None  # VO / OH

    offer: bool | None = None
    offer_amount: float | None = None


class ServiceOrderNumberReserveOut(BaseModel):
    so_number: str
    status: ServiceOrderNrStatusEnum

class ServiceOrderNumberListOut(BaseModel):
    id: int
    so_number: str

    year: int
    month: int
    sequence: int
    date: datetime

    # 🔗 Relaties (leidend)
    supplier_id: Optional[int]
    customer_id: Optional[int]

    # 👁️ Display-velden (altijd gevuld)
    supplier_name: Optional[str] # Let op: afgeleid veld dus komt niet voor in db
    customer_name: Optional[str] # Let op: afgeleid veld dus komt niet voor in db

    description: Optional[str]
    type: Optional[str]

    offer: bool
    offer_amount: Optional[float]

    status: ServiceOrderNrStatusEnum

    reserved_by: Optional[str]
    reserved_at: Optional[datetime]
    confirmed_at: Optional[datetime]

    class Config:
        from_attributes = True
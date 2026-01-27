from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum

from app.schemas.supplier import SupplierOut
from app.schemas.customer import CustomerOut

class ServiceOrderStatusEnum(str, Enum):
    OPEN = "OPEN"
    AANGEVRAAGD = "AANGEVRAAGD"
    OFFERTE = "OFFERTE"
    WACHT_OP_COMBINATIE = "WACHT_OP_COMBINATIE"
    BESTELD = "BESTELD"
    ONTVANGEN = "ONTVANGEN"
    AFGEHANDELD = "AFGEHANDELD"


SERVICEORDER_ALLOWED_TRANSITIONS = {
    ServiceOrderStatusEnum.OPEN: [
        ServiceOrderStatusEnum.AANGEVRAAGD,
    ],
    ServiceOrderStatusEnum.AANGEVRAAGD: [
        ServiceOrderStatusEnum.OFFERTE,
        ServiceOrderStatusEnum.BESTELD,
    ],
    ServiceOrderStatusEnum.OFFERTE: [
        ServiceOrderStatusEnum.WACHT_OP_COMBINATIE,
        ServiceOrderStatusEnum.BESTELD,
    ],
    ServiceOrderStatusEnum.WACHT_OP_COMBINATIE: [
        ServiceOrderStatusEnum.BESTELD,
    ],
    ServiceOrderStatusEnum.BESTELD: [
        ServiceOrderStatusEnum.ONTVANGEN,
    ],
    ServiceOrderStatusEnum.ONTVANGEN: [
        ServiceOrderStatusEnum.AFGEHANDELD,
    ],
}



class ServiceOrderIn(BaseModel):
    so: str
    customer_id: Optional[int] = None
    supplier_id: Optional[int] = None
    customer_ref: Optional[str] = None
    po: Optional[str] = None
    status: Optional[str] = None
    price_type: Optional[str] = None
    employee: Optional[str] = None
    remarks: Optional[str] = None

class ServiceOrderOverview(BaseModel):
    id: int
    so: str

    supplier_id: int
    supplier: SupplierOut | None

    customer_id: int | None
    customer: CustomerOut | None

    po: str | None
    status: str
    price_type: str | None
    remarks: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceOrderStatusTransition(BaseModel):
    to: ServiceOrderStatusEnum
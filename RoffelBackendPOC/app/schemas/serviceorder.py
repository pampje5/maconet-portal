from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ServiceOrderIn(BaseModel):
    so: str
    supplier: Optional[str] = None
    customer_ref: Optional[str] = None
    po: Optional[str] = None
    status: Optional[str] = None
    price_type: Optional[str] = None
    employee: Optional[str] = None
    remarks: Optional[str] = None

class ServiceOrderOverview(BaseModel):
    so: str
    supplier: Optional[str]
    customer_ref: Optional[str]
    po: Optional[str]
    status: Optional[str]
    employee: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
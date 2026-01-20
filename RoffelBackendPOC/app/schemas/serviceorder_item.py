from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ServiceOrderItemIn(BaseModel):
    part_no: str
    description: Optional[str] = None
    qty: int

    list_price: Optional[float] = None
    price_bruto: Optional[float] = None
    price_wvk: Optional[float] = None
    price_edmac: Optional[float] = None
    price_purchase: Optional[float] = None

    leadtime: Optional[str] = None
    bestellen: bool = False
    ontvangen: Optional[bool] = False
    
class ServiceOrderItemOut(BaseModel):
    id: int
    part_no: str
    description: Optional[str]
    qty: int

    list_price: Optional[float]
    price_bruto: Optional[float]
    price_wvk: Optional[float]
    price_edmac: Optional[float]
    price_purchase: Optional[float]

    leadtime: Optional[str]
    bestellen: bool

    ontvangen: bool
    received_at: Optional[datetime]

    class Config:
        from_attributes = True
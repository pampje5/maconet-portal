from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, Union

class ServiceOrderForPOMergeOut(BaseModel):
    so: str
    date: Optional[Union[date, datetime]] = None
    customer_display: str
    supplier_display: str
    order_total: float
    currency: str = "EUR"
    status: Optional[str] = None
    can_merge: bool = True

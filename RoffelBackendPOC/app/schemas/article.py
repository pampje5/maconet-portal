from pydantic import BaseModel
from typing import Optional

class ArticleOut(BaseModel):
    part_no: str
    description: Optional[str] = None
    list_price: Optional[float] = None
    price_bruto: Optional[float] = None
    price_wvk: Optional[float] = None
    price_edmac: Optional[float] = None
    price_purchase: Optional[float] = None

    class Config:
        from_attributes = True
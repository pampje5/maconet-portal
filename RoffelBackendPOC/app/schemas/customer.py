from pydantic import BaseModel
from typing import Optional

class CustomerIn(BaseModel):
    name: str
    contact: str | None = None
    email: str | None = None
    price_type: str | None = None

    # ✅ NAW
    address: str | None = None
    zipcode: str | None = None
    city: str | None = None
    country: str | None = None

class CustomerOut(BaseModel):
    id: int
    name: str
    contact: str | None = None
    email: str | None = None
    price_type: str | None = None

    # ✅ NAW
    address: str | None = None
    zipcode: str | None = None
    city: str | None = None
    country: str | None = None

    class Config:
        from_attributes = True

class ContactOut(BaseModel):
    id: int 
    contact_name: str
    email: str
    is_primary: bool

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    contact_name: str
    email: str

class SullairSettingsIn(BaseModel):
    contact_name: Optional[str] = None
    email: Optional[str] = None

class SullairSettingsOut(BaseModel):
    contact_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

class CustomerPriceRuleIn(BaseModel):
    min_amount: float
    price_type: str

class CustomerPriceRuleOut(BaseModel):
    id: int
    min_amount: float
    price_type: str

    class Config:
        from_attributes = True
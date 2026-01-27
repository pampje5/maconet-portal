from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# =========================
# Input (POST / create)
# =========================
class SupplierIn(BaseModel):
    name: str
    email_general: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_contact_mail: Optional[str] = None
    is_active: bool = True


# =========================
# Update (PUT / PATCH)
# =========================
class SupplierUpdate(BaseModel):
    email_general: Optional[str] = None
    supplier_contact: Optional[str] = None
    supplier_contact_mail: Optional[str] = None
    is_active: Optional[bool] = None


# =========================
# Output (responses)
# =========================
class SupplierOut(BaseModel):
    id: int
    name: str
    email_general: Optional[str]
    supplier_contact: Optional[str]
    supplier_contact_mail: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

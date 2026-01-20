from pydantic import BaseModel
from datetime import datetime

class ServiceOrderLogOut(BaseModel):
    id: int
    action: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

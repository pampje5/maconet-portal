from pydantic import BaseModel,EmailStr
from enum import Enum

class UserRoleEnum (str, Enum):
    user = "user"
    admin = "admin"
    developer = "developer"
    
class UserCreate(BaseModel):
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.user
    first_name: str | None = None
    last_name: str | None = None
    function: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRoleEnum 
    first_name: str | None = None
    last_name: str | None = None
    function: str | None = None

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: UserRoleEnum

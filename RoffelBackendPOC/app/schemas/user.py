from pydantic import BaseModel,EmailStr
from enum import Enum

class UserRoleEnum (str, Enum):
    user = "user"
    designer = "designer"
    admin = "admin"
    
class UserCreate(BaseModel):
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.user

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRoleEnum 

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: UserRoleEnum

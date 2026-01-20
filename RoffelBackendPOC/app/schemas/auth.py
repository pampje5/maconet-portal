from pydantic import BaseModel

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetSubmit(BaseModel):
    token: str
    password: str
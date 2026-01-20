from pydantic import BaseModel

class MailPreviewOut(BaseModel):
    to: str
    subject: str
    body_html: str
    
class MailSendIn(BaseModel):
    to: str
    subject: str
    body_html: str

class MailPreviewIn(BaseModel):
    so: str
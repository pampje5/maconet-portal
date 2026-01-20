from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.serviceorder import ServiceOrder
from app.models.serviceorder_item import ServiceOrderItem
from app.models.customer import Customer, CustomerContact, SullairSettings
from app.schemas.mail import (
    MailPreviewIn,
    MailPreviewOut,
    MailSendIn,
)
from app.core.config import API_KEY

router = APIRouter()
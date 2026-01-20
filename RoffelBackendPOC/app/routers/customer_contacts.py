from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import CustomerContact
from app.schemas.customer import ContactCreate, ContactOut
from app.models.user import User
from app.core.security import require_min_role, UserRole

router = APIRouter(prefix="/customers", tags=["Customer Contacts"])





@router.get("/{customer_id}/contacts", response_model=List[ContactOut])
def get_contacts_for_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    rows = (
        db.query(CustomerContact)
        .filter(CustomerContact.customer_id == customer_id)
        .order_by(CustomerContact.contact_name.asc())
        .all()
    )
    return rows

@router.post("/{customer_id}/contacts", response_model=ContactOut)
def add_contact_for_customer(
    customer_id: int,
    data: ContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin))
):
    contact = CustomerContact(
        customer_id=customer_id,
        contact_name=data.contact_name,
        email=data.email,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.put("/contacts/{contact_id}")
def update_contact(
    contact_id: int, 
    data: ContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin))
    ):
    
    try:
        c = db.query(CustomerContact).filter(CustomerContact.id == contact_id).first()

        if not c:
            raise HTTPException(404, "Contact not found")

        c.contact_name = data.contact_name
        c.email = data.email

        db.commit()
        return {"result": "updated"}
    finally:
        db.close()


@router.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin))
    ):
    c = db.query(CustomerContact).filter(CustomerContact.id == contact_id).first()

    if not c:
        raise HTTPException(404, "Contact not found")

    db.delete(c)
    db.commit()
    return {"result": "deleted"}


@router.post("/contacts/{contact_id}/set_primary")
def set_primary_contact(
    contact_id: int, 
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin))
    ):

    contact = db.query(CustomerContact).filter(CustomerContact.id == contact_id).first()
    if not contact:
        raise HTTPException(404, "Contact not found")

    # alle andere van deze klant op False
    db.query(CustomerContact).filter(
        CustomerContact.customer_id == contact.customer_id
    ).update({CustomerContact.is_primary: False})

    contact.is_primary = True
    db.commit()

    return {"status": "ok"}
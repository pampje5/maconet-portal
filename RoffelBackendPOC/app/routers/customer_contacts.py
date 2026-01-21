from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import CustomerContact
from app.schemas.customer import ContactCreate, ContactOut
from app.models.user import User
from app.core.security import require_min_role, UserRole

router = APIRouter(
    prefix="/customers",
    tags=["Customer Contacts"]
)

# =========================
# GET CONTACTS
# =========================
@router.get("/{customer_id}/contacts", response_model=List[ContactOut])
def get_contacts_for_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    return (
        db.query(CustomerContact)
        .filter(CustomerContact.customer_id == customer_id)
        .order_by(CustomerContact.contact_name.asc())
        .all()
    )

# =========================
# ADD CONTACT
# =========================
@router.post("/{customer_id}/contacts", response_model=ContactOut)
def add_contact_for_customer(
    customer_id: int,
    data: ContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
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

# =========================
# UPDATE CONTACT
# =========================
@router.put("/{customer_id}/contacts/{contact_id}")
def update_contact(
    customer_id: int,
    contact_id: int,
    data: ContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    contact = (
        db.query(CustomerContact)
        .filter(
            CustomerContact.id == contact_id,
            CustomerContact.customer_id == customer_id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(404, "Contact not found")

    contact.contact_name = data.contact_name
    contact.email = data.email
    db.commit()

    return {"result": "updated"}

# =========================
# DELETE CONTACT
# =========================
@router.delete("/{customer_id}/contacts/{contact_id}")
def delete_contact(
    customer_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    contact = (
        db.query(CustomerContact)
        .filter(
            CustomerContact.id == contact_id,
            CustomerContact.customer_id == customer_id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(404, "Contact not found")

    db.delete(contact)
    db.commit()
    return {"result": "deleted"}

# =========================
# SET PRIMARY CONTACT
# =========================
@router.post("/{customer_id}/contacts/{contact_id}/set_primary")
def set_primary_contact(
    customer_id: int,
    contact_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    contact = (
        db.query(CustomerContact)
        .filter(
            CustomerContact.id == contact_id,
            CustomerContact.customer_id == customer_id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(404, "Contact not found")

    # reset others
    db.query(CustomerContact).filter(
        CustomerContact.customer_id == customer_id
    ).update({CustomerContact.is_primary: False})

    contact.is_primary = True
    db.commit()

    return {"status": "ok"}

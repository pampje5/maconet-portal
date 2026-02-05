from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerOut
from app.models.user import User
from app.core.security import get_current_user, require_min_role, UserRole

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.get("", response_model=List[CustomerOut])
def list_customers(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return (
        db.query(Customer)
        .order_by(Customer.name.asc())
        .all()
    )

@router.post("", response_model=CustomerOut)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    rec = Customer(
        name=data.name,
        contact=data.contact,
        email=data.email,
        price_type=data.price_type,
        address=data.address,
        zipcode=data.zipcode,
        city=data.city,
        country=data.country,
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return rec

@router.put("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(404, "Customer not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(cust, field, value)

    db.commit()
    db.refresh(cust)
    return cust
    


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    cust = db.query(Customer).filter(Customer.id == customer_id).first()
    if not cust:
        raise HTTPException(404, "Customer not found")

    if not cust.is_active:
        return {"result": "already inactive"}

    cust.is_active = False
    db.commit()

    return {"result": "deactivated"}






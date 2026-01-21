from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.customer import Customer, CustomerPriceRule
from app.schemas.customer import (
    CustomerPriceRuleIn,
    CustomerPriceRuleOut,
)
from app.models.user import User
from app.core.security import require_min_role, UserRole

router = APIRouter(
    prefix="/customers",
    tags=["Customer Pricing"],
)

# =========================
# GET PRICE RULES
# =========================
@router.get(
    "/{customer_id}/price-rules",
    response_model=List[CustomerPriceRuleOut]
)
def get_price_rules(
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")

    return (
        db.query(CustomerPriceRule)
        .filter(CustomerPriceRule.customer_id == customer_id)
        .order_by(CustomerPriceRule.min_amount.asc())
        .all()
    )

# =========================
# SAVE / REPLACE PRICE RULES
# =========================
@router.post("/{customer_id}/price-rules")
def save_price_rules(
    customer_id: int,
    data: List[CustomerPriceRuleIn],
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin)),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(404, "Customer not found")

    db.query(CustomerPriceRule).filter(
        CustomerPriceRule.customer_id == customer_id
    ).delete()

    for rule in data:
        db.add(
            CustomerPriceRule(
                customer_id=customer_id,
                min_amount=rule.min_amount,
                price_type=rule.price_type,
            )
        )

    db.commit()

    return {
        "status": "ok",
        "count": len(data),
    }

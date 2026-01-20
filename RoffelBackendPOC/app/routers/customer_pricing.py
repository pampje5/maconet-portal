from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import CustomerPriceRule
from app.schemas.customer import (
    CustomerPriceRuleIn,
    CustomerPriceRuleOut,
)
from app.models.user import User
from app.core.security import require_min_role, UserRole

router = APIRouter(prefix="/customers", tags=["Customer Pricing"])




@router.get(
    "/{customer_id}/price-rules",
    response_model=list[CustomerPriceRuleOut]
)
def get_price_rules(
    customer_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user))
):
    

    return (
        db.query(CustomerPriceRule)
        .filter(CustomerPriceRule.customer_id == customer_id)
        .order_by(CustomerPriceRule.min_amount.asc())
        .all()
    )

@router.post("/{customer_id}/price-rules")
def save_price_rules(
    customer_id: int,
    data: list[CustomerPriceRuleIn],
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin))
):
    

    db.query(CustomerPriceRule).filter(
        CustomerPriceRule.customer_id == customer_id
    ).delete()

    for rule in data:
        db.add(CustomerPriceRule(
            customer_id=customer_id,
            min_amount=rule.min_amount,
            price_type=rule.price_type
        ))

    db.commit()
    return {"status": "ok", "count": len(data)}

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.serviceorder import ServiceOrder
from app.models.customer import  CustomerPriceRule
from app.schemas.customer import CustomerPriceRuleIn, CustomerPriceRuleOut
from app.core.config import API_KEY
from app.core.security import require_min_role, UserRole
from app.models.user import User
from app.services.pricing import calculate_order_totals

router = APIRouter()


@router.get("/serviceorders/{so}/pricing")
def get_serviceorder_pricing(
    so: str,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.admin))
):


    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    try:
        pricing = calculate_order_totals(db, order)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return pricing
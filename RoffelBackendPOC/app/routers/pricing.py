from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.serviceorder import ServiceOrder
from app.services.pricing import calculate_order_totals
from app.models.user import User
from app.core.security import require_min_role, UserRole

router = APIRouter(
    prefix="/serviceorders",
    tags=["Pricing"],
)


@router.get("/{so}/pricing")
def get_serviceorder_pricing(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    try:
        return calculate_order_totals(db, order)
    except ValueError as e:
        raise HTTPException(400, str(e))

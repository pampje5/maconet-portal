# app/services/orders.py

from sqlalchemy.orm import Session
from datetime import datetime

from app.models.serviceorder import ServiceOrder
from app.models.serviceorder_log import ServiceOrderLog


def log_event(
    db: Session,
    order: ServiceOrder,
    action: str,
    message: str,
):
    log = ServiceOrderLog(
        serviceorder_id=order.id,
        action=action,
        message=message,
        created_at=datetime.utcnow(),
    )
    db.add(log)
    db.commit()


def set_order_status(
    db: Session,
    order: ServiceOrder,
    status: str,
    message: str,
):
    order.status = status

    log_event(
        db=db,
        order=order,
        action=status,
        message=message,
    )

    db.commit()

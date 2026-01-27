from sqlalchemy.orm import Session
from datetime import datetime

from app.models.purchaseorder_number import PurchaseOrderNumber, PurchaseOrderNrStatus
from app.models.serviceorder_item import ServiceOrderItem
from app.models.serviceorder import ServiceOrder


def collect_order_items_from_serviceorders(
    db: Session,
    so_numbers: list[str],
):
    items = []

    for so in so_numbers:
        so_items = (
            db.query(ServiceOrderItem)
            .filter(ServiceOrderItem.serviceorder_id == so)
            .filter(ServiceOrderItem.bestellen == True)
            .all()
        )
        items.extend(so_items)

    return items


def mark_serviceorder_as_ordered(db: Session, so_number: str):
    so = (
        db.query(ServiceOrder)
        .filter(ServiceOrder.so == so_number)
        .first()
    )

    if so:
        so.status = "BESTELD"
        db.add(so)

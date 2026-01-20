from sqlalchemy.orm import Session

from app.models.serviceorder import ServiceOrder
from app.models.serviceorder_log import ServiceOrderLog


def get_serviceorder_logs(
    db: Session,
    so: str,
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        return None

    return (
        db.query(ServiceOrderLog)
        .filter(ServiceOrderLog.serviceorder_id == order.id)
        .order_by(ServiceOrderLog.created_at.desc())
        .all()
    )

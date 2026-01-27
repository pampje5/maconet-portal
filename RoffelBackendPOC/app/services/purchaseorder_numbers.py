from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.purchaseorder_number import PurchaseOrderNumber, PurchaseOrderNrStatus


def _format_po_number(year: int, month: int, seq: int) -> str:
    yy = str(year)[-2:]
    mm = f"{month:02d}"
    xxx = f"{seq:03d}"
    return f"{yy}{mm}{xxx}"


def reserve_next_purchaseorder_number(db: Session, reserved_by: str) -> PurchaseOrderNumber:
    now = datetime.utcnow()
    year = now.year
    month = now.month

    max_seq = (
        db.query(func.max(PurchaseOrderNumber.sequence))
        .filter(PurchaseOrderNumber.year == year)
        .filter(PurchaseOrderNumber.month == month)
        .scalar()
    ) or 0

    next_seq = max_seq + 1
    po_number = _format_po_number(year, month, next_seq)

    rec = PurchaseOrderNumber(
        po_number=po_number,
        year=year,
        month=month,
        sequence=next_seq,
        date=now,
        status=PurchaseOrderNrStatus.RESERVED,
        reserved_by=reserved_by,
        reserved_at=now,
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

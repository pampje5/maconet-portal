from sqlalchemy.orm import Session
from datetime import datetime
from fastapi import HTTPException

from app.models.serviceorder_number import ServiceOrderNumber, ServiceOrderNrStatus




def format_so_number(year: int, month: int, sequence: int) -> str:
    yy = str(year)[-2:]
    mm = f"{month:02d}"
    seq = f"{sequence:04d}"
    return f"{yy}{mm}{seq}"

def reserve_next_serviceorder_number(
    db: Session,
    reserved_by: str,
    date_: datetime | None = None,
) -> ServiceOrderNumber:

    now = date_ or datetime.utcnow()
    year = now.year
    month = now.month

    # 🔒 SQLite write-lock
    db.connection().exec_driver_sql("BEGIN IMMEDIATE")

    # 1️⃣ hergebruik eerst FREE nummers binnen dit jaar
    free = (
        db.query(ServiceOrderNumber)
        .filter(
            ServiceOrderNumber.year == year,
            ServiceOrderNumber.status == ServiceOrderNrStatus.FREE
        )
        .order_by(ServiceOrderNumber.sequence.asc())
        .first()
    )

    if free:
        free.status = ServiceOrderNrStatus.RESERVED
        free.reserved_by = reserved_by
        free.reserved_at = now
        db.commit()
        return free

    # 2️⃣ bepaal volgende sequence binnen dit jaar
    last_seq = (
        db.query(ServiceOrderNumber.sequence)
        .filter(ServiceOrderNumber.year == year)
        .order_by(ServiceOrderNumber.sequence.desc())
        .first()
    )

    next_seq = last_seq[0] + 1 if last_seq else 1

    so_number = format_so_number(year, month, next_seq)

    rec = ServiceOrderNumber(
        so_number=so_number,
        year=year,
        month=month,
        sequence=next_seq,
        date=now,
        status=ServiceOrderNrStatus.RESERVED,
        reserved_by=reserved_by,
        reserved_at=now,
    )

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return rec


def confirm_serviceorder_number(
    db: Session,
    so_number: str,
    supplier_id: int | None = None,
    supplier_name_free: str | None = None,
    customer_id: int | None = None,
    customer_name_free: str | None = None,
    description: str | None = None,
    type: str | None = None,
):
    rec = (
        db.query(ServiceOrderNumber)
        .filter(ServiceOrderNumber.so_number == so_number)
        .first()
    )

    if not rec:
        raise HTTPException(404, "Service order number not found")

    if rec.status != ServiceOrderNrStatus.RESERVED:
        raise HTTPException(400, "Only RESERVED numbers can be confirmed")

    # 🔗 Relaties
    rec.supplier_id = supplier_id
    rec.supplier_name_free = supplier_name_free

    rec.customer_id = customer_id
    rec.customer_name_free = customer_name_free

    # 📝 Inhoud
    rec.description = description
    rec.type = type

    rec.status = ServiceOrderNrStatus.CONFIRMED
    rec.confirmed_at = datetime.utcnow()

    db.commit()
    return rec



def cancel_serviceorder_number(
    db: Session,
    so_number: str,
):
    rec = (
        db.query(ServiceOrderNumber)
        .filter(ServiceOrderNumber.so_number == so_number)
        .first()
    )

    if not rec:
        raise HTTPException(404, "Service order number not found")

    if rec.status != ServiceOrderNrStatus.RESERVED:
        raise HTTPException(400, "Only RESERVED numbers can be cancelled")

    rec.status = ServiceOrderNrStatus.FREE
    rec.reserved_by = None
    rec.reserved_at = None

    db.commit()
    return rec
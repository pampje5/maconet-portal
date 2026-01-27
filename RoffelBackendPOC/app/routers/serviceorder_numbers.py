from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime



from app.database import get_db
from app.models.serviceorder_number import ServiceOrderNumber, ServiceOrderNrStatus
from app.schemas.serviceorder_number import (
    ServiceOrderNumberOut,
    ServiceOrderNumberUpdate,
    ServiceOrderNumberReserveOut,
    ServiceOrderNumberListOut,
    ServiceOrderNrStatusEnum
)

from app.services.serviceorder_numbers import ( 
    reserve_next_serviceorder_number,
    confirm_serviceorder_number,
    cancel_serviceorder_number,
    )
from app.core.security import get_current_user, require_min_role, UserRole

router = APIRouter(prefix="/serviceorder-numbers", tags=["serviceorder-numbers"])


@router.post("/reserve", response_model=ServiceOrderNumberReserveOut)
def reserve_so_number(
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = reserve_next_serviceorder_number(
        db=db,
        reserved_by=user.email  
    )
    return {
        "so_number": rec.so_number,
        "status": rec.status,
    }

@router.post("/reserve-batch/{count}")
def reserve_batch(
    count: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    numbers = []
    for _ in range(count):
        rec = reserve_next_serviceorder_number(
            db=db,
            reserved_by="WORKSHOP"
        )
        numbers.append(rec.so_number)

    return {
        "count": len(numbers),
        "numbers": numbers
    }

@router.post(
    "/{so_number}/confirm",
    response_model=ServiceOrderNumberOut,
)
def confirm_serviceorder_number(
    so_number: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(ServiceOrderNumber)
        .filter(ServiceOrderNumber.so_number == so_number)
        .first()
    )

    if not rec:
        raise HTTPException(404, "Service order number not found")

    if rec.status != ServiceOrderNrStatusEnum.RESERVED:
        raise HTTPException(
            status_code=400,
            detail="Only RESERVED numbers can be confirmed"
        )

    rec.status = ServiceOrderNrStatusEnum.CONFIRMED
    rec.confirmed_at = datetime.utcnow()

    db.commit()
    db.refresh(rec)

    return rec


@router.post("/{so_number}/cancel")
def cancel_so_number(
    so_number: str,
    user=Depends(require_min_role(UserRole.user)),
    db: Session = Depends(get_db)
):
    cancel_serviceorder_number(db, so_number)
    return {"status": "cancelled"}


@router.get(
    "",
    response_model=list[ServiceOrderNumberListOut],
)
def list_serviceorder_numbers(
    year: int | None = None,
    month: int | None = None,
    quarter: int | None = None,
    status: ServiceOrderNrStatus | None = None,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    query = (
        db.query(ServiceOrderNumber)
    )

    if year:
        query = query.filter(ServiceOrderNumber.year == year)

    if month:
        query = query.filter(ServiceOrderNumber.month == month)

    if quarter:
        start = (quarter - 1) * 3 + 1
        end = start + 2
        query = query.filter(ServiceOrderNumber.month.between(start, end))

    if status:
        query = query.filter(ServiceOrderNumber.status == status)

    records = (
        query
        .order_by(
            ServiceOrderNumber.year.desc(),
            ServiceOrderNumber.sequence.desc(),
        )
        .all()
    )

    # 🔁 EXPLICIETE mapping → geen magic
    return [
        ServiceOrderNumberListOut(
            id=r.id,
            so_number=r.so_number,
            year=r.year,
            month=r.month,
            sequence=r.sequence,
            date=r.date,

            supplier_id=r.supplier_id,
            customer_id=r.customer_id,

            supplier_name=(r.supplier_name_free),
            customer_name=(r.customer_name_free),

            description=r.description,
            type=r.type,

            offer=r.offer,
            offer_amount=r.offer_amount,

            status=r.status,
            reserved_by=r.reserved_by,
            reserved_at=r.reserved_at,
            confirmed_at=r.confirmed_at,
        )
        for r in records
    ]

@router.put(
    "/{so_number}",
    response_model=ServiceOrderNumberOut,
)
def update_serviceorder_number(
    so_number: str,
    payload: ServiceOrderNumberUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(ServiceOrderNumber)
        .filter(ServiceOrderNumber.so_number == so_number)
        .first()
    )

    if not rec:
        raise HTTPException(404, "Service order number not found")

    # 🔒 alleen bewerken zolang hij nog niet definitief is
    if rec.status != ServiceOrderNrStatus.RESERVED:
        raise HTTPException(
            status_code=400,
            detail="Only RESERVED service order numbers can be updated"
        )

    # 🔄 update alleen meegegeven velden
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rec, field, value)

    db.commit()
    db.refresh(rec)

    return rec

@router.get(
    "/{so_number}",
    response_model=ServiceOrderNumberOut,
)
def get_serviceorder_number(
    so_number: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    rec = (
        db.query(ServiceOrderNumber)
        .filter(ServiceOrderNumber.so_number == so_number)
        .first()
    )

    if not rec:
        raise HTTPException(404, "Service order number not found")

    return rec

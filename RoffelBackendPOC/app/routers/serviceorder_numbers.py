from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional


from app.database import get_db
from app.models.serviceorder_number import ServiceOrderNumber, ServiceOrderNrStatus
from app.schemas.serviceorder_number import (
    ServiceOrderNumberOut,
    ServiceOrderNumberUpdate,
    ServiceOrderNumberReserveOut,
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

@router.post("/{so_number}/confirm")
def confirm_so_number(
    so_number: str,
    user= Depends(require_min_role(UserRole.user)),
    db: Session = Depends(get_db)
):
    confirm_serviceorder_number(db, so_number)
    return {"status": "confirmed"}

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
    response_model=List[ServiceOrderNumberOut],
)
def list_serviceorder_numbers(
    year: Optional[int] = Query(None),
    month: Optional[int] = Query(None, ge=1, le=12),
    quarter: Optional[int] = Query(None, ge=1, le=4),
    status: Optional[ServiceOrderNrStatus] = Query(None),

    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ServiceOrderNumber)

    # 🔹 jaarfilter
    if year is not None:
        query = query.filter(ServiceOrderNumber.year == year)

    # 🔹 maandfilter
    if month is not None:
        query = query.filter(ServiceOrderNumber.month == month)

    # 🔹 kwartaalfilter (overrulet maand als beide gezet zijn)
    if quarter is not None:
        start_month = (quarter - 1) * 3 + 1
        end_month = start_month + 2
        query = query.filter(
            ServiceOrderNumber.month.between(start_month, end_month)
        )

    # 🔹 statusfilter
    if status is not None:
        query = query.filter(ServiceOrderNumber.status == status)

    return (
        query
        .order_by(
            ServiceOrderNumber.year.desc(),
            ServiceOrderNumber.sequence.desc()
        )
        .all()
    )

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
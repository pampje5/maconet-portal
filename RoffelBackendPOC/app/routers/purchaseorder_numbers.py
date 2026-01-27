from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_user, require_min_role, UserRole

from app.models.purchaseorder_number import PurchaseOrderNumber, PurchaseOrderServiceOrderLink, PurchaseOrderNrStatus
from app.schemas.purchaseorder_number import (
    PurchaseOrderNumberOut,
    PurchaseOrderNumberUpdate,
    PurchaseOrderNumberReserveOut,
    PurchaseOrderNrStatusEnum,
    PurchaseOrderServiceOrdersUpdate,
    PurchaseOrderPlaceRequest
)

from app.services.purchaseorder_numbers import reserve_next_purchaseorder_number
from app.services.purchaseorder_orders import collect_order_items_from_serviceorders, mark_serviceorder_as_ordered


router = APIRouter(prefix="/purchaseorder-numbers", tags=["purchaseorder-numbers"])


@router.post("/reserve", response_model=PurchaseOrderNumberReserveOut)
def reserve_po_number(
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = reserve_next_purchaseorder_number(db=db, reserved_by=user.email)
    return {"po_number": rec.po_number, "status": rec.status}


@router.get("", response_model=list[PurchaseOrderNumberOut])
def list_purchaseorder_numbers(
    year: int | None = None,
    month: int | None = None,
    status: PurchaseOrderNrStatus | None = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = db.query(PurchaseOrderNumber)

    if year:
        q = q.filter(PurchaseOrderNumber.year == year)
    if month:
        q = q.filter(PurchaseOrderNumber.month == month)
    if status:
        q = q.filter(PurchaseOrderNumber.status == status)

    return (
        q.order_by(
            PurchaseOrderNumber.year.desc(),
            PurchaseOrderNumber.month.desc(),
            PurchaseOrderNumber.sequence.desc(),
        )
        .all()
    )


@router.get("/{po_number}", response_model=PurchaseOrderNumberOut)
def get_purchaseorder_number(
    po_number: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(PurchaseOrderNumber)
        .filter(PurchaseOrderNumber.po_number == po_number)
        .first()
    )
    if not rec:
        raise HTTPException(404, "Purchase order number not found")
    return rec


@router.put("/{po_number}", response_model=PurchaseOrderNumberOut)
def update_purchaseorder_number(
    po_number: str,
    payload: PurchaseOrderNumberUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(PurchaseOrderNumber)
        .filter(PurchaseOrderNumber.po_number == po_number)
        .first()
    )
    if not rec:
        raise HTTPException(404, "Purchase order number not found")

    if rec.status != PurchaseOrderNrStatus.RESERVED:
        raise HTTPException(400, "Only RESERVED purchase order numbers can be updated")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(rec, field, value)

    db.commit()
    db.refresh(rec)
    return rec


@router.post("/{po_number}/confirm", response_model=PurchaseOrderNumberOut)
def confirm_purchaseorder_number(
    po_number: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(PurchaseOrderNumber)
        .filter(PurchaseOrderNumber.po_number == po_number)
        .first()
    )
    if not rec:
        raise HTTPException(404, "Purchase order number not found")

    if rec.status != PurchaseOrderNrStatusEnum.RESERVED:
        raise HTTPException(400, "Only RESERVED numbers can be confirmed")

    rec.status = PurchaseOrderNrStatusEnum.CONFIRMED
    rec.confirmed_at = datetime.utcnow()

    db.commit()
    db.refresh(rec)
    return rec


@router.post("/{po_number}/cancel")
def cancel_po_number(
    po_number: str,
    user=Depends(require_min_role(UserRole.user)),
    db: Session = Depends(get_db),
):
    rec = (
        db.query(PurchaseOrderNumber)
        .filter(PurchaseOrderNumber.po_number == po_number)
        .first()
    )
    if not rec:
        raise HTTPException(404, "Purchase order number not found")

    rec.status = PurchaseOrderNrStatus.CANCELLED
    db.commit()
    return {"status": "cancelled"}

@router.put(
    "/{po_number}/serviceorders",
    response_model=PurchaseOrderNumberOut,
)
def update_po_serviceorders(
    po_number: str,
    payload: PurchaseOrderServiceOrdersUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    po = (
        db.query(PurchaseOrderNumber)
        .filter(PurchaseOrderNumber.po_number == po_number)
        .first()
    )

    if not po:
        raise HTTPException(404, "Purchase order number not found")

    if po.status != PurchaseOrderNrStatus.RESERVED:
        raise HTTPException(
            status_code=400,
            detail="Only RESERVED purchase orders can be updated"
        )

    # 1️⃣ Bestaande koppelingen expliciet verwijderen
    db.query(PurchaseOrderServiceOrderLink)\
        .filter(PurchaseOrderServiceOrderLink.purchase_order_id == po.id)\
        .delete(synchronize_session=False)

    db.commit()   # ⬅️ DIT IS DE CRUCIALE FIX

    # 2️⃣ Nieuwe koppelingen toevoegen
    for so in payload.so_numbers:
        db.add(
            PurchaseOrderServiceOrderLink(
                purchase_order_id=po.id,
                so_number=so
            )
        )

    db.commit()
    db.refresh(po)
    return po

@router.post("/{po_number}/order")
def place_purchaseorder(
    po_number: str,
    payload: PurchaseOrderPlaceRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    po = (
        db.query(PurchaseOrderNumber)
        .filter(PurchaseOrderNumber.po_number == po_number)
        .first()
    )

    if not po:
        raise HTTPException(404, "Purchase order not found")

    if po.status != PurchaseOrderNrStatus.RESERVED:
        raise HTTPException(400, "Only RESERVED purchase orders can be ordered")

    so_numbers = [l.so_number for l in po.serviceorders]

    if not so_numbers:
        raise HTTPException(400, "No serviceorders linked to this PO")

    # 1️⃣ Items verzamelen
    items = collect_order_items_from_serviceorders(db, so_numbers)

    if not items:
        raise HTTPException(400, "No orderable items found")

    total = sum(
        (it.price_purchase or 0) * it.qty
        for it in items
    )

    # 2️⃣ Minimum-order-check
    MIN_ORDER_AMOUNT = 500  # straks config

    if total < MIN_ORDER_AMOUNT and not payload.force:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "MIN_ORDER_NOT_REACHED",
                "order_total": total,
                "minimum": MIN_ORDER_AMOUNT,
            },
        )

    # 3️⃣ HIER haak je je bestaande bestelactie in
    # perform_supplier_order(...)

    # 4️⃣ Statusupdates
    for so in so_numbers:
        mark_serviceorder_as_ordered(db, so)

    po.status = PurchaseOrderNrStatus.CONFIRMED
    po.order_total = total
    po.confirmed_at = datetime.utcnow()

    db.commit()

    return {
        "status": "ordered",
        "po_number": po.po_number,
        "order_total": total,
        "serviceorders": so_numbers,
    }



from fastapi import APIRouter, Depends, HTTPException, Path, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime

from app.database import get_db

from app.models.serviceorder import ServiceOrder
from app.models.serviceorder_item import ServiceOrderItem
from app.models.article import Article
from app.models.user import User
from app.models.customer import Customer
from app.models.supplier import Supplier

from app.schemas.serviceorder import (
    ServiceOrderIn,
    ServiceOrderOverview,
    ServiceOrderStatusTransition,
    ServiceOrderStatusEnum,
    SERVICEORDER_ALLOWED_TRANSITIONS,
)
from app.schemas.serviceorder_item import (
    ServiceOrderItemIn,
    ServiceOrderItemOut,
)
from app.schemas.serviceorder_log import ServiceOrderLogOut
from app.schemas.article import ArticleOut
from app.schemas.mail import MailPreviewOut, MailPreviewIn
from app.schemas.serviceorder_merge import ServiceOrderForPOMergeOut

from app.core.security import get_current_user, require_min_role, UserRole

from app.services.orders import set_order_status, log_event
from app.services.documents.packing_slip import build_packing_slip_pdf
from app.services.documents.stock_order import build_stock_order_pdf
from app.services.documents.mail_templates import (
    build_stock_order_mail,
    build_supplier_leadtime_mail,
    build_offer_mail,
    build_order_confirmation_mail,
)
from app.services.serviceorder_numbers import confirm_serviceorder_number
from app.services.pricing import calculate_order_totals

# ✅ NEW: echte mail verzending
from app.services.mail.mail_sender import send_mail

import os


router = APIRouter(
    prefix="/serviceorders",
    tags=["serviceorders"],
)

# ==================================================
# SERVICE ORDERS
# ==================================================

@router.post("/upsert")
def upsert_serviceorder(
    payload: ServiceOrderIn,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    existing = (
        db.query(ServiceOrder)
        .filter(ServiceOrder.so == payload.so)
        .first()
    )

    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)

        db.commit()
        return {"result": "updated", "so": payload.so}

    rec = ServiceOrder(**payload.model_dump())

    db.add(rec)
    db.commit()
    db.refresh(rec)

    set_order_status(
        db,
        rec,
        "OPEN",
        "Serviceorder aangemaakt",
    )

    return {"result": "created", "so": payload.so}


@router.get("/overview", response_model=List[ServiceOrderOverview])
def list_serviceorders_overview(
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    orders = (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.supplier),
            joinedload(ServiceOrder.customer),
        )
        .order_by(ServiceOrder.created_at.desc())
        .all()
    )

    return orders


@router.get("/{so}", response_model=ServiceOrderIn)
def get_serviceorder(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")
    return order


# ==================================================
# SERVICE ORDER ITEMS
# ==================================================

@router.post("/{so}/items/replace")
def replace_items(
    so: str,
    items: List[ServiceOrderItemIn],
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    db.query(ServiceOrderItem).filter(
        ServiceOrderItem.serviceorder_id == order.id
    ).delete()

    for item in items:
        db.add(ServiceOrderItem(
            serviceorder_id=order.id,
            **item.model_dump()
        ))

    db.commit()
    return {"result": "ok", "count": len(items)}


@router.get("/{so}/items", response_model=List[ServiceOrderItemOut])
def get_items(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    return (
        db.query(ServiceOrderItem)
        .filter(ServiceOrderItem.serviceorder_id == order.id)
        .all()
    )


@router.post("/{so}/items/{item_id}/receive")
def receive_item(
    so: str,
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    item = db.query(ServiceOrderItem).filter(
        ServiceOrderItem.id == item_id,
        ServiceOrderItem.serviceorder_id == order.id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    if not item.bestellen:
        raise HTTPException(400, "Item was not ordered")

    item.ontvangen = True
    item.received_at = datetime.utcnow()
    db.commit()

    remaining = db.query(ServiceOrderItem).filter(
        ServiceOrderItem.serviceorder_id == order.id,
        ServiceOrderItem.bestellen == True,
        ServiceOrderItem.ontvangen == False
    ).count()

    if remaining == 0:
        set_order_status(
            db,
            order,
            "ONTVANGEN",
            "Alle bestelde artikelen zijn ontvangen",
        )
    else:
        log_event(
            db,
            order,
            "DEELONTVANGST",
            f"Artikel {item.part_no} ontvangen",
        )

    return {"status": "ok"}

@router.put("/{so}/po")
def update_serviceorder_po(
    so: str,
    payload: dict,  # { "po": "12345" }
    db: Session = Depends(get_db),
    user=Depends(require_min_role(UserRole.user)),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()

    if not order:
        raise HTTPException(404, "Serviceorder not found")

    order.po = payload.get("po")
    db.commit()

    log_event(
        db,
        order,
        "PO_UPDATED",
        f"PO gewijzigd naar {order.po or '-'}"
    )

    return {"status": "ok", "po": order.po}



# ==================================================
# ARTICLES (kan later naar eigen router)
# ==================================================

@router.get("/articles/{part_no}", response_model=ArticleOut)
def get_article(
    part_no: str = Path(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    rec = db.query(Article).filter(Article.part_no == part_no).first()
    if not rec:
        raise HTTPException(404, "Article not found")
    return rec


# ==================================================
# DOCUMENTS
# ==================================================

@router.get("/{so}/packing-slip/customer")
def packing_slip_customer(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    pdf_path = build_packing_slip_pdf(db, order, mode="customer")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"PackingSlip_{order.so}.pdf",
    )


@router.get("/{so}/packing-slip/internal")
def packing_slip_internal(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    pdf_path = build_packing_slip_pdf(db, order, mode="internal")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"PackingSlip_INTERNAL_{order.so}.pdf",
    )


@router.get("/mail/stock-order/pdf/{so}")
def preview_stock_order_pdf(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == order.supplier_id)
        .first()
    )

    if not supplier or not supplier.email_general:
        raise HTTPException(400, "Supplier email not configured")

    pdf_path = build_stock_order_pdf(db, order, supplier.email_general)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=os.path.basename(pdf_path),
    )


@router.post("/{so}/order/send")
def send_stock_order(
    so: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    

    set_order_status(
        db,
        order,
        "BESTELD",
        "Stock order sent to supplier",
    )

    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == order.supplier_id)
        .first()
    )

    mail = build_stock_order_mail(db, order)

    # async verzenden
    background.add_task(
        send_mail,
        mail["to"],
        mail["subject"],
        mail["body_html"],
        mail.get("pdf_path"),
    )

    return {
        "status": "sent",
        "pdf": mail.get("pdf_path"),
    }


# =====================================
# Mail Previews
# =====================================

@router.post(
    "/{so}/mail/leadtime/preview",
    response_model=MailPreviewOut,
)
def preview_supplier_leadtime_mail(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    return build_supplier_leadtime_mail(db, so)


@router.post(
    "/{so}/mail/offer/preview",
    response_model=MailPreviewOut,
)
def preview_offer_mail(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    return build_offer_mail(db, so)


@router.post(
    "/{so}/mail/order-confirmation/preview",
    response_model=MailPreviewOut,
)
def preview_order_confirmation_mail(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    return build_order_confirmation_mail(db, so)


# =====================================
# ✅ Mail SEND (nieuw)
# =====================================

@router.post("/{so}/mail/leadtime/send")
def send_supplier_leadtime_mail(
    so: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    mail = build_supplier_leadtime_mail(db, so)

    # async verzenden
    background.add_task(
        send_mail,
        mail["to"],
        mail["subject"],
        mail["body_html"],
    )

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    set_order_status(
        db,
        order,
        "LEADTIME_AANGEVRAAGD",
        "Leadtime mail sent to supplier",
    )

    return {"status": "sent"}


@router.post("/{so}/mail/offer/send")
def send_offer_mail(
    so: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    mail = build_offer_mail(db, so)

    background.add_task(
        send_mail,
        mail["to"],
        mail["subject"],
        mail["body_html"],
    )

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    set_order_status(
        db,
        order,
        "OFFER_VERSTUURD",
        "Offer mail sent to customer",
    )

    return {"status": "sent"}


@router.post("/{so}/mail/order-confirmation/send")
def send_order_confirmation_mail(
    so: str,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    mail = build_order_confirmation_mail(db, so)

    background.add_task(
        send_mail,
        mail["to"],
        mail["subject"],
        mail["body_html"],
    )

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    set_order_status(
        db,
        order,
        "CONFIRMATIE_VERSTUURD",
        "Order confirmation sent to customer",
    )

    return {"status": "sent"}


@router.get("/{so}/order/pdf")
def get_stock_order_pdf(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    # optioneel: check items marked for ordering
    items = (
        db.query(ServiceOrderItem)
        .filter(
            ServiceOrderItem.serviceorder_id == order.id,
            ServiceOrderItem.bestellen == True
        )
        .all()
    )
    if not items:
        raise HTTPException(400, "No items marked for ordering")

    pdf_path = build_stock_order_pdf(db, order)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"StockOrder_{order.so}.pdf",
    )


@router.get("/{so}/order/preview")
def preview_stock_order(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    supplier = (
        db.query(Supplier)
        .filter(Supplier.id == order.supplier_id)
        .first()
    )

    if not supplier or not supplier.email_general:
        raise HTTPException(400, "Supplier email not configured")

    items = (
        db.query(ServiceOrderItem)
        .filter(
            ServiceOrderItem.serviceorder_id == order.id,
            ServiceOrderItem.bestellen == True
        )
        .all()
    )
    if not items:
        raise HTTPException(400, "No items marked for ordering")

    # PDF bouwen
    pdf_path = build_stock_order_pdf(db, order)

    subject = f"Stock Order {order.so}"
    body_html = f"""
    <p>Dear {supplier.supplier_contact},</p>

    <p>
        Please find attached our Stock Order for service order
        <b>{order.so}</b>.
    </p>

    <p>Kind regards,<br/>Maconet B.V.</p>
    """

    return {
        "to": supplier.email_general,
        "subject": subject,
        "body_html": body_html,
        "pdf": os.path.basename(pdf_path),
        "pdf_path": pdf_path,
    }


# =========================================
# Status updates
# =========================================

@router.post("/{so}/mail/offer/mark-sent")
def mark_offer_sent(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    set_order_status(
        db,
        order=db.query(ServiceOrder).filter(ServiceOrder.so == so).first(),
        status="OFFER_VERSTUURD",
        message="Offer mail sent to customer",
    )

    return {"status": "ok"}


@router.post("/{so}/mail/order-confirmation/mark-sent")
def mark_order_confirmation_sent(
    so: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    set_order_status(
        db,
        order=db.query(ServiceOrder).filter(ServiceOrder.so == so).first(),
        status="CONFIRMATIE_VERSTUURD",
        message="Order confirmation sent to customer",
    )

    return {"status": "ok"}


@router.post("/{so}/transition")
def transition_serviceorder(
    so: str,
    payload: ServiceOrderStatusTransition,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(ServiceOrder)
        .filter(ServiceOrder.so == so)
        .first()
    )

    if not order:
        raise HTTPException(404, "Serviceorder not found")

    current = ServiceOrderStatusEnum(order.status)
    target = payload.to

    allowed = SERVICEORDER_ALLOWED_TRANSITIONS.get(current, [])

    if target not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Transition {current} → {target} not allowed"
        )

    order.status = target
    db.commit()

    return {"so": so, "status": target}


@router.get("/{so}/allowed-statuses")
def get_allowed_statuses(
    so: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    order = (
        db.query(ServiceOrder)
        .filter(ServiceOrder.so == so)
        .first()
    )

    if not order:
        # Nieuwe SO
        current = ServiceOrderStatusEnum.OPEN
    else:
        current = ServiceOrderStatusEnum(order.status)

    allowed = SERVICEORDER_ALLOWED_TRANSITIONS.get(current, [])

    return {
        "current": current,
        "allowed": allowed,
    }


# ================================
# t.b.v Merging
# ================================

@router.get("/for-po-merge", response_model=list[ServiceOrderForPOMergeOut])
def list_serviceorders_for_po_merge(
    db: Session = Depends(get_db),
    user: User = Depends(require_min_role(UserRole.user)),
):
    orders = (
        db.query(ServiceOrder)
        .options(
            joinedload(ServiceOrder.customer),
            joinedload(ServiceOrder.supplier),
        )
        .order_by(ServiceOrder.created_at.desc())
        .all()
    )

    out: list[ServiceOrderForPOMergeOut] = []

    for o in orders:
        # ---- klant/leverancier display met fallbacks ----
        customer_display = (
            getattr(o, "customer_name_free", None)
            or (o.customer.name if getattr(o, "customer", None) else None)
            or "—"
        )
        supplier_display = (
            getattr(o, "supplier_name_free", None)
            or (o.supplier.name if getattr(o, "supplier", None) else None)
            or "—"
        )

        # ---- totaal (jouw pricing geeft key 'total') ----
        order_total = 0.0
        try:
            pricing = calculate_order_totals(db, o)
            order_total = float(pricing.get("total") or 0.0)
        except Exception:
            # niet hard falen op 1 order; alleen totaal blijft 0
            order_total = 0.0

        out.append(
            ServiceOrderForPOMergeOut(
                so=o.so,
                date=getattr(o, "date", None) or getattr(o, "created_at", None),
                customer_display=customer_display,
                supplier_display=supplier_display,
                order_total=order_total,
                status=getattr(o, "status", None),
                can_merge=True,
            )
        )

    return out

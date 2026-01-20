# app/services/documents/mail_templates.py

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.serviceorder import ServiceOrder
from app.models.serviceorder_item import ServiceOrderItem
from app.models.customer import Customer, CustomerContact, SullairSettings



from app.services.pricing import calculate_order_totals
from app.services.pricing import format_currency


# ==================================================
# SULLAIR – LEADTIME REQUEST
# ==================================================

def build_sullair_leadtime_mail(db: Session, so: str):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    items = db.query(ServiceOrderItem).filter(
        ServiceOrderItem.serviceorder_id == order.id
    ).all()

    if not items:
        raise HTTPException(400, "No items in serviceorder")

    sullair = db.query(SullairSettings).first()
    if not sullair:
        raise HTTPException(400, "Sullair settings not configured")

    rows = ""
    for idx, it in enumerate(items, start=1):
        rows += f"""
        <tr>
          <td style="text-align:center;">{idx}</td>
          <td>{it.part_no}</td>
          <td>{it.description or ""}</td>
          <td style="text-align:center;">{it.qty}</td>
          <td style="text-align:right;">{format_currency(it.list_price)}</td>
          <td></td>
          <td></td>
        </tr>
        """

    body = f"""
    <div style="font-family: Arial; font-size:14px;">
        <p>Dear {sullair.contact_name or 'Sir or Madam'},</p>

        <p>
            We kindly request, with serviceorder number
            <b>{order.so}</b>, the leadtimes for the following items:
        </p>

        <table style="border-collapse:collapse;width:100%;">
            <tr>
                <th style="border:1px solid #000;padding:6px;">Item</th>
                <th style="border:1px solid #000;padding:6px;">Part No</th>
                <th style="border:1px solid #000;padding:6px;">Description</th>
                <th style="border:1px solid #000;padding:6px;">Qty</th>
                <th style="border:1px solid #000;padding:6px;">Price Each</th>
                <th style="border:1px solid #000;padding:6px;">Leadtime NL</th>
                <th style="border:1px solid #000;padding:6px;">Comments</th>
            </tr>
            {rows}
        </table>

        <p>Kind regards,<br/><b>Maconet B.V.</b></p>
    </div>
    """

    return {
        "to": sullair.email,
        "subject": f"Leadtime request service order {order.so}",
        "body_html": body,
    }


# ==================================================
# OFFER MAIL (QUOTATION)
# ==================================================

def build_offer_mail(db: Session, so: str):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    try:

        pricing = calculate_order_totals(db, order)
    except ValueError as e:
        raise HTTPException(
                status_code=400,
                detail=f"Pricing fout voor serviceorder {so}: {e}"
        )

    items = db.query(ServiceOrderItem).filter(
        ServiceOrderItem.serviceorder_id == order.id
    ).all()

    customer = db.query(Customer).filter(
        Customer.name == order.supplier
    ).first()
    if not customer:
        raise HTTPException(400, "Customer not found")

    contact = db.query(CustomerContact).filter(
        CustomerContact.customer_id == customer.id,
        CustomerContact.is_primary == True
    ).first()
    if not contact:
        raise HTTPException(400, "No primary contact for customer")

    has_leadtimes = any((it.leadtime or "").strip() for it in items)

    rows = ""
    for idx, it in enumerate(pricing["items"], start=1):
        db_item = next(x for x in items if x.part_no == it["part_no"])
        lead = db_item.leadtime or ""

        rows += f"""
        <tr>
            <td>{idx}</td>
            <td>{it['part_no']}</td>
            <td>{it['description']}</td>
            <td style="text-align:right;">{it['qty']}</td>
            <td style="text-align:right;">{format_currency(it['price_each'])}</td>
            {f"<td>{lead}</td>" if has_leadtimes else ""}
            <td style="text-align:right;">{format_currency(it['line_total'])}</td>
        </tr>
        """

    leadtime_note = (
        "" if has_leadtimes
        else "<p><i>Leadtimes are requested from our supplier.</i></p>"
    )

    body = f"""
    <div style="font-family: Arial; font-size:14px;">
        <p>Dear {contact.contact_name},</p>

        <p>
            Please find below our quotation for service order
            <b>{order.so}</b>.
        </p>

        {leadtime_note}

        <table style="border-collapse:collapse;width:100%;">
            <tr>
                <th>Item</th>
                <th>Part No</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Price</th>
                {f"<th>Leadtime</th>" if has_leadtimes else ""}
                <th>Line total</th>
            </tr>
            {rows}
        </table>

        <p>
            <b>Total ({pricing['price_type']}):
            {format_currency(pricing['total'])}</b>
        </p>

        <p>Kind regards,<br/>Maconet B.V.</p>
    </div>
    """

    return {
        "to": contact.email,
        "subject": f"Quotation for service order {order.so}",
        "body_html": body,
    }


# ==================================================
# ORDER CONFIRMATION
# ==================================================

def build_order_confirmation_mail(db: Session, so: str):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    pricing = calculate_order_totals(db, order)

    items = db.query(ServiceOrderItem).filter(
        ServiceOrderItem.serviceorder_id == order.id,
        ServiceOrderItem.bestellen == True
    ).all()

    if not items:
        raise HTTPException(400, "No items marked for ordering")

    customer = db.query(Customer).filter(
        Customer.name == order.supplier
    ).first()
    if not customer:
        raise HTTPException(400, "Customer not found")

    contact = db.query(CustomerContact).filter(
        CustomerContact.customer_id == customer.id,
        CustomerContact.is_primary == True
    ).first()
    if not contact:
        raise HTTPException(400, "No primary contact for customer")

    rows = ""
    total = 0.0

    for idx, it in enumerate(pricing["items"], start=1):
        total += it["line_total"]
        rows += f"""
        <tr>
            <td>{idx}</td>
            <td>{it['part_no']}</td>
            <td>{it['description']}</td>
            <td style="text-align:right;">{it['qty']}</td>
            <td style="text-align:right;">{format_currency(it['price_each'])}</td>
            <td style="text-align:right;">{format_currency(it['line_total'])}</td>
        </tr>
        """

    body = f"""
    <div style="font-family: Arial; font-size:14px;">
        <p>Dear {contact.contact_name},</p>

        <p>
            Please find below our order confirmation for service order
            <b>{order.so}</b>.
        </p>

        <table style="border-collapse:collapse;width:100%;">
            <tr>
                <th>Item</th>
                <th>Part No</th>
                <th>Description</th>
                <th>Qty</th>
                <th>Price</th>
                <th>Line total</th>
            </tr>
            {rows}
            <tr>
                <td colspan="5" style="text-align:right;"><b>Total</b></td>
                <td style="text-align:right;"><b>{format_currency(total)}</b></td>
            </tr>
        </table>

        <p>Kind regards,<br/>Maconet B.V.</p>
    </div>
    """

    return {
        "to": contact.email,
        "subject": f"Order confirmation service order {order.so}",
        "body_html": body,
    }

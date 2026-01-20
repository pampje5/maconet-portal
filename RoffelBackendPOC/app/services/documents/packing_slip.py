# app/services/documents/packing_slip.py

from datetime import date
import os
import uuid

from sqlalchemy.orm import Session
from fastapi import HTTPException

from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, Image
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

from app.models.serviceorder import ServiceOrder
from app.models.serviceorder_item import ServiceOrderItem
from app.models.customer import Customer
from app.services.pricing import get_price_for_item, format_currency


# ==================================================
# Data helper
# ==================================================

def get_packing_slip_data(db: Session, order: ServiceOrder):
    customer = (
        db.query(Customer)
        .filter(Customer.name == order.supplier)
        .first()
    )
    if not customer:
        raise HTTPException(400, "Customer not found for serviceorder")

    items = (
        db.query(ServiceOrderItem)
        .filter(
            ServiceOrderItem.serviceorder_id == order.id,
            ServiceOrderItem.ontvangen == True
        )
        .all()
    )

    if not items:
        raise HTTPException(400, "No received items")

    lines = []
    for it in items:
        lines.append({
            "part_no": it.part_no,
            "description": it.description or "",
            "qty": it.qty or 0,
            "leadtime": it.leadtime or "",
            "price_each": get_price_for_item(
                it,
                customer.price_type or "BRUTO"
            ) or 0.0,
        })

    return {
        "so": order.so,
        "po": order.po or "",
        "customer_ref": order.customer_ref or "",
        "customer": {
            "name": customer.name,
            "address": customer.address or "",
            "zipcode": customer.zipcode or "",
            "city": customer.city or "",
            "country": customer.country or "",
        },
        "price_type": customer.price_type or "BRUTO",
        "lines": lines,
    }


# ==================================================
# PDF builder
# ==================================================

def build_packing_slip_pdf(
    db: Session,
    order: ServiceOrder,
    mode: str = "customer",  # customer | internal
) -> str:
    """
    mode:
      - customer  -> zonder prijzen
      - internal  -> met prijzen + totalen
    """

    data = get_packing_slip_data(db, order)
    show_prices = (mode == "internal")

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../../"))

    LOGO = os.path.join(BASE_DIR, "assets", "Maconet.png")

    tmp_dir = os.path.join(BASE_DIR, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    filename = os.path.join(
        tmp_dir,
        f"packing_slip_{order.so}_{uuid.uuid4().hex}.pdf"
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Packing slip {order.so}",
    )

    elements = []
    content_w = doc.width

    # ================= Header =================

    if os.path.exists(LOGO):
        logo = Image(LOGO, width=50 * mm, height=23 * mm)
    else:
        logo = Paragraph("<b>Maconet B.V.</b>", normal)

    header = Table(
        [
            ["", logo],
            ["", "Valkenierstraat 23"],
            ["", "2984 AZ Ridderkerk"],
            ["", "The Netherlands"],
            ["", "+31 180 410 755"],
        ],
        colWidths=[content_w * 0.60, content_w * 0.40],
    )
    header.setStyle(TableStyle([
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("VALIGN", (1,0), (1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 10 * mm))

    # ================= Title =================

    today = date.today().strftime("%d-%m-%Y")
    title = "PACKING SLIP" if not show_prices else "PACKING SLIP (INTERNAL)"

    top = Table(
        [[Paragraph(f"<b>{title}</b>", normal), f"Ridderkerk, {today}"]],
        colWidths=[content_w * 0.65, content_w * 0.35],
    )
    top.setStyle(TableStyle([
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(top)
    elements.append(Spacer(1, 6 * mm))

    # ================= Customer block =================

    c = data["customer"]

    left = [
        Paragraph(f"<b>{c['name']}</b>", normal),
        Paragraph(c["address"], normal),
        Paragraph(f"{c['zipcode']} {c['city']}".strip(), normal),
        Paragraph(c["country"], normal),
    ]

    right = [
        Paragraph(f"<b>SO:</b> {data['so']}", normal),
        Paragraph(f"<b>PO:</b> {data['po']}", normal),
        Paragraph(f"<b>Customer ref:</b> {data['customer_ref']}", normal),
    ]

    info = Table(
        [[left, right]],
        colWidths=[content_w * 0.60, content_w * 0.40],
    )
    info.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(info)
    elements.append(Spacer(1, 8 * mm))

    # ================= Items table =================

    headers = ["Item", "Part No", "Description", "Qty"]
    if show_prices:
        headers += ["Price", "Line total"]

    table_data = [headers]

    total = 0.0
    for idx, line in enumerate(data["lines"], start=1):
        qty = line["qty"]
        price = line["price_each"]
        line_total = qty * price
        total += line_total

        row = [
            str(idx),
            line["part_no"],
            Paragraph(line["description"].replace("\n", "<br/>"), normal),
            str(qty),
        ]

        if show_prices:
            row += [
                format_currency(price),
                format_currency(line_total),
            ]

        table_data.append(row)

    if show_prices:
        table_data.append([
            "", "", "", "",
            "Total",
            format_currency(total),
        ])

    if show_prices:
        widths = [
            content_w * 0.06,
            content_w * 0.16,
            content_w * 0.38,
            content_w * 0.08,
            content_w * 0.16,
            content_w * 0.16,
        ]
    else:
        widths = [
            content_w * 0.07,
            content_w * 0.20,
            content_w * 0.53,
            content_w * 0.20,
        ]

    tbl = Table(table_data, colWidths=widths)
    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))

    elements.append(tbl)
    elements.append(Spacer(1, 10 * mm))
    elements.append(Paragraph("Kind regards,", normal))
    elements.append(Paragraph("Maconet B.V.", normal))

    doc.build(elements)
    return filename

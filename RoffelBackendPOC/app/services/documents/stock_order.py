# app/services/documents/stock_order.py

import os
import uuid
from datetime import date

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
from app.models.customer import SullairSettings
from app.services.pricing import format_currency


# ==================================================
# DATA
# ==================================================

def get_stock_order_items(db: Session, order: ServiceOrder):
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

    lines = []
    total_net = 0.0

    for it in items:
        qty = it.qty or 0
        list_price = it.list_price or 0.0
        purchase = it.price_purchase or 0.0

        net = qty * purchase
        total_net += net

        lines.append({
            "part_no": it.part_no,
            "description": it.description or "",
            "qty": qty,
            "price_each": list_price,
            "net_amount": net,
        })

    return lines, round(total_net, 2)


# ==================================================
# PDF
# ==================================================

def build_stock_order_pdf(db: Session, order: ServiceOrder) -> str:
    sullair = db.query(SullairSettings).first()
    if not sullair:
        raise HTTPException(400, "Sullair settings not configured")

    lines, total_net = get_stock_order_items(db, order)

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    BASE_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../")
    )
    LOGO = os.path.join(BASE_DIR, "assets", "Maconet.png")

    tmp_dir = os.path.join(BASE_DIR, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    filename = os.path.join(
        tmp_dir,
        f"stockorder_{order.so}_{uuid.uuid4().hex}.pdf"
    )

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Stock Order {order.so}",
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
    elements.append(Spacer(1, 20))

    # ================= Reference =================

    today = date.today().strftime("%d-%m-%Y")
    ref = Table(
        [[f"Our reference: {order.so}/{order.po or ''}", f"Ridderkerk, {today}"]],
        colWidths=[content_w * 0.65, content_w * 0.35],
    )
    ref.setStyle(TableStyle([
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(ref)
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        f"Dear {sullair.contact_name or 'Sir or Madam'},", normal
    ))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Herewith we send you our Stock order:", normal
    ))
    elements.append(Spacer(1, 10))

    # ================= Items =================

    table_data = [[
        "Item", "Part No", "Description",
        "Qty", "Price Each", "Net Amount"
    ]]

    for idx, line in enumerate(lines, start=1):
        table_data.append([
            str(idx),
            line["part_no"],
            Paragraph(line["description"], normal),
            str(line["qty"]),
            format_currency(line["price_each"]),
            format_currency(line["net_amount"]),
        ])

    table_data.append([
        "", "", "", "",
        "Total amount",
        format_currency(total_net),
    ])

    widths = [
        content_w * 0.06,
        content_w * 0.16,
        content_w * 0.38,
        content_w * 0.08,
        content_w * 0.16,
        content_w * 0.16,
    ]

    tbl = Table(table_data, colWidths=widths)
    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-2), 0.5, colors.black),
        ("GRID", (0,-1), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("ALIGN", (3,1), (-1,-1), "RIGHT"),
        ("FONTNAME", (4,-1), (5,-1), "Helvetica-Bold"),
        ("LINEABOVE", (0,-1), (-1,-1), 1.0, colors.black),
        ("SPAN", (0,-1), (3,-1)),
    ]))

    elements.append(tbl)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Kind regards,", normal))
    elements.append(Paragraph("Maconet B.V.", normal))

    doc.build(elements)
    return filename

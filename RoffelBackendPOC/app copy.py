from datetime import datetime, timezone, timedelta, date
from typing import Optional, List

from fastapi import FastAPI, Header, HTTPException, Path, Depends, Body
from pydantic import BaseModel, EmailStr
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey,
    Float, Boolean, UniqueConstraint, Enum
)

from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

from passlib.context import CryptContext
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
import os
import uuid
import enum
import io


import secrets



# ============================
# CONFIGURATION
# ============================

API_KEY = "CHANGE_ME"
JWT_SECRET = "CHANGE_ME_JWT_SECRET"
JWT_ALG = "HS256"

DATABASE_URL = "sqlite:///roffel_tool.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ============================
# FASTAPI INIT
# ============================

app = FastAPI(title="Roffel Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # belangrijk: laat OPTIONS toe
    allow_headers=["*"],
)

# ============================
# DEPENDENCY
# ============================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================
# (SECURITY) HELPERS
# ============================

pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)

class ServiceOrderNrStatus(str, enum.Enum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def check_api_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

def get_user_from_jwt_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")

    token = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class UserRole(str, enum.Enum):
    user = "user"
    designer = "designer"
    admin = "admin"

ROLE_LEVEL = {
    UserRole.user: 1,
    UserRole.admin: 5,
    UserRole. designer: 10,
}





# ============================
# DATABASE MODELS
# ============================

class ServiceOrder(Base):
    __tablename__ = "serviceorders"

    id = Column(Integer, primary_key=True, index=True)
    so = Column(String, unique=True, index=True, nullable=False)
    supplier = Column(String)
    customer_ref = Column(String)
    po = Column(String)
    status = Column(String)
    price_type = Column(String)
    employee = Column(String)
    remarks = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class ServiceOrderItem(Base):
    __tablename__ = "serviceorder_items"

    id = Column(Integer, primary_key=True)
    serviceorder_id = Column(Integer, ForeignKey("serviceorders.id"))

    part_no = Column(String, nullable=False)
    description = Column(String)
    qty = Column(Integer)

    list_price = Column(Float)
    price_bruto = Column(Float)
    price_wvk = Column(Float)
    price_edmac = Column(Float)
    price_purchase = Column(Float)

    leadtime = Column(String)
    bestellen = Column(Boolean, default=False)

    ontvangen = Column(Boolean, default=False)
    received_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)
    part_no = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)

    list_price = Column(Float)
    price_bruto = Column(Float)
    price_wvk = Column(Float)
    price_edmac = Column(Float)
    price_purchase = Column(Float)

    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    role = Column(
        Enum(UserRole),
        default=UserRole.user,
        nullable=False
    )

    is_admin = Column(Boolean, default=False)

    reset_token = Column(String, nullable = True)
    reset_expires = Column(DateTime, nullable = True)

    created_at = Column(DateTime, default=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    contact = Column(String, nullable=True)
    email = Column(String, nullable=True)
    price_type = Column(String, nullable=True)

    # ✅ NAW velden (nieuw)
    address = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class CustomerContact(Base):
    __tablename__ = "customer_contacts"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    contact_name = Column(String, nullable=False)
    email = Column(String, nullable=False)

    is_primary = Column(Boolean, default=False)  # ✅ toegevoegd

    created_at = Column(DateTime, default=datetime.utcnow)

class SullairSettings(Base):
    __tablename__ = "sullair_settings"

    id = Column(Integer, primary_key=True)

    contact_name = Column(String, nullable=True)
    email = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

class ServiceOrderLog(Base):
    __tablename__ = "serviceorder_logs"

    id = Column(Integer, primary_key=True)
    serviceorder_id = Column(Integer, ForeignKey("serviceorders.id"))
    action = Column(String)        # bv: "AANGEVRAAGD", "OFFERTE"
    message = Column(String)       # bv: "Aanvraag verstuurd naar Sullair"
    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerPriceRule(Base):
    __tablename__ = "customer_price_rules"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    min_amount = Column(Float, nullable=False)
    price_type = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

class ServiceOrderNumber(Base):
    __tablename__ = "service_order_numbers"

    id = Column(Integer, primary_key=True)

    so_number = Column(String, nullable=False, unique=True, index=True)

    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    sequence = Column(Integer, nullable=False)

    date = Column(DateTime, nullable=False, default=datetime.utcnow)

    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name_free = Column(String, nullable=True)

    supplier = Column(String, nullable=True)
    description = Column(String, nullable=True)
    type = Column(String(2), nullable=True)

    offer = Column(Boolean, default=False)
    offer_amount = Column(Float, nullable=True)

    status = Column(
        Enum(ServiceOrderNrStatus),
        nullable=False,
        default=ServiceOrderNrStatus.FREE,
        index=True,
    )

    reserved_by = Column(String, nullable=True)
    reserved_at = Column(DateTime, nullable=True)
    confirmed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("year", "sequence", name="uq_so_year_sequence"),
    )


Base.metadata.create_all(bind=engine)

# ============================
# AUTH DEPENDENCIES
# ============================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

        if "role" in payload:
            user.role = payload["role"]


    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def require_min_role(min_role: UserRole):
    def _guard(user: User = Depends(get_current_user)):
        user_level = ROLE_LEVEL[user.role]
        required_level = ROLE_LEVEL[min_role]

        if user_level < required_level:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions"
            )
        return user
    return _guard
  


def create_access_token(user: User) -> str:
    payload = {
        "sub": user.email,
        "role": user.role.value,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

@app.get("/auth/me")
def read_me(user: User = Depends(get_current_user)):
    return {
        "email": user.email,
        "is_admin": user.is_admin,
    }



# ============================
# BUSINESS / DOCUMENT HELPERS
# ============================
def set_order_status(db, order: ServiceOrder, status: str, message: str):
    order.status = status

    log = ServiceOrderLog(
        serviceorder_id=order.id,
        action=status,
        message=message
    )

    db.add(log)
    db.commit()

def log_event(db, so: ServiceOrder, action: str, message: str):
    db.add(ServiceOrderLog(
        serviceorder_id=so.id,
        action=action,
        message=message
    ))
    db.commit()


def format_currency(value):
    if value is None:
        return ""
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")



def get_price_for_item(item, price_type: str) -> float | None:
    """
    Geeft de juiste prijs terug voor een ServiceOrderItem
    op basis van price_type
    """
    price_map = {
        "LIST": item.list_price,
        "BRUTO": item.price_bruto,
        "WVK": item.price_wvk,
        "EDMAC": item.price_edmac,
        "PURCHASE": item.price_purchase,
    }

    return price_map.get(price_type)

def determine_price_type_for_customer(
    db: Session,
    customer_id: int,
    order_total: float,
    default_price_type: str | None
) -> str:
    """
    Bepaalt het juiste prijs_type op basis van:
    - klant staffels
    - order totaal
    - fallback naar basis prijstype
    """

    rules = (
        db.query(CustomerPriceRule)
        .filter(CustomerPriceRule.customer_id == customer_id)
        .order_by(CustomerPriceRule.min_amount.asc())
        .all()
    )

    selected = default_price_type

    for rule in rules:
        if order_total >= rule.min_amount:
            selected = rule.price_type

    return selected or default_price_type or "BRUTO"

def calculate_order_totals(
    db: Session,
    order,
):
    items = (
        db.query(ServiceOrderItem)
        .filter(ServiceOrderItem.serviceorder_id == order.id)
        .all()
    )

    customer = (
        db.query(Customer)
        .filter(Customer.name == order.supplier)
        .first()
    )

    if not customer:
        raise ValueError("Customer not found for serviceorder")

    # eerst: basisprijs (voor staffelcheck)
    base_total = 0.0
    for it in items:
        price = get_price_for_item(it, customer.price_type or "BRUTO")
        if price:
            base_total += price * it.qty

    # bepaal definitief prijstype
    final_price_type = determine_price_type_for_customer(
        db=db,
        customer_id=customer.id,
        order_total=base_total,
        default_price_type=customer.price_type
    )

    # herbereken met definitieve prijs
    final_total = 0.0
    priced_items = []

    for it in items:
        price = get_price_for_item(it, final_price_type) or 0.0
        line_total = price * it.qty

        final_total += line_total

        priced_items.append({
            "part_no": it.part_no,
            "description": it.description,
            "qty": it.qty,
            "price_each": price,
            "line_total": line_total,
        })

    return {
        "price_type": final_price_type,
        "total": round(final_total, 2),
        "items": priced_items,
    }

def get_stock_order_data(db: Session, order: ServiceOrder):
    """
    Dataset voor Hitachi / Sullair stock orders
    - Price Each = list_price
    - Net Amount = qty * price_purchase
    """

    items = (
        db.query(ServiceOrderItem)
        .filter(ServiceOrderItem.serviceorder_id == order.id)
        .all()
    )

    if not items:
        raise ValueError("No items in serviceorder")

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
            "price_each": list_price,      # 👈 what supplier sees
            "net_amount": net,             # 👈 what they charge
        })

    return {
        "lines": lines,
        "total": round(total_net, 2)
    }


from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
import os, uuid, io
from datetime import date

def build_stock_order_pdf(db: Session, order: ServiceOrder, supplier_email: str):
    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOGO = os.path.join(BASE_DIR, "assets", "Maconet.png")

    # Zorg voor een tmp map die ook op Windows werkt
    tmp_dir = os.path.join(BASE_DIR, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    filename = os.path.join(tmp_dir, f"stockorder_{order.so}_{uuid.uuid4().hex}.pdf")

    # Marges: hiermee krijg je een nette linkermarge en matchen alle blokken
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"Stock Order {order.so}"
    )

    elements = []
    content_w = doc.width  # <<< cruciaal: alles hierop baseren

    # =========================
    # Header: logo rechtsboven
    # =========================
    if os.path.exists(LOGO):
        logo = Image(LOGO, width=50*mm, height=23*mm)  # schaalbaar
    else:
        logo = Paragraph("<b>Maconet B.V.</b>", normal)

    header = Table(
    [
        ["", logo],
        ["", Paragraph("Valkenierstraat 23", normal)],
        ["", Paragraph("2984 AZ Ridderkerk", normal)],
        ["", Paragraph("The Netherlands", normal)],
        ["", Paragraph("+31 180 410 755", normal)],
    ],
    colWidths=[350, 150],
    )

    header.setStyle(TableStyle([
        ("ALIGN", (1,0), (1,-1), "RIGHT"),
        ("VALIGN", (1,0), (1,-1), "TOP"),

        ("ALIGN",(1,1), (1,-1), "LEFT"),

        ("TOPPADDING", (1,1), (1,-1), 2),
        ("BOTTOMPADDING", (1,1), (1,-1), 2),
        ("LEFTPADDING", (1,0), (1,-1), 0),
        ("RIGHTPADDING", (1,0), (1,-1), 0),
    ]))

    elements.append(header)
    elements.append(Spacer(1, 25))

    # =========================
    # Ontvanger (links)
    # =========================
    elements.append(Paragraph("Hitachi Global Air Power Company", normal))
    elements.append(Paragraph("Attn. Europe Sales", normal))
    elements.append(Spacer(1, 6*mm))

    # =========================
    # Reference links + datum rechts
    # (Our reference iets naar rechts: door linkerkolom iets smaller + padding)
    # =========================
    today = date.today().strftime("%d-%m-%Y")
    ref_left = f"Our reference: {order.so}/{order.po or ''}"

    ref_tbl = Table(
        [[ref_left, f"Ridderkerk, {today}"]],
        colWidths=[content_w * 0.62, content_w * 0.38],
        hAlign="LEFT"
    )
    ref_tbl.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        # hier schuif je "Our reference" optisch iets naar rechts
        ("LEFTPADDING", (0,0), (0,0), 0),
        ("RIGHTPADDING", (1,0), (1,0), 0),
        ("LEFTPADDING", (1,0), (1,0), 0),
        ("TOPPADDING", (0,0), (-1,-1), 0),
        ("BOTTOMPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(ref_tbl)
    elements.append(Spacer(1, 8*mm))

    # =========================
    # Aanhef
    # =========================
    sullair = db.query(SullairSettings).first()
    name = (sullair.contact_name if sullair and sullair.contact_name else "Sir or Madam")

    elements.append(Paragraph(f"Dear {name},", normal))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph("Herewith we send you our Stock order:", normal))
    elements.append(Spacer(1, 6*mm))

    # =========================
    # Items (alleen bestellen == True)
    # Price Each = list_price
    # Net Amount = qty * price_purchase
    # =========================
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

    # Kolommen: maak ze optisch netjes binnen doc.width
    # (totaal = content_w)
    col_item = content_w * 0.06
    col_part = content_w * 0.16
    col_desc = content_w * 0.44
    col_qty  = content_w * 0.08
    col_each = content_w * 0.14
    col_net  = content_w * 0.14

    table_data = [[
        "Item", "Part No", "Description", "Qty", "Price Each", "Net Amount"
    ]]

    total_net = 0.0

    for idx, it in enumerate(items, start=1):
        qty = it.qty or 0
        price_each = it.list_price or 0.0
        net = (it.price_purchase or 0.0) * qty
        total_net += net

        # Paragraph voor description voorkomt rare layout als tekst langer wordt
        desc = Paragraph((it.description or "").replace("\n", "<br/>"), normal)

        table_data.append([
            str(idx),
            it.part_no or "",
            desc,
            str(qty),
            format_currency(price_each),
            format_currency(net),
        ])

    # Total row (label + totaal onder Net Amount)
    table_data.append(["", "", "", "", "Total amount", format_currency(total_net)])

    tbl = Table(
        table_data,
        colWidths=[col_item, col_part, col_desc, col_qty, col_each, col_net],
        hAlign="LEFT"
    )

    tbl.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-2), 0.5, colors.black),
        ("GRID", (0,-1), (-1,-1), 0.5, colors.black),

        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),

        ("VALIGN", (0,0), (-1,-1), "TOP"),

        ("ALIGN", (0,1), (0,-2), "CENTER"),  # Item
        ("ALIGN", (3,1), (3,-2), "RIGHT"),   # Qty
        ("ALIGN", (4,1), (5,-2), "RIGHT"),   # amounts

        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),

        # Total row styling
        ("FONTNAME", (4,-1), (5,-1), "Helvetica-Bold"),
        ("ALIGN", (4,-1), (5,-1), "RIGHT"),
        ("LINEABOVE", (0,-1), (-1,-1), 1.0, colors.black),
        ("SPAN", (0,-1), (3,-1)),  # leeg blok links samenvoegen
    ]))

    elements.append(tbl)
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("Kind regards,", normal))
    elements.append(Paragraph("Maconet B.V.", normal))

    doc.build(elements)
    return filename

def get_packing_slip_data(db: Session, order: ServiceOrder):
    customer = db.query(Customer).filter(Customer.name == order.supplier).first()
    if not customer:
        raise ValueError("Customer not found for serviceorder")

    items = (
        db.query(ServiceOrderItem)
        .filter(
            ServiceOrderItem.serviceorder_id == order.id,
            ServiceOrderItem.ontvangen == True
        )
        .all()
    )

    if not items:
        raise ValueError("No received items")

    lines = []
    for it in items:
        lines.append({
            "part_no": it.part_no,
            "description": it.description or "",
            "qty": it.qty or 0,
            "leadtime": it.leadtime or "",
            "price_each": get_price_for_item(it, customer.price_type or "BRUTO") or 0.0,
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

from reportlab.lib import colors

def build_packing_slip_pdf(db: Session, order: ServiceOrder, mode: str = "customer"):
    """
    mode:
      - "customer"  -> zonder prijzen
      - "internal"  -> met prijzen + totals
    """
    data = get_packing_slip_data(db, order)
    show_prices = (mode == "internal")

    styles = getSampleStyleSheet()
    normal = styles["Normal"]

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOGO = os.path.join(BASE_DIR, "assets", "Maconet.png")

    tmp_dir = os.path.join(BASE_DIR, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    filename = os.path.join(tmp_dir, f"packing_slip_{order.so}_{uuid.uuid4().hex}.pdf")

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

    # ===== Header: logo rechts + Maconet adres =====
    if os.path.exists(LOGO):
        logo = Image(LOGO, width=50*mm, height=23*mm)
    else:
        logo = Paragraph("<b>Maconet B.V.</b>", normal)

    header = Table(
        [
            ["", logo],
            ["", Paragraph("Valkenierstraat 23", normal)],
            ["", Paragraph("2984 AZ Ridderkerk", normal)],
            ["", Paragraph("The Netherlands", normal)],
            ["", Paragraph("+31 180 410 755", normal)],
        ],
        colWidths=[content_w * 0.60, content_w * 0.40],
        hAlign="LEFT"
    )
    header.setStyle(TableStyle([
        ("VALIGN", (1,0), (1,-1), "TOP"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("ALIGN", (1,1), (1,-1), "LEFT"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
        ("TOPPADDING", (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
    ]))
    elements.append(header)
    elements.append(Spacer(1, 10*mm))

    # ===== Titel + datum =====
    today = date.today().strftime("%d-%m-%Y")
    title = "PACKING SLIP" if not show_prices else "PACKING SLIP (INTERNAL)"
    top_tbl = Table(
        [[Paragraph(f"<b>{title}</b>", normal), f"Ridderkerk, {today}"]],
        colWidths=[content_w*0.65, content_w*0.35],
        hAlign="LEFT"
    )
    top_tbl.setStyle(TableStyle([
        ("ALIGN", (0,0), (0,0), "LEFT"),
        ("ALIGN", (1,0), (1,0), "RIGHT"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(top_tbl)
    elements.append(Spacer(1, 6*mm))

    # ===== Klant NAW links + SO/PO/Ref rechts =====
    c = data["customer"]

    left_block = [
        Paragraph(f"<b>{c['name']}</b>", normal),
        Paragraph(c["address"], normal),
        Paragraph(f"{c['zipcode']} {c['city']}".strip(), normal),
        Paragraph(c["country"], normal),
    ]

    right_block = [
        Paragraph(f"<b>SO:</b> {data['so']}", normal),
        Paragraph(f"<b>PO:</b> {data['po']}", normal),
        Paragraph(f"<b>Customer ref:</b> {data['customer_ref']}", normal),
    ]

    info_tbl = Table(
        [[left_block, right_block]],
        colWidths=[content_w*0.60, content_w*0.40],
        hAlign="LEFT"
    )
    info_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
        ("RIGHTPADDING", (0,0), (-1,-1), 0),
    ]))
    elements.append(info_tbl)
    elements.append(Spacer(1, 8*mm))

    # ===== Tabel =====
    headers = ["Item", "Part No", "Description", "Qty"]
    if show_prices:
        headers += ["Price", "Line total"]

    table_data = [headers]

    total = 0.0
    for idx, line in enumerate(data["lines"], start=1):
        qty = line["qty"]
        price = line["price_each"] or 0.0
        line_total = qty * price
        total += line_total

        row = [
            str(idx),
            line["part_no"],
            Paragraph(line["description"].replace("\n", "<br/>"), normal),
            str(qty),
        ]

        if show_prices:
            row += [format_currency(price), format_currency(line_total)]

        table_data.append(row)

    if show_prices:
        # total row
        table_data.append(["", "", "", "", "", "Total", format_currency(total)])

    # kolombreedtes binnen doc.width
    if show_prices:
        widths = [
            content_w*0.06,  # item
            content_w*0.16,  # part
            content_w*0.38,  # desc
            content_w*0.08,  # qty
            content_w*0.13,  # price
            content_w*0.13,  # line
        ]
    else:
        widths = [
            content_w*0.07,
            content_w*0.20,
            content_w*0.53,
            content_w*0.20,     
        ]

    tbl = Table(table_data, colWidths=widths, hAlign="LEFT")
    style_cmds = [
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#EEEEEE")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ALIGN", (3,1), (3,-1), "RIGHT"),   # Qty rechts
        ("ALIGN", (4,1), (4,-1), "LEFT"),    # Leadtime links
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]

    if show_prices:
        # prijzen rechts
        style_cmds += [
            ("ALIGN", (5,1), (6,-1), "RIGHT"),
            ("FONTNAME", (-2,-1), (-1,-1), "Helvetica-Bold"),
            ("LINEABOVE", (0,-1), (-1,-1), 1.0, colors.black),
            ("SPAN", (0,-1), (4,-1)),
        ]

    tbl.setStyle(TableStyle(style_cmds))

    elements.append(tbl)
    elements.append(Spacer(1, 10*mm))
    elements.append(Paragraph("Kind regards,", normal))
    elements.append(Paragraph("Maconet B.V.", normal))

    doc.build(elements)
    return filename

def format_so_number(year: int, month: int, sequence: int) -> str:
    yy = str(year)[-2:]
    mm = f"{month:02d}"
    seq = f"{sequence:04d}"
    return f"{yy}{mm}{seq}"

def reserve_next_serviceorder_number(
    db: Session,
    reserved_by: str,
    year: int | None = None,
    month: int | None = None,
) -> ServiceOrderNumber:

    now = datetime.utcnow()
    year = year or now.year
    month = month or now.month

    # 🔒 SQLite write-lock
    db.connection().exec_driver_sql("BEGIN IMMEDIATE")

    # 1️⃣ eerst: bestaand vrij nummer
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

    # 2️⃣ anders: nieuw sequence bepalen
    last_seq = (
        db.query(ServiceOrderNumber.sequence)
        .filter(ServiceOrderNumber.year == year)
        .order_by(ServiceOrderNumber.sequence.desc())
        .first()
    )

    next_seq = (last_seq[0] + 1) if last_seq else 1
    so_number = format_so_number(year, month, next_seq)

    rec = ServiceOrderNumber(
        so_number=so_number,
        year=year,
        month=month,
        sequence=next_seq,
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



# ============================
# Pydantic Schemas
# ============================

class ServiceOrderIn(BaseModel):
    so: str
    supplier: Optional[str] = None
    customer_ref: Optional[str] = None
    po: Optional[str] = None
    status: Optional[str] = None
    price_type: Optional[str] = None
    employee: Optional[str] = None
    remarks: Optional[str] = None

class ServiceOrderOverview(BaseModel):
    so: str
    supplier: Optional[str]
    customer_ref: Optional[str]
    po: Optional[str]
    status: Optional[str]
    employee: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ServiceOrderItemIn(BaseModel):
    part_no: str
    description: Optional[str] = None
    qty: int

    list_price: Optional[float] = None
    price_bruto: Optional[float] = None
    price_wvk: Optional[float] = None
    price_edmac: Optional[float] = None
    price_purchase: Optional[float] = None

    leadtime: Optional[str] = None
    bestellen: bool = False
    ontvangen: Optional[bool] = False
    
class ServiceOrderItemOut(BaseModel):
    id: int
    part_no: str
    description: Optional[str]
    qty: int

    list_price: Optional[float]
    price_bruto: Optional[float]
    price_wvk: Optional[float]
    price_edmac: Optional[float]
    price_purchase: Optional[float]

    leadtime: Optional[str]
    bestellen: bool

    ontvangen: bool
    received_at: Optional[datetime]

    class Config:
        from_attributes = True

class ServiceOrderLogOut(BaseModel):
    id: int
    action: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class ArticleOut(BaseModel):
    part_no: str
    description: Optional[str] = None
    list_price: Optional[float] = None
    price_bruto: Optional[float] = None
    price_wvk: Optional[float] = None
    price_edmac: Optional[float] = None
    price_purchase: Optional[float] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.user

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    id: int
    email: str
    role: UserRole

    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    email: str

class PasswordResetSubmit(BaseModel):
    token: str
    password: str

class CustomerIn(BaseModel):
    name: str
    contact: str | None = None
    email: str | None = None
    price_type: str | None = None

    # ✅ NAW
    address: str | None = None
    zipcode: str | None = None
    city: str | None = None
    country: str | None = None

class CustomerOut(BaseModel):
    id: int
    name: str
    contact: str | None = None
    email: str | None = None
    price_type: str | None = None

    # ✅ NAW
    address: str | None = None
    zipcode: str | None = None
    city: str | None = None
    country: str | None = None

    class Config:
        from_attributes = True

class ContactOut(BaseModel):
    id: int 
    contact_name: str
    email: str
    is_primary: bool

    class Config:
        from_attributes = True

class ContactCreate(BaseModel):
    contact_name: str
    email: str

class SullairSettingsIn(BaseModel):
    contact_name: Optional[str] = None
    email: Optional[str] = None

class SullairSettingsOut(BaseModel):
    contact_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

class MailPreviewOut(BaseModel):
    to: str
    subject: str
    body_html: str
    
class MailSendIn(BaseModel):
    to: str
    subject: str
    body_html: str

class MailPreviewIn(BaseModel):
    so: str

class CustomerPriceRuleIn(BaseModel):
    min_amount: float
    price_type: str

class CustomerPriceRuleOut(BaseModel):
    id: int
    min_amount: float
    price_type: str

    class Config:
        from_attributes = True

from enum import Enum as PyEnum

class ServiceOrderNrStatusEnum(str, PyEnum):
    FREE = "FREE"
    RESERVED = "RESERVED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class ServiceOrderNumberOut(BaseModel):
    id: int
    so_number: str

    year: int
    month: int
    sequence: int
    date: datetime

    customer_id: int | None = None
    customer_name_free: str | None = None

    supplier: str | None = None
    description: str | None = None
    type: str | None = None
    offer: bool
    offer_amount: float | None = None
    status: ServiceOrderNrStatusEnum

    reserved_by: str | None = None
    reserved_at: datetime | None = None
    confirmed_at: datetime | None = None

    class Config:
        from_attributes = True

class ServiceOrderNumberUpdate(BaseModel):
    customer_id: int | None = None
    customer_name_free: str | None = None

    supplier: str | None = None
    description: str | None = None
    type: str | None = None  # VO / OH

    offer: bool | None = None
    offer_amount: float | None = None

class ServiceOrderNumberReserveOut(BaseModel):
    so_number: str
    status: ServiceOrderNrStatusEnum






# ============================
# HEALTH
# ============================

@app.get("/health")
def health():
    return {"ok": True}


# ============================
# USERS & AUTH
# ============================

@app.post("/users/create")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(400, "User already exists")

    # 🔐 tijdelijk wachtwoord
    temp_password = secrets.token_urlsafe(10)

    user = User(
        email=data.email,
        password_hash=hash_password(temp_password),
        role=data.role,
    )

    # 🔁 force reset
    reset_token = secrets.token_urlsafe(32)
    user.reset_token = reset_token
    user.reset_expires = datetime.utcnow() + timedelta(hours=24)

    db.add(user)
    db.commit()
    db.refresh(user)

    # 📧 voorlopig console output (later mail)
    print("=== NEW USER CREATED ===")
    print("Email:", user.email)
    print("Temporary password:", temp_password)
    print("Reset link:")
    print(f"http://localhost:3000/reset-password/{reset_token}")
    print("========================")

    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
    }

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # ❌ jezelf niet verwijderen
    if current_user.id == user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete yourself"
        )

    # ❌ designer mag alleen door designer worden verwijderd
    if (
        user.role == UserRole.designer
        and current_user.role != UserRole.designer
    ):
        raise HTTPException(
            status_code=403,
            detail="Only designer can delete a designer"
        )

    db.delete(user)
    db.commit()

    return {
        "status": "deleted",
        "user_id": user_id,
        "email": user.email,
    }


@app.post("/auth/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    # Swagger gebruikt 'username' → wij gebruiken email
    u = db.query(User).filter(User.email == form.username).first()
    if not u:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(form.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(u)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@app.get("/auth/whoami")
def who_am_i(user: User = Depends(get_current_user)):
    return {
        "email": user.email,
        "role": user.role,
    }


@app.post("/auth/request-password-reset")
def request_password_reset(data: PasswordResetRequest):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == data.email).first()

        # altijd OK teruggeven (veiligheid)
        if not user:
            return {"result": "ok"}

        token = secrets.token_urlsafe(32)

        user.reset_token = token
        user.reset_expires = datetime.utcnow() + timedelta(minutes=30)

        db.commit()

        print("========== PASSWORD RESET LINK ==========")
        print(f"http://localhost:3000/reset-password/{token}")
        print("=========================================")

        return {"result": "ok"}

    finally:
        db.close()

@app.post("/auth/reset-password")
def reset_password(data: PasswordResetSubmit):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.reset_token == data.token).first()

        if not user:
            raise HTTPException(400, "Invalid token")

        if not user.reset_expires or user.reset_expires < datetime.utcnow():
            raise HTTPException(400, "Token expired")

        user.password_hash = hash_password(data.password)
        user.reset_token = None
        user.reset_expires = None

        db.commit()

        return {"result": "password changed"}

    finally:
        db.close()

@app.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    users = db.query(User).order_by(User.email.asc()).all()
    return users


@app.post("/users/{user_id}/set-role")
def set_user_role(
    user_id: int,
    role: UserRole = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.designer)),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")

    user.role = role
    db.commit()

    return {
        "user_id": user.id,
        "email": user.email,
        "new_role": user.role,
    }

# ============================
# SERVICE ORDERS CRUD
# ============================

@app.post("/serviceorders/upsert")
def upsert_serviceorder(payload: ServiceOrderIn, x_api_key: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    check_api_key(x_api_key)

    existing = db.query(ServiceOrder).filter(ServiceOrder.so == payload.so).first()

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
        "Serviceorder aangemaakt"
    )
    return {"result": "created", "so": payload.so}


@app.get("/serviceorders/overview", response_model=List[ServiceOrderOverview])
def list_serviceorders_overview(x_api_key: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    check_api_key(x_api_key)

    records = db.query(ServiceOrder).order_by(ServiceOrder.created_at.desc()).all()

    return records

@app.get("/serviceorders/{so}", response_model=ServiceOrderIn)
def get_serviceorder(
    so: str,
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()

    if not order:
        raise HTTPException(404, "Serviceorder not found")

    return order



# ============================
# SERVICE ORDER ITEMS
# ============================

@app.post("/serviceorders/{so}/items/replace")
def replace_items(
    so: str,
    items: List[ServiceOrderItemIn],
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    db.query(ServiceOrderItem).filter(ServiceOrderItem.serviceorder_id == order.id).delete()

    for item in items:
        rec = ServiceOrderItem(serviceorder_id=order.id, **item.model_dump())
        db.add(rec)

    db.commit()
    return {"result": "ok", "count": len(items)}


@app.get(
    "/serviceorders/{so}/items",
    response_model=list[ServiceOrderItemOut]
)
def get_items(
    so: str,
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    return (
        db.query(ServiceOrderItem)
        .filter(ServiceOrderItem.serviceorder_id == order.id)
        .all()
    )


@app.post("/serviceorders/{so}/items/{item_id}/receive")
def receive_item(
    so: str,
    item_id: int,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    item = (
        db.query(ServiceOrderItem)
        .filter(
            ServiceOrderItem.id == item_id,
            ServiceOrderItem.serviceorder_id == order.id
        )
        .first()
    )

    if not item:
        raise HTTPException(404, "Item not found")

    if not item.bestellen:
        raise HTTPException(400, "Item was not ordered")

    # markeer ontvangen
    item.ontvangen = True
    item.received_at = datetime.utcnow()
    db.commit()

    # 🔍 check: zijn alle bestelde items ontvangen?
    remaining = (
        db.query(ServiceOrderItem)
        .filter(
            ServiceOrderItem.serviceorder_id == order.id,
            ServiceOrderItem.bestellen == True,
            ServiceOrderItem.ontvangen == False
        )
        .count()
    )

    if remaining == 0:
        set_order_status(
            db,
            order,
            "ONTVANGEN",
            "Alle bestelde artikelen zijn ontvangen"
        )
    else:
        log_event(
            db,
            order,
            "DEELONTVANGST",
            f"Artikel {item.part_no} ontvangen"
        )

    return {"status": "ok"}

# ============================
# ARTICLE LOOKUP
# ============================

@app.get("/articles/{part_no}", response_model=ArticleOut)
def get_article(
    part_no: str = Path(...),
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    rec = db.query(Article).filter(Article.part_no == part_no).first()

    if not rec:
        raise HTTPException(404, "Article not found")

    return rec

# ============================
# CUSTOMERS
# ============================
@app.get("/customers", response_model=list[CustomerOut])
def list_customers(x_api_key: Optional[str] = Header(default=None)):
    check_api_key(x_api_key)

    db = SessionLocal()
    try:
        rows = db.query(Customer).order_by(Customer.name.asc()).all()
        return rows
    finally:
        db.close()


@app.post("/customers", response_model=CustomerOut)
def create_customer(
    data: CustomerIn, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
    ):
    

    
    try:
        rec = Customer(
            name=data.name,
            contact=data.contact,
            email=data.email,
            price_type=data.price_type,
            address=data.address,
            zipcode=data.zipcode,
            city=data.city,
            country=data.country,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec
    finally:
        db.close()


@app.put("/customers/{customer_id}")
def update_customer(
    customer_id: int, 
    payload: CustomerIn, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
    ):
    
    try:
        cust = db.query(Customer).filter(Customer.id == customer_id).first()
        if not cust:
            raise HTTPException(404, "Customer not found")

        cust.name = payload.name
        cust.contact = payload.contact
        cust.email = payload.email
        cust.price_type = payload.price_type
        cust.address = payload.address
        cust.zipcode = payload.zipcode
        cust.city = payload.city
        cust.country = payload.country

        db.commit()

        return {"result": "updated"}
    finally:
        db.close()

@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin)),
):
    
    try:
        cust = db.query(Customer).filter(Customer.id == customer_id).first()

        if not cust:
            raise HTTPException(404, "Customer not found")

        # verwijder ook gekoppelde contacten
        db.query(CustomerContact).filter(
            CustomerContact.customer_id == customer_id
        ).delete()

        db.delete(cust)
        db.commit()

        return {"result": "deleted"}
    finally:
        db.close()

# =============================
# CONTACTS
# =============================

@app.get("/customers/{customer_id}/contacts", response_model=List[ContactOut])
def get_contacts_for_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    rows = (
        db.query(CustomerContact)
        .filter(CustomerContact.customer_id == customer_id)
        .order_by(CustomerContact.contact_name.asc())
        .all()
    )
    return rows


@app.post("/customers/{customer_id}/contacts", response_model=ContactOut)
def add_contact_for_customer(
    customer_id: int,
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin))
):
    contact = CustomerContact(
        customer_id=customer_id,
        contact_name=data.contact_name,
        email=data.email,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@app.put("/contacts/{contact_id}")
def update_contact(
    contact_id: int, 
    data: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin))
    ):
    
    try:
        c = db.query(CustomerContact).filter(CustomerContact.id == contact_id).first()

        if not c:
            raise HTTPException(404, "Contact not found")

        c.contact_name = data.contact_name
        c.email = data.email

        db.commit()
        return {"result": "updated"}
    finally:
        db.close()


@app.delete("/contacts/{contact_id}")
def delete_contact(
    contact_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin))
    ):
    c = db.query(CustomerContact).filter(CustomerContact.id == contact_id).first()

    if not c:
        raise HTTPException(404, "Contact not found")

    db.delete(c)
    db.commit()
    return {"result": "deleted"}


@app.post("/contacts/{contact_id}/set_primary")
def set_primary_contact(
    contact_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin))
    ):

    contact = db.query(CustomerContact).filter(CustomerContact.id == contact_id).first()
    if not contact:
        raise HTTPException(404, "Contact not found")

    # alle andere van deze klant op False
    db.query(CustomerContact).filter(
        CustomerContact.customer_id == contact.customer_id
    ).update({CustomerContact.is_primary: False})

    contact.is_primary = True
    db.commit()

    return {"status": "ok"}

# =========================
# SETTINGS
# =========================

@app.get("/sullair/settings", response_model=SullairSettingsOut)
def get_sullair_settings(db: Session = Depends(get_db)):
    rec = db.query(SullairSettings).first()
    if not rec:
        # nog nooit ingesteld → leeg object terug
        return SullairSettingsOut(contact_name="", email="")
    return rec


@app.post("/sullair/settings", response_model=SullairSettingsOut)
def save_sullair_settings(
    data: SullairSettingsIn, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin))
    ):
    rec = db.query(SullairSettings).first()

    if not rec:
        rec = SullairSettings()

    rec.contact_name = data.contact_name
    rec.email = data.email

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return rec

# ============================
# MAIL PREVIEW – SULLAIR
# ============================

@app.post("/mail/sullair/preview", response_model=MailPreviewOut)
def preview_sullair_mail(
    data: MailPreviewIn,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == data.so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    items = (
        db.query(ServiceOrderItem)
        .filter(ServiceOrderItem.serviceorder_id == order.id)
        .all()
    )

    if not items:
        raise HTTPException(400, "No items in serviceorder")

    sullair_name = "John Doe"
    sullair_email = "orders@sullair.com"

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
    <div style="font-family: Arial, sans-serif; font-size: 14px; color: #000;">

        <p style="margin: 0 0 16px 0;">
            Dear {sullair_name},
        </p>

        <p style="margin: 0 0 20px 0;">
            We kindly request, with serviceorder number
            <b>{order.so}</b>, the leadtimes for the following items:
        </p>

        <table
            style="border-collapse: collapse; margin-bottom: 20px; width: 100%;"
        >
            <tr>
                <th style="border:1px solid #000; padding:6px; text-align:left;">Item</th>
                <th style="border:1px solid #000; padding:6px;">Part No.</th>
                <th style="border:1px solid #000; padding:6px;">Description</th>
                <th style="border:1px solid #000; padding:6px; text-align:right;">QTY</th>
                <th style="border:1px solid #000; padding:6px; text-align:right;">Price Each</th>
                <th style="border:1px solid #000; padding:6px;">Leadtime NL</th>
                <th style="border:1px solid #000; padding:6px;">Comments</th>
            </tr>
            {rows}
        </table>

        <p style="margin: 24px 0 4px 0;">
            Kind regards,
        </p>

        <p style="margin: 0;">
            <b>Maconet B.V.</b>
        </p>

    </div>
    """


    subject = f"Leadtime request service order {order.so}"

    set_order_status(
        db,
        order,
        "AANGEVRAAGD",
        f"Aanvraag verstuurd naar Sullair ({sullair_email})"
    )

    return {
        "to": sullair_email,
        "subject": subject,
        "body_html": body
    }

@app.post("/mail/offer/preview", response_model=MailPreviewOut)
def preview_offer_mail(
    data: MailPreviewIn,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    # =========================
    # Serviceorder
    # =========================
    order = db.query(ServiceOrder).filter(ServiceOrder.so == data.so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    pricing = calculate_order_totals(db, order)

    items = (
        db.query(ServiceOrderItem)
        .filter(ServiceOrderItem.serviceorder_id == order.id)
        .all()
    )

    has_leadtimes = any(it.leadtime and it.leadtime.strip() for it in items)

    # =========================
    # Klant + contact
    # =========================
    customer = db.query(Customer).filter(Customer.name == order.supplier).first()
    if not customer:
        raise HTTPException(400, "Customer not found")

    contact = (
        db.query(CustomerContact)
        .filter(
            CustomerContact.customer_id == customer.id,
            CustomerContact.is_primary == True
        )
        .first()
    )

    if not contact:
        raise HTTPException(400, "No primary contact for customer")

    # =========================
    # Tabel header
    # =========================
    header_html = (
        "<th style='border:1px solid #000;padding:6px;'>Qty</th>"
        "<th style='border:1px solid #000;padding:6px;'>Price</th>"
        + (
            "<th style='border:1px solid #000;padding:6px;'>Leadtime</th>"
            if has_leadtimes else ""
        )
        + "<th style='border:1px solid #000;padding:6px;'>Line total</th>"
    )

    # =========================
    # Rijen
    # =========================
    rows = ""

    for idx, it in enumerate(pricing["items"], start=1):
        db_item = next(x for x in items if x.part_no == it["part_no"])
        leadtime = db_item.leadtime or ""

        row = f"""
        <tr>
            <td>{idx}</td>
            <td>{it['part_no']}</td>
            <td>{it['description']}</td>
            <td style="text-align:right;">{it['qty']}</td>
            <td style="text-align:right;">{format_currency(it['price_each'])}</td>
        """

        if has_leadtimes:
            row += f"<td>{leadtime}</td>"

        row += f"""
            <td style="text-align:right;">{format_currency(it['line_total'])}</td>
        </tr>
        """

        rows += row

    # =========================
    # Leadtimes melding
    # =========================
    leadtime_notice = ""
    if not has_leadtimes:
        leadtime_notice = "<p><i>Leadtimes are requested from our supplier.</i></p>"

    # =========================
    # Mail body
    # =========================
    body = f"""
    <div style="font-family: Arial; font-size:14px;">
        <p>Dear {contact.contact_name},</p>

        <p>
            Please find below our quotation for service order
            <b>{order.so}</b>.
        </p>

        {leadtime_notice}

        <table style="border-collapse:collapse;width:100%;">
            <tr>
                <th style="border:1px solid #000;padding:6px;">Item</th>
                <th style="border:1px solid #000;padding:6px;">Part No</th>
                <th style="border:1px solid #000;padding:6px;">Description</th>
                {header_html}
            </tr>
            {rows}
        </table>

        <p style="margin-top:16px;">
            <b>Total ({pricing['price_type']}): {format_currency(pricing['total'])}</b>
        </p>

        <p>Kind regards,<br>Maconet B.V.</p>
    </div>
    """

    # =========================
    # Status + log
    # =========================
    set_order_status(
        db,
        order,
        "OFFERTE",
        f"Offerte verstuurd naar {contact.email}"
    )

    return {
        "to": contact.email,
        "subject": f"Quotation for service order {order.so}",
        "body_html": body,
    }

@app.post("/mail/stock-order/preview")
def preview_stock_order(
        data: MailPreviewIn,
        x_api_key: str = Header(...),
        db: Session = Depends(get_db),
    ):
        check_api_key(x_api_key)

        order = db.query(ServiceOrder).filter(ServiceOrder.so == data.so).first()
        if not order:
            raise HTTPException(404, "Serviceorder not found")

        sullair = db.query(SullairSettings).first()
        if not sullair:
            raise HTTPException(400, "Sullair settings not configured")

        # Alleen artikelen die besteld worden
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
        pdf_path = build_stock_order_pdf(db, order, sullair.email)

        subject = f"Stock Order {order.so}"
        body = f"""
        <p>Dear {sullair.contact_name},</p>

        <p>
            Please find attached our Stock Order for service order
            <b>{order.so}</b>.
        </p>

        <p>Kind regards,<br/>Maconet B.V.</p>
        """

        return {
            "to": sullair.email,
            "subject": subject,
            "body_html": body,
            "pdf": os.path.basename(pdf_path),
            "pdf_path": pdf_path
        }

@app.post("/mail/order-confirmation/preview", response_model=MailPreviewOut)
def preview_order_confirmation(
    data: MailPreviewIn,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == data.so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    # Bestelde items uit DB
    ordered_items = (
        db.query(ServiceOrderItem)
        .filter(
            ServiceOrderItem.serviceorder_id == order.id,
            ServiceOrderItem.bestellen == True
        )
        .all()
    )
    if not ordered_items:
        raise HTTPException(400, "No items marked for ordering")

    # pricing engine (gebruiken we alleen om price/line_total te bepalen)
    pricing_all = calculate_order_totals(db, order)

    # snelle lookup op part_no -> pricing row
    pricing_map = {p["part_no"]: p for p in pricing_all["items"]}

    # leadtime check op ordered items
    has_leadtimes = any((it.leadtime or "").strip() for it in ordered_items)

    # klant + primair contact
    customer = db.query(Customer).filter(Customer.name == order.supplier).first()
    if not customer:
        raise HTTPException(400, "Customer not found")

    contact = (
        db.query(CustomerContact)
        .filter(CustomerContact.customer_id == customer.id, CustomerContact.is_primary == True)
        .first()
    )
    if not contact:
        raise HTTPException(400, "No primary contact for customer")

    # HTML helper voor borders/alignment
    th = 'style="border:1px solid #000;padding:6px;text-align:left;background:#f2f2f2;"'
    td = 'style="border:1px solid #000;padding:6px;"'
    td_r = 'style="border:1px solid #000;padding:6px;text-align:right;white-space:nowrap;"'
    td_c = 'style="border:1px solid #000;padding:6px;text-align:center;white-space:nowrap;"'
    td_l = 'style="border:1px solid #000;padding:6px;text-align:left;"'

    # rows bouwen + total berekenen
    rows = ""
    total = 0.0

    for idx, db_it in enumerate(ordered_items, start=1):
        p = pricing_map.get(db_it.part_no)

        # Als pricing_map het part_no niet kent (kan bij rommeldata), skippen we netjes
        if not p:
            continue

        qty = p["qty"]
        price_each = p["price_each"]
        line_total = p["line_total"]
        total += (line_total or 0.0)

        lead = (db_it.leadtime or "").strip()

        if has_leadtimes:
            rows += f"""
            <tr>
              <td {td_c}>{idx}</td>
              <td {td_l}>{p['part_no']}</td>
              <td {td_l}>{p['description'] or ""}</td>
              <td {td_r}>{qty}</td>
              <td {td_l}>{lead}</td>
              <td {td_r}>{format_currency(price_each)}</td>
              <td {td_r}>{format_currency(line_total)}</td>
            </tr>
            """
        else:
            rows += f"""
            <tr>
              <td {td_c}>{idx}</td>
              <td {td_l}>{p['part_no']}</td>
              <td {td_l}>{p['description'] or ""}</td>
              <td {td_r}>{qty}</td>
              <td {td_r}>{format_currency(price_each)}</td>
              <td {td_r}>{format_currency(line_total)}</td>
            </tr>
            """

    # Als alles geskipt werd (edge case) -> foutmelding
    if rows.strip() == "":
        raise HTTPException(400, "No priced ordered items found (pricing mismatch)")

    # Header dynamisch
    if has_leadtimes:
        header_cols = f"""
          <th {th}>Item</th>
          <th {th}>Part No</th>
          <th {th}>Description</th>
          <th {th} style="text-align:right;">Qty</th>
          <th {th}>Leadtime</th>
          <th {th} style="text-align:right;">Price</th>
          <th {th} style="text-align:right;">Line total</th>
        """
        leadtime_note = ""
    else:
        header_cols = f"""
          <th {th}>Item</th>
          <th {th}>Part No</th>
          <th {th}>Description</th>
          <th {th} style="text-align:right;">Qty</th>
          <th {th} style="text-align:right;">Price</th>
          <th {th} style="text-align:right;">Line total</th>
        """
        leadtime_note = """
          <p style="margin:10px 0 0 0;">
            <i>Leadtimes are requested from our supplier.</i>
          </p>
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
          {header_cols}
        </tr>
        {rows}
        <tr>
          <td {td} colspan="{6 if has_leadtimes else 5}" style="text-align:right;font-weight:bold;">
            Total
          </td>
          <td {td_r} style="font-weight:bold;">
            {format_currency(total)}
          </td>
        </tr>
      </table>

      {leadtime_note}

      <p style="margin-top:16px;">Kind regards,<br/>Maconet B.V.</p>
    </div>
    """

    # status + log (preview: als je dit liever pas bij "send" doet, zet dit blok daar)
    set_order_status(
        db,
        order,
        "BESTELD",
        f"Order confirmation preview created for {contact.email}"
    )

    return {
        "to": contact.email,
        "subject": f"Order confirmation service order {order.so}",
        "body_html": body,
    }

@app.post("/mail/send")
def send_mail(
    data: MailSendIn,
    x_api_key: str = Header(...),
):
    check_api_key(x_api_key)

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    msg = MIMEMultipart("alternative")
    msg["From"] = "Maconet B.V. <no-reply@maconet.nl>"
    msg["To"] = data.to
    msg["Subject"] = data.subject

    msg.attach(MIMEText(data.body_html, "html"))

    # ⚠️ SMTP later netjes in config
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)

    return {"status": "sent"}

@app.post("/mail/stock-order/send")
def send_stock_order(
    data: MailPreviewIn,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == data.so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    sullair = db.query(SullairSettings).first()
    if not sullair:
        raise HTTPException(400, "Sullair settings not configured")

    # Alleen regels met bestellen = true
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

    # PDF maken
    pdf_path = build_stock_order_pdf(db, order, sullair.email)

    # Mail opbouwen
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.application import MIMEApplication
    from email.mime.text import MIMEText

    msg = MIMEMultipart()
    msg["From"] = "Maconet B.V. <no-reply@maconet.nl>"
    msg["To"] = sullair.email
    msg["Subject"] = f"Stock Order {order.so}"

    msg.attach(MIMEText("Please find attached our Stock Order.", "plain"))

    with open(pdf_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=f"StockOrder_{order.so}.pdf")
        part["Content-Disposition"] = f'attachment; filename="StockOrder_{order.so}.pdf"'
        msg.attach(part)

    # ✉️ verzenden
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)

    # 🔥 STATUS + LOG = TRANSACTION
    order.status = "BESTELD"

    db.add(ServiceOrderLog(
        serviceorder_id=order.id,
        action="BESTELD",
        message=f"Stock order sent to Hitachi ({sullair.email})"
    ))

    db.commit()

    return {
        "status": "sent",
        "pdf": f"StockOrder_{order.so}.pdf"
    }

@app.post("/mail/stock-order/simulate")
def simulate_stock_order(
    data: MailPreviewIn,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == data.so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    sullair = db.query(SullairSettings).first()
    if not sullair:
        raise HTTPException(400, "Sullair settings not configured")

    # Alleen regels die besteld worden
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

    # PDF wél bouwen (belangrijk!)
    pdf_path = build_stock_order_pdf(db, order, sullair.email)

    # Status + log exact alsof mail is verzonden
    order.status = "BESTELD"

    db.add(ServiceOrderLog(
        serviceorder_id=order.id,
        action="BESTELD",
        message=f"[SIMULATED] Stock order sent to Hitachi ({sullair.email})"
    ))

    db.commit()

    return {
        "status": "simulated",
        "pdf": os.path.basename(pdf_path),
        "pdf_path": pdf_path
    }

# ==================================================
# Pakbon generator
# ==================================================

@app.get("/serviceorders/{so}/packing-slip/customer")
def packing_slip_customer(
    so: str,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    pdf_path = build_packing_slip_pdf(db, order, mode="customer")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"PackingSlip_{order.so}.pdf"
    )

@app.get("/serviceorders/{so}/packing-slip/internal")
def packing_slip_internal(
    so: str,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    pdf_path = build_packing_slip_pdf(db, order, mode="internal")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"PackingSlip_INTERNAL_{order.so}.pdf"
    )

# ==================================================
# Pricingengine
# ==================================================

@app.get(
    "/customers/{customer_id}/price-rules",
    response_model=list[CustomerPriceRuleOut]
)
def get_price_rules(
    customer_id: int,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    return (
        db.query(CustomerPriceRule)
        .filter(CustomerPriceRule.customer_id == customer_id)
        .order_by(CustomerPriceRule.min_amount.asc())
        .all()
    )

@app.post("/customers/{customer_id}/price-rules")
def save_price_rules(
    customer_id: int,
    data: list[CustomerPriceRuleIn],
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_min_role(UserRole.admin))
):
    check_api_key(x_api_key)

    db.query(CustomerPriceRule).filter(
        CustomerPriceRule.customer_id == customer_id
    ).delete()

    for rule in data:
        db.add(CustomerPriceRule(
            customer_id=customer_id,
            min_amount=rule.min_amount,
            price_type=rule.price_type
        ))

    db.commit()
    return {"status": "ok", "count": len(data)}

@app.get("/serviceorders/{so}/pricing")
def get_serviceorder_pricing(
    so: str,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    try:
        pricing = calculate_order_totals(db, order)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return pricing

# =========================================
# logging actie
# =========================================

@app.get(
    "/serviceorders/{so}/log",
    response_model=list[ServiceOrderLogOut]
)
def get_serviceorder_log(
    so: str,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    return (
        db.query(ServiceOrderLog)
        .filter(ServiceOrderLog.serviceorder_id == order.id)
        .order_by(ServiceOrderLog.created_at.desc())
        .all()
    )

@app.get("/serviceorders/{so}/order/pdf")
def get_stock_order_pdf(
    so: str,
    x_api_key: str = Header(...),
    db: Session = Depends(get_db),
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    sullair = db.query(SullairSettings).first()
    if not sullair:
        raise HTTPException(400, "Sullair settings not configured")

    pdf_path = build_stock_order_pdf(db, order, sullair.email)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"StockOrder_{order.so}.pdf"
    )

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def get_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALG])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
@app.get("/serviceorders/{so}/order/pdf-preview")
def get_stock_order_pdf_preview(
    so: str,
    user=Depends(get_user_from_jwt_token),
    db: Session = Depends(get_db)
):
    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

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

    pdf_path = build_stock_order_pdf(db, order, "preview")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"StockOrder_{order.so}.pdf"
    )

@app.post("/serviceorder-numbers/reserve")
def reserve_so_number(
    user=Depends(get_user_from_jwt_token),
    db: Session = Depends(get_db)
):
    rec = reserve_next_serviceorder_number(
        db=db,
        reserved_by=user["sub"]
    )
    return {
        "so_number": rec.so_number,
        "status": rec.status,
    }

@app.post("/serviceorder-numbers/reserve-batch/{count}")
def reserve_batch(
    count: int,
    user=Depends(get_user_from_jwt_token),
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

@app.post("/serviceorder-numbers/{so_number}/confirm")
def confirm_so_number(
    so_number: str,
    db: Session = Depends(get_db)
):
    confirm_serviceorder_number(db, so_number)
    return {"status": "confirmed"}

@app.post("/serviceorder-numbers/{so_number}/cancel")
def cancel_so_number(
    so_number: str,
    db: Session = Depends(get_db)
):
    cancel_serviceorder_number(db, so_number)
    return {"status": "cancelled"}




from datetime import datetime, timezone, timedelta
from typing import Optional, List

from fastapi import FastAPI, Header, HTTPException, Path, Depends
from pydantic import BaseModel
from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey,
    Float, Boolean
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

from passlib.context import CryptContext
from jose import jwt, JWTError

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
# SECURITY HELPERS
# ============================

pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto"
)



def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(email: str, is_admin: bool) -> str:
    payload = {
        "sub": email,
        "admin": is_admin,
        "exp": datetime.utcnow() + timedelta(hours=8),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def check_api_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


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

    price_bruto = Column(Float)
    price_wvk = Column(Float)
    price_edmac = Column(Float)

    leadtime = Column(String)
    bestellen = Column(Boolean, default=False)

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



Base.metadata.create_all(bind=engine)


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
    price_bruto: Optional[float] = None
    price_wvk: Optional[float] = None
    price_edmac: Optional[float] = None
    leadtime: Optional[str] = None
    bestellen: bool = False


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
    email: str
    password: str
    is_admin: bool = False


class UserLogin(BaseModel):
    email: str
    password: str

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

class CustomerOut(BaseModel):
    id: int
    name: str
    contact: str | None = None
    email: str | None = None
    price_type: str | None = None

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
# HEALTH
# ============================

@app.get("/health")
def health():
    return {"ok": True}


# ============================
# USERS & AUTH
# ============================

@app.post("/users/create")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(400, "User already exists")

    u = User(
        email=user.email,
        password_hash=hash_password(user.password),
        is_admin=user.is_admin
    )

    db.add(u)
    db.commit()

    return {"result": "created", "email": user.email}


@app.post("/auth/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == user.email).first()
    if not u:
        raise HTTPException(401, "Invalid credentials")

    if not verify_password(user.password, u.password_hash):
        raise HTTPException(401, "Invalid credentials")

    token = create_access_token(u.email, u.is_admin)

    return {"access_token": token, "token_type": "bearer"}

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
    return {"result": "created", "so": payload.so}


@app.get("/serviceorders/overview", response_model=List[ServiceOrderOverview])
def list_serviceorders_overview(x_api_key: Optional[str] = Header(default=None), db: Session = Depends(get_db)):
    check_api_key(x_api_key)

    records = db.query(ServiceOrder).order_by(ServiceOrder.created_at.desc()).all()

    return records


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


@app.get("/serviceorders/{so}/items")
def get_items(
    so: str,
    x_api_key: Optional[str] = Header(default=None),
    db: Session = Depends(get_db)
):
    check_api_key(x_api_key)

    order = db.query(ServiceOrder).filter(ServiceOrder.so == so).first()
    if not order:
        raise HTTPException(404, "Serviceorder not found")

    rows = db.query(ServiceOrderItem).filter(ServiceOrderItem.serviceorder_id == order.id).all()
    return rows


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
def create_customer(data: CustomerIn, x_api_key: Optional[str] = Header(default=None)):
    check_api_key(x_api_key)

    db = SessionLocal()
    try:
        rec = Customer(
            name=data.name,
            contact=data.contact,
            email=data.email
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        return rec
    finally:
        db.close()


@app.put("/customers/{customer_id}")
def update_customer(customer_id: int, payload: CustomerIn, x_api_key: str = Header(None)):
    check_api_key(x_api_key)

    db = SessionLocal()
    try:
        cust = db.query(Customer).filter(Customer.id == customer_id).first()
        if not cust:
            raise HTTPException(404, "Customer not found")

        cust.name = payload.name
        cust.contact = payload.contact
        cust.email = payload.email
        cust.price_type = payload.price_type

        db.commit()

        return {"result": "updated"}
    finally:
        db.close()

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, x_api_key: str = Header(None)):
    check_api_key(x_api_key)

    db = SessionLocal()
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
    db: Session = Depends(get_db)
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
def update_contact(contact_id: int, data: ContactCreate):
    db = SessionLocal()
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
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    c = db.query(CustomerContact).filter(CustomerContact.id == contact_id).first()

    if not c:
        raise HTTPException(404, "Contact not found")

    db.delete(c)
    db.commit()
    return {"result": "deleted"}


@app.post("/contacts/{contact_id}/set_primary")
def set_primary_contact(contact_id: int, db: Session = Depends(get_db)):

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
def save_sullair_settings(data: SullairSettingsIn, db: Session = Depends(get_db)):
    rec = db.query(SullairSettings).first()

    if not rec:
        rec = SullairSettings()

    rec.contact_name = data.contact_name
    rec.email = data.email

    db.add(rec)
    db.commit()
    db.refresh(rec)

    return rec







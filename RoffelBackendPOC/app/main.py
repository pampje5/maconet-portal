# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware



app = FastAPI(title="Roffel Backend API")

from app.database import SessionLocal
from app.core.bootstrap import create_initial_admin

from app.routers import (
    health,
    auth,
    users,
    serviceorders,
    customers,
    mail,
    pricing,
    serviceorder_numbers,
    serviceorder_log,
    customer_contacts,
    customer_pricing,
    sullair_settings,
    articles,
    suppliers,
    purchaseorder_numbers,
)

app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["maconet.roffeloac.nl"]


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(serviceorders.router)
app.include_router(serviceorder_log.router)
app.include_router(customers.router)
app.include_router(mail.router)
app.include_router(pricing.router)
app.include_router(serviceorder_numbers.router)
app.include_router(customer_contacts.router)
app.include_router(customer_pricing.router)
app.include_router(sullair_settings.router)
app.include_router(articles.router)
app.include_router(suppliers.router)
app.include_router(purchaseorder_numbers.router)

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        create_initial_admin(db)
    finally:
        db.close()

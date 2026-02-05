from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from datetime import datetime

from app.database import Base
import sqlalchemy as sa

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    contact = Column(String, nullable=True)
    email = Column(String, nullable=True)
    price_type = Column(String, nullable=True)

    address = Column(String, nullable=True)
    zipcode = Column(String, nullable=True)
    city = Column(String, nullable=True)
    country = Column(String, nullable=True)

    is_active = Column(Boolean, nullable=False, server_default=sa.true())

    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerContact(Base):
    __tablename__ = "customer_contacts"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    contact_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class CustomerPriceRule(Base):
    __tablename__ = "customer_price_rules"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)

    min_amount = Column(Float, nullable=False)
    price_type = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)


class SullairSettings(Base):
    __tablename__ = "sullair_settings"

    id = Column(Integer, primary_key=True)
    contact_name = Column(String, nullable=True)
    email = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

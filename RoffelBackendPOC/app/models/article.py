from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime

from app.database import Base

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
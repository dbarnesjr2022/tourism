from sqlalchemy import Column, Integer, String, Float, DateTime, func
from backend.app.db import Base


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    businesses = Column(String, nullable=True)  # comma-separated business ids for MVP
    predicted_uplift = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

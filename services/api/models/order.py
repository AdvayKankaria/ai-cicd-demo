from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from services.api.database import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="PENDING")
    total_amount = Column(Float, default=0.0)
    idempotency_key = Column(String, nullable=True, index=True)

    user = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order")

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
    Boolean,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import uuid


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # Order details
    total_amount = Column(Float, nullable=False)
    tax_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, nullable=False)

    # Status and tracking
    status = Column(
        String(50), default="pending"
    )  # pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    payment_status = Column(
        String(50), default="pending"
    )  # pending, paid, failed, refunded

    # Delivery information
    delivery_address = Column(Text, nullable=False)
    delivery_phone = Column(String(20), nullable=False)
    delivery_notes = Column(Text, nullable=True)
    estimated_delivery_time = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    confirmed_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)

    # Relationships
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_number:
            self.order_number = f"ORD-{str(uuid.uuid4())[:8].upper()}"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False, index=True)
    product_name = Column(String(255), nullable=False)
    product_description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    special_instructions = Column(Text, nullable=True)
    subtotal = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="items")

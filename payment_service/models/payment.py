"""
Payment Models - Database models for payment service
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Decimal,
    DateTime,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Payment(Base):
    """
    Payment model for storing payment information.
    """

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), index=True, nullable=True)
    user_id = Column(Integer, index=True, nullable=True)

    # Amount fields
    original_amount = Column(Decimal(10, 2), nullable=False)
    discount_amount = Column(Decimal(10, 2), default=0)
    final_amount = Column(Decimal(10, 2), nullable=False)
    refunded_amount = Column(Decimal(10, 2), default=0)
    currency = Column(String(3), nullable=False, default="USD")

    # Payment method and gateway info
    payment_method = Column(String(50), nullable=False)  # stripe, momo, vnpay
    gateway_payment_id = Column(String(255), unique=True, index=True)
    client_secret = Column(String(255), nullable=True)

    # Status fields
    status = Column(
        String(50), nullable=False, default="pending"
    )  # pending, processing, completed, failed, cancelled, refunded
    gateway_status = Column(String(50), nullable=True)  # Gateway-specific status

    # Promotion info
    promotion_code = Column(String(50), nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    confirmed_at = Column(DateTime, nullable=True)

    # Relationships
    transactions = relationship("PaymentTransaction", back_populates="payment")

    def __repr__(self):
        return f"<Payment(id={self.id}, order_id={self.order_id}, amount={self.final_amount}, status={self.status})>"


class PaymentTransaction(Base):
    """
    Payment transaction model for tracking all payment-related transactions.
    """

    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)

    # Transaction details
    transaction_type = Column(
        String(50), nullable=False
    )  # create_intent, confirm_payment, refund, webhook
    amount = Column(
        Decimal(10, 2), nullable=True
    )  # For refunds and partial transactions
    status = Column(String(50), nullable=False)  # success, failed, pending

    # Gateway response
    gateway_response = Column(JSON, nullable=True)
    gateway_transaction_id = Column(String(255), nullable=True)

    # Error info
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    payment = relationship("Payment", back_populates="transactions")

    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, payment_id={self.payment_id}, type={self.transaction_type}, status={self.status})>"


class PaymentMethod(Base):
    """
    Payment method model for storing user's saved payment methods.
    """

    __tablename__ = "payment_methods"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    # Payment method details
    gateway = Column(String(50), nullable=False)  # stripe, momo, vnpay
    gateway_payment_method_id = Column(String(255), nullable=False)

    # Card/method info (encrypted/tokenized)
    method_type = Column(String(50), nullable=False)  # card, bank_account, wallet
    last_four = Column(String(4), nullable=True)  # Last 4 digits for cards
    brand = Column(String(50), nullable=True)  # visa, mastercard, etc.
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)

    # Status
    is_default = Column(String(1), default="N")  # Y/N
    is_active = Column(String(1), default="Y")  # Y/N

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<PaymentMethod(id={self.id}, user_id={self.user_id}, gateway={self.gateway}, type={self.method_type})>"


class Refund(Base):
    """
    Refund model for tracking refund information.
    """

    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)

    # Refund details
    gateway_refund_id = Column(String(255), unique=True, index=True)
    amount = Column(Decimal(10, 2), nullable=False)
    reason = Column(String(255), nullable=True)
    status = Column(
        String(50), nullable=False, default="pending"
    )  # pending, succeeded, failed

    # Processing info
    processed_by = Column(Integer, nullable=True)  # User ID who processed the refund
    gateway_response = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Refund(id={self.id}, payment_id={self.payment_id}, amount={self.amount}, status={self.status})>"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base
from models.cart import Cart, CartItem
from models.order import Order, OrderItem
from services.cart.cart_service import CartService
from services.orders.order_service import OrderService
from schemas.cart_schemas import CartItemCreate
from schemas.order_schema import OrderCreate

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order_basic.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def test_order_model():
    """Test basic order model functionality"""
    db = TestingSessionLocal()
    try:
        # Create an order
        order = Order(
            user_id=1,
            total_amount=25.0,
            tax_amount=2.5,
            delivery_fee=3.0,
            discount_amount=1.0,
            final_amount=29.5,
            delivery_address="123 Test St",
            delivery_phone="555-0123",
        )
        db.add(order)
        db.commit()
        db.refresh(order)

        assert order.id is not None
        assert order.user_id == 1
        assert order.total_amount == 25.0
        assert order.final_amount == 29.5
        assert order.status == "pending"
        assert order.payment_status == "pending"
        assert order.order_number is not None

        # Add order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=1,
            product_name="Test Product",
            price=12.5,
            quantity=2,
            subtotal=25.0,
        )
        db.add(order_item)
        db.commit()
        db.refresh(order_item)

        assert order_item.id is not None
        assert order_item.subtotal == 25.0

    finally:
        db.close()


def test_order_service():
    """Test order service functionality"""
    db = TestingSessionLocal()
    try:
        # Create a cart with items first
        cart = CartService.get_or_create_cart(db, user_id=999)

        item_data = CartItemCreate(
            product_id=1, product_name="Test Product", price=15.0, quantity=2
        )

        CartService.add_item_to_cart(db, cart.id, item_data)

        # Create order from cart
        order_data = OrderCreate(
            delivery_address="123 Test Street, City, State 12345",
            delivery_phone="555-012-3456",
            delivery_notes="Test notes",
            discount_amount=1.0,
        )

        order = OrderService.create_order_from_cart(db, cart.id, order_data)

        assert order.user_id == 999
        assert order.total_amount == 30.0  # 15.0 * 2
        assert order.delivery_address == "123 Test Street, City, State 12345"
        assert order.status == "pending"
        assert order.order_number is not None

        # Test getting order by ID
        retrieved_order = OrderService.get_order_by_id(db, order.id)
        assert retrieved_order.id == order.id
        assert retrieved_order.order_number == order.order_number

        # Test getting order by number
        order_by_number = OrderService.get_order_by_number(db, order.order_number)
        assert order_by_number.id == order.id

        # Test getting user orders
        user_orders = OrderService.get_user_orders(db, user_id=1)
        assert len(user_orders) == 1
        assert user_orders[0].id == order.id

    finally:
        db.close()

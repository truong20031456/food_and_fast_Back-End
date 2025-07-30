import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from core.database import Base
from models.cart import Cart, CartItem
from services.cart.cart_service import CartService
from schemas.cart_schemas import CartCreate, CartItemCreate

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_basic.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_database():
    """Clean database before each test"""
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate tables
    Base.metadata.create_all(bind=engine)
    yield


def test_cart_model():
    """Test basic cart model functionality"""
    db = TestingSessionLocal()
    try:
        # Create a cart
        cart = Cart(user_id=1, session_id="test_session")
        db.add(cart)
        db.commit()
        db.refresh(cart)

        assert cart.id is not None
        assert cart.user_id == 1
        assert cart.session_id == "test_session"
        assert cart.status == "active"
        assert cart.total_amount == 0.0
        assert cart.total_items == 0

        # Add an item
        item = CartItem(
            cart_id=cart.id,
            product_id=1,
            product_name="Test Product",
            price=10.0,
            quantity=2,
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        assert item.id is not None
        assert item.subtotal == 20.0

        # Refresh cart to get updated totals
        db.refresh(cart)
        assert cart.total_amount == 20.0
        assert cart.total_items == 2

    finally:
        db.close()


def test_cart_service():
    """Test cart service functionality"""
    db = TestingSessionLocal()
    try:
        # Test get_or_create_cart
        cart = CartService.get_or_create_cart(db, user_id=2)
        assert cart.user_id == 2
        assert cart.status == "active"

        # Test adding item
        item_data = CartItemCreate(
            product_id=1, product_name="Test Product", price=15.0, quantity=3
        )

        cart_item = CartService.add_item_to_cart(db, cart.id, item_data)
        assert cart_item.product_id == 1
        assert cart_item.subtotal == 45.0

        # Test getting cart items
        items = CartService.get_cart_items(db, cart.id)
        assert len(items) == 1
        assert items[0].product_name == "Test Product"

    finally:
        db.close()

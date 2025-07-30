import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from core.database import get_db, Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cart.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def clean_database():
    """Clean database before each test"""
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    # Recreate tables
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
async def client():
    """Create test client"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestCart:
    @pytest.mark.asyncio
    async def test_create_cart(self, client):
        """Test creating a new cart"""
        response = await client.post(
            "/api/v1/cart/", json={"user_id": 1, "session_id": "test_session"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == 1
        assert data["session_id"] == "test_session"
        assert data["status"] == "active"
        assert data["total_amount"] == 0.0
        assert data["total_items"] == 0

    @pytest.mark.asyncio
    async def test_get_user_cart(self, client):
        """Test getting user cart"""
        response = await client.get("/api/v1/cart/user/1")
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == 1

    @pytest.mark.asyncio
    async def test_add_item_to_cart(self, client):
        """Test adding item to cart"""
        # First create a cart
        cart_response = await client.post("/api/v1/cart/", json={"user_id": 2})
        cart_id = cart_response.json()["id"]

        # Add item to cart
        item_data = {
            "product_id": 1,
            "product_name": "Burger",
            "product_description": "Delicious beef burger",
            "price": 12.99,
            "quantity": 2,
            "special_instructions": "No onions",
        }

        response = await client.post(f"/api/v1/cart/{cart_id}/items", json=item_data)
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == 1
        assert data["product_name"] == "Burger"
        assert data["quantity"] == 2
        assert data["subtotal"] == 25.98

    @pytest.mark.asyncio
    async def test_get_cart_items(self, client):
        """Test getting cart items"""
        # Create cart and add item
        cart_response = await client.post("/api/v1/cart/", json={"user_id": 3})
        cart_id = cart_response.json()["id"]

        item_data = {
            "product_id": 2,
            "product_name": "Pizza",
            "price": 15.99,
            "quantity": 1,
        }

        await client.post(f"/api/v1/cart/{cart_id}/items", json=item_data)

        # Get items
        response = await client.get(f"/api/v1/cart/{cart_id}/items")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["product_name"] == "Pizza"

    @pytest.mark.asyncio
    async def test_update_cart_item(self, client):
        """Test updating cart item"""
        # Create cart and add item
        cart_response = await client.post("/api/v1/cart/", json={"user_id": 4})
        cart_id = cart_response.json()["id"]

        item_data = {
            "product_id": 3,
            "product_name": "Fries",
            "price": 4.99,
            "quantity": 1,
        }

        item_response = await client.post(
            f"/api/v1/cart/{cart_id}/items", json=item_data
        )
        item_id = item_response.json()["id"]

        # Update item
        update_data = {"quantity": 3, "special_instructions": "Extra crispy"}
        response = await client.put(f"/api/v1/cart/items/{item_id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 3
        assert data["special_instructions"] == "Extra crispy"
        assert data["subtotal"] == 14.97

    @pytest.mark.asyncio
    async def test_remove_cart_item(self, client):
        """Test removing cart item"""
        # Create cart and add item
        cart_response = await client.post("/api/v1/cart/", json={"user_id": 5})
        cart_id = cart_response.json()["id"]

        item_data = {
            "product_id": 4,
            "product_name": "Drink",
            "price": 2.99,
            "quantity": 1,
        }

        item_response = await client.post(
            f"/api/v1/cart/{cart_id}/items", json=item_data
        )
        item_id = item_response.json()["id"]

        # Remove item
        response = await client.delete(f"/api/v1/cart/items/{item_id}")
        assert response.status_code == 204

        # Verify item is removed
        items_response = await client.get(f"/api/v1/cart/{cart_id}/items")
        assert len(items_response.json()) == 0

    @pytest.mark.asyncio
    async def test_clear_cart(self, client):
        """Test clearing all items from cart"""
        # Create cart and add multiple items
        cart_response = await client.post("/api/v1/cart/", json={"user_id": 6})
        cart_id = cart_response.json()["id"]

        items = [
            {"product_id": 5, "product_name": "Item1", "price": 10.0, "quantity": 1},
            {"product_id": 6, "product_name": "Item2", "price": 15.0, "quantity": 2},
        ]

        for item in items:
            await client.post(f"/api/v1/cart/{cart_id}/items", json=item)

        # Clear cart
        response = await client.delete(f"/api/v1/cart/{cart_id}/items")
        assert response.status_code == 204

        # Verify cart is empty
        items_response = await client.get(f"/api/v1/cart/{cart_id}/items")
        assert len(items_response.json()) == 0

    @pytest.mark.asyncio
    async def test_cart_not_found(self, client):
        """Test getting non-existent cart"""
        response = await client.get("/api/v1/cart/999")
        assert response.status_code == 404
        assert "Cart not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_item_not_found(self, client):
        """Test updating non-existent item"""
        response = await client.put("/api/v1/cart/items/999", json={"quantity": 1})
        assert response.status_code == 404
        assert "Cart item not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalid_item_data(self, client):
        """Test adding invalid item data"""
        cart_response = await client.post("/api/v1/cart/", json={"user_id": 7})
        cart_id = cart_response.json()["id"]

        # Invalid price
        invalid_item = {
            "product_id": 7,
            "product_name": "Invalid Item",
            "price": -5.0,  # Negative price
            "quantity": 1,
        }

        response = await client.post(f"/api/v1/cart/{cart_id}/items", json=invalid_item)
        assert response.status_code == 422  # Validation error

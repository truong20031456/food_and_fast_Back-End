import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from core.database import get_db, Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_order.db"

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

class TestOrder:
    
    @pytest.mark.asyncio
    async def setup_method(self, client):
        """Setup test data before each test"""
        # Create a cart with items for testing
        cart_response = await client.post("/api/v1/cart/", json={"user_id": 1})
        self.cart_id = cart_response.json()["id"]
        
        # Add items to cart
        items = [
            {
                "product_id": 1,
                "product_name": "Burger",
                "product_description": "Beef burger",
                "price": 12.99,
                "quantity": 2
            },
            {
                "product_id": 2,
                "product_name": "Fries",
                "price": 4.99,
                "quantity": 1
            }
        ]
        
        for item in items:
            await client.post(f"/api/v1/cart/{self.cart_id}/items", json=item)
    
    @pytest.mark.asyncio
    async def test_create_order(self, client):
        """Test creating order from cart"""
        order_data = {
            "delivery_address": "123 Main St, City, State 12345",
            "delivery_phone": "555-0123",
            "delivery_notes": "Ring the doorbell",
            "discount_amount": 2.0
        }
        
        response = await client.post(
            f"/api/v1/orders/?cart_id={self.cart_id}",
            json=order_data
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["user_id"] == 1
        assert data["delivery_address"] == order_data["delivery_address"]
        assert data["delivery_phone"] == order_data["delivery_phone"]
        assert data["status"] == "pending"
        assert data["payment_status"] == "pending"
        assert len(data["items"]) == 2
        assert data["total_amount"] == 30.97  # (12.99 * 2) + 4.99
        assert data["final_amount"] > 0  # Should include tax and delivery fee
        assert "order_number" in data
    
    @pytest.mark.asyncio
    async def test_get_order_by_id(self, client):
        """Test getting order by ID"""
        # Create order first
        order_data = {
            "delivery_address": "456 Oak Ave, City, State 12345",
            "delivery_phone": "555-0456"
        }
        
        create_response = await client.post(
            f"/api/v1/orders/?cart_id={self.cart_id}",
            json=order_data
        )
        order_id = create_response.json()["id"]
        
        # Get order
        response = await client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == order_id
        assert data["delivery_address"] == order_data["delivery_address"]
    
    @pytest.mark.asyncio
    async def test_get_order_by_number(self, client):
        """Test getting order by order number"""
        # Create order first
        order_data = {
            "delivery_address": "789 Pine St, City, State 12345",
            "delivery_phone": "555-0789"
        }
        
        create_response = await client.post(
            f"/api/v1/orders/?cart_id={self.cart_id}",
            json=order_data
        )
        order_number = create_response.json()["order_number"]
        
        # Get order by number
        response = await client.get(f"/api/v1/orders/number/{order_number}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["order_number"] == order_number
    
    @pytest.mark.asyncio
    async def test_get_user_orders(self, client):
        """Test getting orders for a user"""
        # Create multiple orders
        for i in range(3):
            cart_response = await client.post("/api/v1/cart/", json={"user_id": 2})
            cart_id = cart_response.json()["id"]
            
            # Add item to cart
            await client.post(
                f"/api/v1/cart/{cart_id}/items",
                json={
                    "product_id": i + 1,
                    "product_name": f"Product {i}",
                    "price": 10.0,
                    "quantity": 1
                }
            )
            
            # Create order
            await client.post(
                f"/api/v1/orders/?cart_id={cart_id}",
                json={
                    "delivery_address": f"Address {i}",
                    "delivery_phone": f"555-{i:04d}"
                }
            )
        
        # Get user orders
        response = await client.get("/api/v1/orders/user/2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    @pytest.mark.asyncio
    async def test_update_order_status(self, client):
        """Test updating order status"""
        # Create order first
        order_data = {
            "delivery_address": "123 Test St",
            "delivery_phone": "555-0000"
        }
        
        create_response = await client.post(
            f"/api/v1/orders/?cart_id={self.cart_id}",
            json=order_data
        )
        order_id = create_response.json()["id"]
        
        # Update status
        status_data = {"status": "confirmed"}
        response = await client.patch(f"/api/v1/orders/{order_id}/status", json=status_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"
    
    @pytest.mark.asyncio
    async def test_cancel_order(self, client):
        """Test cancelling an order"""
        # Create order first
        order_data = {
            "delivery_address": "456 Test Ave",
            "delivery_phone": "555-0001"
        }
        
        create_response = await client.post(
            f"/api/v1/orders/?cart_id={self.cart_id}",
            json=order_data
        )
        order_id = create_response.json()["id"]
        
        # Cancel order
        response = await client.patch(f"/api/v1/orders/{order_id}/cancel")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"
    
    @pytest.mark.asyncio
    async def test_order_not_found(self, client):
        """Test getting non-existent order"""
        response = await client.get("/api/v1/orders/999")
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
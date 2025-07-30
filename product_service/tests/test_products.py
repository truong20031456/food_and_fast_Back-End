import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from models.category import Category
from models.product import Product


@pytest.mark.asyncio
async def test_create_product(
    client: TestClient, db_session: AsyncSession, sample_product_data: dict
):
    """Test creating a product."""
    # First create a category
    category = Category(
        name="Test Category", slug="test-category", description="Test category"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Update product data with valid category_id
    sample_product_data["category_id"] = category.id

    response = client.post("/products/", json=sample_product_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_product_data["name"]
    assert data["slug"] == sample_product_data["slug"]
    assert data["price"] == sample_product_data["price"]
    assert data["sku"] == sample_product_data["sku"]


@pytest.mark.asyncio
async def test_get_product(
    client: TestClient, db_session: AsyncSession, sample_product_data: dict
):
    """Test getting a product by ID."""
    # First create a category
    category = Category(
        name="Test Category", slug="test-category", description="Test category"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create a product
    product = Product(
        name=sample_product_data["name"],
        slug=sample_product_data["slug"],
        description=sample_product_data["description"],
        price=sample_product_data["price"],
        category_id=category.id,
        sku=sample_product_data["sku"],
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    response = client.get(f"/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product.id
    assert data["name"] == product.name
    assert data["slug"] == product.slug


@pytest.mark.asyncio
async def test_get_product_not_found(client: TestClient):
    """Test getting a non-existent product."""
    response = client.get("/products/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_products(
    client: TestClient, db_session: AsyncSession, sample_product_data: dict
):
    """Test listing products."""
    # First create a category
    category = Category(
        name="Test Category", slug="test-category", description="Test category"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create a product
    product = Product(
        name=sample_product_data["name"],
        slug=sample_product_data["slug"],
        description=sample_product_data["description"],
        price=sample_product_data["price"],
        category_id=category.id,
        sku=sample_product_data["sku"],
    )
    db_session.add(product)
    await db_session.commit()

    response = client.get("/products/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["products"]) >= 1
    assert data["products"][0]["name"] == product.name


@pytest.mark.asyncio
async def test_update_product(
    client: TestClient, db_session: AsyncSession, sample_product_data: dict
):
    """Test updating a product."""
    # First create a category
    category = Category(
        name="Test Category", slug="test-category", description="Test category"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create a product
    product = Product(
        name=sample_product_data["name"],
        slug=sample_product_data["slug"],
        description=sample_product_data["description"],
        price=sample_product_data["price"],
        category_id=category.id,
        sku=sample_product_data["sku"],
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Update the product
    update_data = {"name": "Updated Product Name", "price": 39.99}
    response = client.put(f"/products/{product.id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["price"] == update_data["price"]


@pytest.mark.asyncio
async def test_delete_product(
    client: TestClient, db_session: AsyncSession, sample_product_data: dict
):
    """Test deleting a product."""
    # First create a category
    category = Category(
        name="Test Category", slug="test-category", description="Test category"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Create a product
    product = Product(
        name=sample_product_data["name"],
        slug=sample_product_data["slug"],
        description=sample_product_data["description"],
        price=sample_product_data["price"],
        category_id=category.id,
        sku=sample_product_data["sku"],
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    response = client.delete(f"/products/{product.id}")
    assert response.status_code == 200
    data = response.json()
    assert "deleted successfully" in data["message"]

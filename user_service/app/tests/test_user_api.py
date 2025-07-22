import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import AsyncMock, patch
import jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM


# Helper để tạo JWT hợp lệ
def generate_jwt(user_id: int):
    payload = {"sub": user_id}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@pytest.fixture(autouse=True)
def mock_redis():
    with patch("app.utils.redis_client.redis_client", autospec=True) as mock_redis:
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()
        mock_redis.delete = AsyncMock()
        yield mock_redis


@pytest.fixture(autouse=True)
def mock_auth_service():
    # Giả lập httpx.AsyncClient.post trả về xác thực token hợp lệ
    with patch(
        "app.dependencies.httpx.AsyncClient.post", new_callable=AsyncMock
    ) as mock_post:
        mock_post.return_value.json = AsyncMock(
            return_value={"user_id": 1, "valid": True}
        )
        mock_post.return_value.status_code = 200
        yield mock_post


client = TestClient(app)


def test_create_user():
    data = {
        "username": "apitestuser",
        "email": "apitest@example.com",
        "password": "password123",
        "profile": None,
    }
    response = client.post("/users/", json=data)
    assert response.status_code == 201
    user = response.json()
    assert user["username"] == data["username"]
    assert user["email"] == data["email"]
    assert user["is_active"] is True


def test_get_user():
    data = {
        "username": "apigetuser",
        "email": "apiget@example.com",
        "password": "password123",
        "profile": None,
    }
    create_resp = client.post("/users/", json=data)
    user_id = create_resp.json()["id"]
    token = generate_jwt(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/users/{user_id}", headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["id"] == user_id


def test_update_user():
    data = {
        "username": "apiupdateuser",
        "email": "apiupdate@example.com",
        "password": "password123",
        "profile": None,
    }
    create_resp = client.post("/users/", json=data)
    user_id = create_resp.json()["id"]
    token = generate_jwt(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"username": "updatedapiuser"}
    response = client.put(f"/users/{user_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    user = response.json()
    assert user["username"] == "updatedapiuser"


def test_soft_delete_user():
    data = {
        "username": "apideleteuser",
        "email": "apidelete@example.com",
        "password": "password123",
        "profile": None,
    }
    create_resp = client.post("/users/", json=data)
    user_id = create_resp.json()["id"]
    token = generate_jwt(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    del_resp = client.delete(f"/users/{user_id}", headers=headers)
    assert del_resp.status_code == 204
    get_resp = client.get(f"/users/{user_id}", headers=headers)
    assert get_resp.status_code == 404


def test_list_users():
    for i in range(3):
        client.post(
            "/users/",
            json={
                "username": f"apilistuser{i}",
                "email": f"apilistuser{i}@example.com",
                "password": "password123",
                "profile": None,
            },
        )
    token = generate_jwt(1)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/users/", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "users" in data
    assert data["total"] >= 3

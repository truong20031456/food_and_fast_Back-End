# Order Service

## Chạy local

```bash
cd order_service
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8005
```

## Chạy Docker

```bash
docker build -t order-service .
docker run -p 8005:8005 --env-file .env order-service
```

## Test

```bash
pytest
```

## Ví dụ API

### Tạo đơn hàng

**Request:**
```
POST /orders/
Content-Type: application/json
{
  "user_id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 101,
      "quantity": 2,
      "price": 19.99,
      "headers": {"Authorization": "Bearer token"}
    }
  ],
  "total": 39.98,
  "price": 39.98
}
```
**Response:**
```
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 101,
      "quantity": 2,
      "price": 19.99,
      "headers": {"Authorization": "Bearer token"}
    }
  ],
  "total": 39.98
}
```

### Lấy danh sách đơn hàng

**Request:**
```
GET /orders/
```
**Response:**
```
{
  "orders": [
    {
      "id": 1,
      "items": [
        {
          "id": 1,
          "product_id": 101,
          "quantity": 2,
          "price": 19.99,
          "headers": {"Authorization": "Bearer token"}
        }
      ],
      "total": 39.98
    }
  ]
}
```

### Cập nhật đơn hàng

**Request:**
```
PUT /orders/1
Content-Type: application/json
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 101,
      "quantity": 3,
      "price": 19.99,
      "headers": {"Authorization": "Bearer token"}
    }
  ],
  "total": 59.97
}
```
**Response:**
```
{
  "id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 101,
      "quantity": 3,
      "price": 19.99,
      "headers": {"Authorization": "Bearer token"}
    }
  ],
  "total": 59.97
}
```

### Xóa đơn hàng

**Request:**
```
DELETE /orders/1
```
**Response:**
```
{
  "detail": "Order deleted"
}
```

## Cấu trúc thư mục

- models/: SQLAlchemy models (Base, Order, Cart)
- schemas/: Pydantic schemas (OrderItem, OrderRead, ...)
- controllers/: FastAPI routers (order_controller)
- modules/: Business logic (orders, cart)
- main.py: FastAPI app entry
- requirements.txt, Dockerfile, README.md

## Cấu hình

- Sử dụng .env cho biến môi trường (DATABASE_URL, REDIS_URL, ...)
- Sẽ bổ sung core/config.py, core/database.py nếu cần

## CI/CD

- Đã có sẵn workflow tại .github/workflows/ci-order_service.yml
- Đảm bảo test, lint, build Docker, security scan 
# API Gateway - Food & Fast

## 1. Tổng quan

API Gateway là cửa ngõ trung tâm cho toàn bộ nền tảng microservices của Food & Fast. Nó đóng vai trò là điểm vào duy nhất (single entry point) cho tất cả các yêu cầu từ client (web, mobile).

**Các trách nhiệm chính:**

- **Định tuyến (Routing):** Định tuyến động các yêu cầu đến các microservice phù hợp dựa trên đường dẫn (path).
- **Xác thực & Phân quyền (Authentication & Authorization):** Đảm bảo chỉ những yêu cầu hợp lệ và đã được xác thực mới có thể truy cập vào các tài nguyên được bảo vệ.
- **Tổng hợp & Giao tiếp:** Giao tiếp với các service nội bộ và trả về phản hồi cho client.
- **Giám sát & Bảo mật:** Cung cấp một lớp bảo vệ, giám sát và ghi log tập trung.

---

## 2. Các tính năng cốt lõi

- **Dynamic Request Routing:** Tự động chuyển tiếp các yêu cầu đến các service tương ứng (Auth, User, Product, Order, v.v.) thông qua một cơ chế service registry.
- **Centralized Authentication:** Kiểm tra JWT token trên các route yêu cầu xác thực trước khi chuyển tiếp.
- **Service Discovery & Health Checks:** Tự động kiểm tra "sức khỏe" của các downstream services. Tích hợp cơ chế caching (sử dụng Redis) để giảm thiểu số lần health check không cần thiết.
- **Circuit Breaker Pattern:** Tự động "ngắt mạch" các yêu cầu đến một service nếu service đó liên tục báo lỗi, giúp ngăn ngừa lỗi hàng loạt (cascading failures) và cho phép service có thời gian phục hồi.
- **Observability:** Tự động thêm các header quan trọng vào mỗi yêu cầu (`X-Request-ID`, `X-Client-IP`, `X-User-ID`) để phục vụ cho việc logging và distributed tracing.

---

## 3. Hướng dẫn cài đặt và chạy Local

### Yêu cầu
- Python 3.11+
- Docker (để chạy Redis)
- Một virtual environment (ví dụ: `venv`)

### Các bước cài đặt
1.  **Clone a repository:**
    ```bash
    git clone https://github.com/your-username/food-fast-ecommerce.git
    cd food-fast-ecommerce/api_gateway
    ```

2.  **Tạo và kích hoạt môi trường ảo:**
    ```bash
    # Dành cho macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # Dành cho Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Cài đặt các dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình biến môi trường:**
    -   Sao chép file `.env.example` thành `.env`.
    -   Cập nhật các giá trị trong file `.env` cho phù hợp với môi trường local của bạn. Xem chi tiết ở mục **Biến môi trường**.

5.  **Chạy Redis (sử dụng Docker):**
    ```bash
    docker run -d -p 6379:6379 --name redis-gateway redis:7-alpine
    ```

6.  **Chạy API Gateway:**
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```
    Service sẽ chạy tại `http://localhost:8000`.

---

## 4. Chạy kiểm thử (Tests)

Để đảm bảo chất lượng code, hãy chạy bộ kiểm thử tự động. Cần có một instance Redis đang chạy để thực hiện test.

```bash
pytest -v --cov=.
```

---

## 5. API Endpoints

Dưới đây là các endpoint chính do API Gateway quản lý.

| Method | Endpoint | Mô tả | Yêu cầu xác thực |
| :--- | :--- | :--- | :--- |
| `ANY` | `/{path:path}` | **Proxy chính.** Chuyển tiếp tất cả các yêu cầu đến service tương ứng. | **Có** (trừ các path public) |
| `GET` | `/services/health` | Kiểm tra "sức khỏe" của tất cả các downstream services. | Không |
| `GET` | `/services` | Liệt kê tất cả các service đã đăng ký và các route của chúng. | Không |
| `POST` | `/auth/google` | Chuyển tiếp yêu cầu đăng nhập bằng Google đến `auth_service`. | Không |
| `GET` | `/auth/google/auth-url` | Lấy URL xác thực của Google từ `auth_service`. | Không |
| `POST` | `/auth/google/callback` | Xử lý callback từ Google sau khi xác thực thành công. | Không |

---

## 6. Biến môi trường (Environment Variables)

Các biến này cần được định nghĩa trong file `.env` để service có thể hoạt động.

| Tên biến | Mô tả | Ví dụ |
| :--- | :--- | :--- |
| `PYTHONPATH` | Thêm thư mục gốc của dự án vào Python path để import `shared_code`. | `.` |
| `SECRET_KEY` | Khóa bí mật chung cho các hoạt động mã hóa nội bộ. | `your-very-secret-key` |
| `JWT_SECRET_KEY` | **QUAN TRỌNG:** Khóa bí mật dùng để ký và xác thực JWT. **PHẢI GIỐNG NHAU** ở tất cả 8 services. | `your-shared-jwt-secret-key` |
| `REDIS_URL` | URL để kết nối đến Redis (dùng cho caching health check). | `redis://localhost:6379/0` |
| `AUTH_SERVICE_URL` | URL của Auth Service. | `http://localhost:8001` |
| `USER_SERVICE_URL` | URL của User Service. | `http://localhost:8002` |
| `PRODUCT_SERVICE_URL` | URL của Product Service. | `http://localhost:8003` |
| `ORDER_SERVICE_URL` | URL của Order Service. | `http://localhost:8004` |
| `PAYMENT_SERVICE_URL` | URL của Payment Service. | `http://localhost:8005` |
| `NOTIFICATION_SERVICE_URL` | URL của Notification Service. | `http://localhost:8006` |
| `ANALYTICS_SERVICE_URL` | URL của Analytics Service. | `http://localhost:8007` |
| `REQUEST_TIMEOUT` | Thời gian chờ (giây) tối đa cho một yêu cầu chuyển tiếp. | `30.0` |
| `HEALTH_CHECK_TIMEOUT` | Thời gian chờ (giây) tối đa cho một lần kiểm tra health check. | `5.0` |

---

## 7. Quy trình CI/CD

Pipeline CI/CD cho API Gateway được định nghĩa trong `.github/workflows/ci-api_gateway.yml` và bao gồm các bước chính sau:

1.  **Lint & Format:** Kiểm tra code style với `black` và `flake8`, kiểm tra type-hinting với `mypy`.
2.  **Security Scan:** Quét lỗ hổng bảo mật với `bandit` và kiểm tra các dependency không an toàn với `safety`.
3.  **Run Tests:** Chạy bộ unit test và integration test với `pytest` và tạo báo cáo độ bao phủ code (coverage report).
4.  **Docker Build:** Xây dựng Docker image và chạy một bài test đơn giản trên container.
5.  **Build & Push:** (Khi push lên các nhánh `main`, `develop`) Build và đẩy Docker image lên Docker Hub.
6.  **Deploy:** (Tương lai) Tự động deploy lên môi trường Staging hoặc Production.

---

## 8. JWT_SECRET_KEY - Quan trọng!

**JWT_SECRET_KEY phải được cấu hình giống nhau ở tất cả 8 services:**

- **API Gateway** (Port 8000)
- **Auth Service** (Port 8001) 
- **User Service** (Port 8002)
- **Product Service** (Port 8003)
- **Order Service** (Port 8004)
- **Payment Service** (Port 8005)
- **Notification Service** (Port 8006)
- **Analytics Service** (Port 8007)

### Tại sao cần dùng chung?

1. **Token Validation**: API Gateway cần validate JWT token trước khi forward request
2. **Cross-Service Auth**: Các services khác cần validate token để xác thực user
3. **Microservices Security**: Tất cả services phải "tin tưởng" cùng một secret key

### Cách triển khai:

```bash
# Trong tất cả .env files của 8 services
JWT_SECRET_KEY=your-super-secret-jwt-key-that-must-be-identical
```

---

## 9. Đóng góp

Nếu bạn muốn đóng góp, vui lòng tạo một Issue để thảo luận hoặc một Pull Request với những thay đổi của bạn.
# JWT_SECRET_KEY Setup Guide

## Tổng quan

`JWT_SECRET_KEY` là một biến môi trường **QUAN TRỌNG** phải được cấu hình **GIỐNG NHAU** ở tất cả 8 services trong hệ thống Food & Fast.

## Danh sách Services cần JWT_SECRET_KEY

| Service | Port | Mục đích sử dụng |
|---------|------|------------------|
| API Gateway | 8000 | Validate JWT tokens trước khi forward requests |
| Auth Service | 8001 | Sign và issue JWT tokens |
| User Service | 8002 | Validate tokens để xác thực user operations |
| Product Service | 8003 | Validate tokens cho user-specific product operations |
| Order Service | 8004 | Validate tokens để xác thực order operations |
| Payment Service | 8005 | Validate tokens cho payment operations |
| Notification Service | 8006 | Validate tokens cho notification preferences |
| Analytics Service | 8007 | Validate tokens cho user analytics |

## Cách cấu hình

### 1. Tạo JWT Secret Key mạnh

```bash
# Tạo một secret key mạnh (64 ký tự)
openssl rand -hex 32
# Hoặc sử dụng Python
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Cấu hình trong tất cả .env files

```bash
# Trong tất cả 8 services, thêm vào file .env:
JWT_SECRET_KEY=your-generated-secret-key-here
```

### 3. Ví dụ cấu hình

```bash
# api_gateway/.env
JWT_SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456

# auth_service/.env  
JWT_SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456

# user_service/.env
JWT_SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456

# ... và tương tự cho 5 services còn lại
```

## Kiểm tra cấu hình

### 1. Test JWT Token Generation (Auth Service)

```bash
# Test tạo token
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### 2. Test JWT Token Validation (API Gateway)

```bash
# Test validate token
curl -X GET http://localhost:8000/api/v1/users/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### Lỗi thường gặp

1. **"Invalid token"**: JWT_SECRET_KEY không giống nhau giữa các services
2. **"Token expired"**: Token đã hết hạn (kiểm tra ACCESS_TOKEN_EXPIRE_MINUTES)
3. **"Invalid signature"**: JWT_SECRET_KEY bị thay đổi sau khi token được tạo

### Debug Steps

1. Kiểm tra JWT_SECRET_KEY ở tất cả services
2. Verify token format và expiration
3. Check logs của Auth Service và API Gateway
4. Test với Postman hoặc curl

## Security Best Practices

1. **Không commit JWT_SECRET_KEY vào Git**
2. **Sử dụng secret management service** (AWS Secrets Manager, HashiCorp Vault)
3. **Rotate JWT_SECRET_KEY định kỳ**
4. **Monitor JWT token usage**
5. **Set appropriate token expiration times**

## Production Deployment

```bash
# Sử dụng environment variables
export JWT_SECRET_KEY="your-production-secret-key"

# Hoặc trong Docker Compose
environment:
  - JWT_SECRET_KEY=${JWT_SECRET_KEY}
```

## Monitoring

- Monitor JWT token validation failures
- Track token expiration patterns
- Alert on unusual JWT usage patterns
- Log JWT-related security events 
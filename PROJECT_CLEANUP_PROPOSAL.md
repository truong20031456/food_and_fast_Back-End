# 🧹 Project Cleanup & Simplification Proposal

## 🎯 **MỤC TIÊU**
- Loại bỏ file không cần thiết
- Hợp nhất cấu trúc trùng lặp
- Tối giản hóa để dễ đọc, dễ hiểu
- Chuẩn hóa cấu trúc microservices

## 🗑️ **1. CÁC FILE CẦN LOẠI BỎ**

### A. File tạm thời và cache
```bash
# Xóa tất cả cache Python
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} +
find . -name ".ruff_cache" -type d -exec rm -rf {} +

# Xóa file cache môi trường (có thể tạo lại)
rm -f **/.env.cache
```

### B. File GitHub workflows trùng lặp
**HIỆN TẠI**: Mỗi service có file CI/CD riêng
```
.github/workflows/main.yml                     # Keep
.github/workflows/e2e-testing.yml             # Keep
analytics_service/.github/                     # DELETE
api_gateway/.github/                          # DELETE
auth_service/.github/                         # DELETE
notification_service/.github/                 # DELETE
order_service/.github/                        # DELETE
payment_service/.github/                      # DELETE
product_service/.github/                      # DELETE
user_service/.github/                         # DELETE
```
**ĐÍNH KÈM**: Chỉ giữ lại 2 file CI/CD ở root level

### C. File env.example trùng lặp
**HIỆN TẠI**: 
```
shared_code/env.example                       # Keep (template chung)
api_gateway/env.example                       # DELETE
api_gateway/.env.example                      # Keep (rename)
```

### D. File báo cáo và documentation có thể hợp nhất
```
CI_CD_ENHANCEMENT_REPORT.md                   # DELETE (merge vào README)
CI_FIX_REPORT.md                             # DELETE (merge vào README)
SERVICE_ARCHITECTURE_STANDARD.md             # Keep nhưng rút gọn
SHARED_CODE_STRUCTURE.md                     # Keep nhưng rút gọn
```

## 🔄 **2. HỢP NHẤT CẤU TRÚC TRÙNG LẶP**

### A. Chuẩn hóa cấu trúc service
**TRƯỚC**:
```
# Cấu trúc không nhất quán
analytics_service/
├── controllers/
├── core/
├── models/
├── services/

product_service/
├── controllers/
├── modules/        # Khác biệt
├── models/
├── core/

user_service/
├── app/
│   ├── controllers/  # Thêm layer app
│   ├── models/
│   └── services/
```

**SAU** (Chuẩn hóa):
```
{service_name}/
├── main.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── README.md
├── api/
│   └── routers/
├── core/
│   ├── config.py
│   └── database.py
├── models/
├── schemas/
├── services/
└── tests/
```

### B. Hợp nhất main.py patterns
**TRƯỚC**: 3 patterns khác nhau:
1. Manual FastAPI setup (payment, product, analytics, notification)
2. Shared app factory (auth, user, order, api_gateway)
3. Mixed approaches

**SAU**: Tất cả sử dụng shared app factory:
```python
# Standard pattern cho tất cả services
from shared_code.core.app import create_app
from shared_code.core.config import get_service_settings

settings = get_service_settings("{service_name}")

app = create_app(
    service_name="{Service Name}",
    settings=settings,
    routers=[router1, router2],
    startup_tasks=[startup_task],
    shutdown_tasks=[shutdown_task],
)
```

## 📦 **3. TỐI GIẢN HÓA SHARED_CODE**

### A. Cấu trúc hiện tại phức tạp:
```
shared_code/
├── cache/
│   ├── base_cache.py
│   ├── cache_manager.py
│   ├── redis_client.py
│   └── legacy_cache_service.py    # LOẠI BỎ
├── core/
├── middleware/                    # TRỐNG - LOẠI BỎ
├── models/
├── monitoring/
├── services/                      # TRỐNG - LOẠI BỎ
└── utils/
```

### B. Cấu trúc tối giản:
```
shared_code/
├── __init__.py
├── README.md
├── core/               # Core functionality
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   └── exceptions.py
├── cache/              # Cache system
│   ├── __init__.py
│   ├── manager.py      # Merge cache_manager + redis_client
│   └── service.py      # Merge base_cache + legacy
├── utils/              # Utilities
│   ├── logging.py
│   ├── security.py
│   └── validation.py
└── models/             # Shared models
    ├── __init__.py
    └── base.py
```

## 🗂️ **4. ĐƠN GIẢN HÓA DOCKER COMPOSE**

### A. Hiện tại có quá nhiều file:
```
docker-compose.yml           # Development
docker-compose.prod.yml      # Production
docker-compose.staging.yml   # Staging  
docker-compose.test.yml      # Testing
```

### B. Đề xuất:
```
docker-compose.yml           # Development (default)
docker-compose.override.yml  # Local overrides
docker-compose.prod.yml      # Production
```

## 📋 **5. HỢP NHẤT DOCUMENTATION**

### A. Merge reports vào README chính:
```
README.md (enhanced)
├── Architecture Overview
├── Quick Start
├── Services
├── Development
├── CI/CD Pipeline    # From CI_CD_ENHANCEMENT_REPORT.md
├── Service Standards # From SERVICE_ARCHITECTURE_STANDARD.md
├── Shared Code      # From SHARED_CODE_STRUCTURE.md
└── Troubleshooting  # From CI_FIX_REPORT.md
```

### B. Service READMEs:
- Giữ README riêng cho mỗi service
- Chuẩn hóa template
- Tập trung vào usage và API

## 🎯 **6. BENEFITS SAU KHI CLEANUP**

### A. Giảm complexity:
- **Trước**: ~150+ files config/docs
- **Sau**: ~50 files cần thiết

### B. Chuẩn hóa:
- Tất cả services follow same pattern
- Shared code structure đơn giản
- Documentation tập trung

### C. Dễ maintain:
- Ít file trùng lặp
- Pattern nhất quán
- Onboarding nhanh hơn

## 🚀 **7. IMPLEMENTATION PLAN**

### Phase 1: Cleanup files
1. Xóa cache và temp files
2. Xóa duplicate CI/CD configs  
3. Consolidate env files

### Phase 2: Standardize services
1. Chuẩn hóa main.py pattern
2. Restructure service directories
3. Update imports và dependencies

### Phase 3: Simplify shared_code
1. Merge duplicate cache modules
2. Remove empty directories
3. Update documentation

### Phase 4: Documentation
1. Merge reports vào README
2. Update service READMEs
3. Create migration guide

## ❓ **8. QUYẾT ĐỊNH CẦN THẢO LUẬN**

1. **Có xóa các file .env.cache không?** (Có thể regenerate)
2. **Có merge tất cả docker-compose files?** 
3. **Service nào priority cao nhất để refactor trước?**
4. **Có giữ lại git history cho moved files?**

---

**Tóm tắt**: Proposal này sẽ giảm ~60% files không cần thiết, chuẩn hóa 100% service structure, và tạo ra codebase dễ đọc, dễ maintain hơn.

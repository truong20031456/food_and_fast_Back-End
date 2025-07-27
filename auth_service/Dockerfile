FROM python:3.13.5-slim

WORKDIR /app

# Cài đặt các dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy toàn bộ mã nguồn vào image
COPY . .

# Thiết lập biến môi trường (nếu cần, có thể thêm vào đây)
# ENV DATABASE_URL=...
# ENV REDIS_URL=...
# ENV SECRET_KEY=...

# Chạy ứng dụng
CMD ["python", "main.py"]

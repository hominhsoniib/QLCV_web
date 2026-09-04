# Hướng Dẫn Triển Khai Hệ Thống (Deployment Guide)

Tài liệu này hướng dẫn chi tiết cách triển khai, cấu hình môi trường và cài đặt các dịch vụ tích hợp cho dự án AMS PRO 5.0 (QLCV Python).

## 1. Yêu Cầu Hệ Thống

- **Hệ điều hành:** Windows / Linux / macOS
- **Python version:** 3.9 trở lên
- **Thư viện chính:** FastAPI, Uvicorn, SQLAlchemy, Pandas, Python-multipart

## 2. Các Bước Cài Đặt Cục Bộ

1. **Clone hoặc tải mã nguồn:** Đảm bảo toàn bộ thư mục `QLCV_Python` đã được lưu tại vị trí mong muốn.
2. **Cài đặt thư viện:** Chạy lệnh sau để cài đặt các package trong `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình môi trường (.env):**
   Sao chép tệp `.env.example` thành `.env` và cấu hình các khoá bảo mật:
   - `SECRET_KEY`: Khóa ký phiên cookie (Có thể tự sinh chuỗi ngẫu nhiên bằng lệnh: `python -c "import secrets; print(secrets.token_hex(32))"`).
   - `DATABASE_URL`: Đường dẫn CSDL. Mặc định `sqlite:///qlcv.db` được cấu hình để chạy trực tiếp không cần cài đặt SQL Server.
   - `GOOGLE_SPREADSHEET_ID`: Nhập ID của Spreadsheet gốc nếu muốn đồng bộ hóa dữ liệu trực tuyến.
4. **Chuẩn bị file seed Excel:**
   Đặt tệp `seed.xlsx` ở thư mục gốc của dự án. Server sẽ tự động quét tệp này khi khởi chạy lần đầu để tạo và điền dữ liệu cho các bảng SQLite.
5. **Khởi chạy hệ thống:**
   Khởi chạy server uvicorn:
   ```bash
   uvicorn app:app --reload --port 8000
   ```

---

## 3. Thiết Lập Tích Hợp Google Drive API (Không bắt buộc)

Để kích hoạt tính năng chọn tệp từ Google Drive qua picker và đổi tên tệp tự động trên server:

1. Truy cập [Google Cloud Console](https://console.cloud.google.com/).
2. Tạo một dự án mới (Project).
3. Bật **Google Drive API** và **Google Picker API**.
4. Truy cập trang **Credentials**:
   - Tạo **API Key** (dùng cho Picker ở client-side).
   - Tạo **OAuth Client ID** (dùng cho xác thực người dùng Picker).
   - Tạo **Service Account** (tài khoản dịch vụ):
     - Tạo và tải xuống khoá dạng **JSON** cho Service Account này.
     - Đổi tên tệp khóa này thành `credentials.json` và đặt tại thư mục gốc của dự án `QLCV_Python`.
     - Cấp quyền truy cập cho email của Service Account này vào thư mục Drive dùng chung của bạn.
5. Cấu hình đường dẫn tệp JSON này trong file `.env` tại khoá `GOOGLE_APPLICATION_CREDENTIALS`.

*Lưu ý: Nếu không cấu hình Google API, hệ thống vẫn hoạt động hoàn toàn bình thường nhờ cơ chế tải file lên thư mục cục bộ `static/uploads`.*

---

## 4. Deploy Lên Production (Docker & VPS)

### Chạy bằng Uvicorn trong nền (Background)
Để chạy FastAPI trên VPS Linux dạng dịch vụ nền (Daemon):
```bash
nohup uvicorn app:app --host 0.0.0.0 --port 8000 > server.log 2>&1 &
```
Hoặc cấu hình qua **Systemd Service** của Linux để tự động restart khi server gặp sự cố.

### Triển khai Nginx Reverse Proxy (Khuyên dùng)
Cấu hình file Nginx cấu khống cổng 80/443 về Uvicorn cổng 8000:
```nginx
server {
    listen 80;
    server_name amspro.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/QLCV_Python/static/;
    }
}
```

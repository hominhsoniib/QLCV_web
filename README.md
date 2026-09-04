# AMS PRO 5.0 - Quản Lý Công Việc (QLCV) Python Migration

Dự án chuyển đổi hoàn chỉnh hệ thống Quản lý Công việc (QLCV) doanh nghiệp từ nền tảng **Google Apps Script** sang **Python Web Application** sử dụng **FastAPI**, **Jinja2**, và **SQLAlchemy**.

## 🚀 Tính Năng Nổi Bật

1. **REST API & Cơ sở dữ liệu:** Chuyển đổi toàn bộ truy vấn Apps Script `google.script.run` thành các REST API và lưu trữ Google Sheets thành SQLite Database qua SQLAlchemy ORM.
2. **Đồng bộ tự động & Seeding:** Tự động tạo cấu trúc bảng SQLite và seed đồng bộ toàn bộ 131 nhân viên, 111 công việc, 14 phòng ban từ file Excel (`seed.xlsx`) khi khởi chạy server lần đầu.
3. **Phân quyền & Phiên làm việc (Session):** Hệ thống signed cookie bảo mật, phân tách quyền hạn (ADMIN/MANAGER/USER).
4. **Google Drive Integration & Local Storage:** Tích hợp file upload lưu trữ cục bộ tại thư mục `static/uploads` song song với việc hỗ trợ Google Drive API tự động đổi tên file picked theo mã công việc.
5. **Giao diện hiện đại (SPA):** Thiết kế Dark Mode chuyên nghiệp, tối giản, glassmorphism với Bootstrap 4.5 và Outfit/Inter fonts.

## 🛠️ Công Nghệ Sử Dụng

- **Backend:** FastAPI (Python 3.9+)
- **Database ORM:** SQLAlchemy
- **Database Engine:** SQLite (Dễ dàng mở rộng sang PostgreSQL/MySQL)
- **HTML Templates:** Jinja2
- **Thống kê & Đọc Sheet Excel:** Pandas, OpenPyXL
- **CSS Framework:** Custom Tailwind-style CSS & Bootstrap 4.5.2
- **Google API Client:** google-api-python-client, google-auth

## 📂 Cấu Trúc Thư Mục Dự Án

```
QLCV_Python
├── app.py              # File chạy chính của server FastAPI
├── config.py           # Quản lý hằng số & Đọc .env
├── seed.xlsx           # File Excel dữ liệu đồng bộ từ Google Sheets
├── qlcv.db             # Database SQLite tự động sinh ra
├── database/
│   └── connection.py   # Thiết lập session SQLAlchemy
├── models/
│   └── models.py       # Khai báo các Table Model
├── routes/
│   ├── auth.py         # Routes Đăng nhập, Logout, Stats
│   ├── tasks.py        # Routes Quản lý & Cập nhật Công việc
│   ├── master.py       # Routes Phòng ban & Nhân sự CRUD
│   └── documents.py    # Routes Thư mục Tài liệu & File Upload
├── services/
│   ├── auth_service.py # Xác thực & Dashboard Stats
│   ├── task_service.py # Core logic Công việc (Báo cáo, Nhắc nhở, Ủy quyền)
│   ├── department_service.py # CRUD phòng ban
│   ├── employee_service.py   # CRUD nhân sự
│   ├── document_service.py   # CRUD tài liệu & Tự sinh mã tài liệu
│   ├── drive_service.py      # Local upload & Google Drive API rename
│   └── sheet_service.py      # Import dữ liệu Excel sang DB
├── static/
│   ├── css/
│   ├── js/
│   └── uploads/        # Lưu trữ các file đính kèm cục bộ
└── templates/          # Thư mục chứa các tệp HTML Jinja2
```

## ⚙️ Hướng Dẫn Chạy Nhanh

1. Cài đặt các thư viện phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
2. Cấu hình file `.env` (được tạo sẵn từ `.env.example`).
3. Khởi chạy Uvicorn Server:
   ```bash
   python app.py
   ```
   hoặc chạy trực tiếp qua Uvicorn để tự động reload khi sửa code:
   ```bash
   uvicorn app:app --reload --port 8000
   ```
4. Truy cập địa chỉ `http://localhost:8000` và đăng nhập bằng tài khoản:
   - **Tài khoản:** `CEO` hoặc `ADMIN`
   - **Mật khẩu:** `Ceo@123456` (đối với `CEO`) hoặc `admin` (đối với `ADMIN`)

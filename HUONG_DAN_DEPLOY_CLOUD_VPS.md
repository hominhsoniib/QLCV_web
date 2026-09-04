# 🚀 HƯỚNG DẪN CHI TIẾT DEPLOY HỆ THỐNG WEB LÊN CLOUD VPS (CHẠY 24/7 ONLINE)

Tài liệu này hướng dẫn chi tiết từng bước đưa hệ thống **AMS PRO 5.0 & NEXUS CRM & QUOTEFLOW OS** lên máy chủ Cloud VPS để toàn bộ nhân viên có thể truy cập bằng trình duyệt web từ bất kỳ đâu (ở nhà, quán cafe, di động 4G,...) 24/7.

---

## 📌 MỤC LỤC
1. [Bước 1: Thuê Cloud VPS & Đăng ký Tên miền](#bước-1-thuê-cloud-vps--đăng-ký-tên-miền)
2. [Bước 2: Trỏ Tên miền (DNS) về VPS](#bước-2-trỏ-tên-miền-dns-về-vps)
3. [Bước 3: Tải mã nguồn & Cài đặt môi trường trên VPS](#bước-3-tải-mã-nguồn--cài-đặt-môi-trường-trên-vps)
4. [Bước 4: Cấu hình Nginx & Cấp SSL (HTTPS) miễn phí](#bước-4-cấu-hình-nginx--cấp-ssl-https-miễn-phí)
5. [Bước 5: Chạy ứng dụng tự động 24/7 với Systemd](#bước-5-chạy-ứng-dụng-tự-động-247-với-systemd)
6. [Bước 6: Kiểm tra & Quản lý tài khoản nhân viên](#bước-6-kiểm-tra--quản-lý-tài-khoản-nhân-viên)

---

## 🖥️ BƯỚC 1: THUÊ CLOUD VPS & ĐĂNG KÝ TÊN MIỀN

### 1. Thuê máy chủ Cloud VPS
Bạn có thể chọn thuê máy chủ ảo (Cloud VPS) tại các nhà cung cấp Việt Nam để có tốc độ truy cập nhanh nhất:
- **Nhà cung cấp đề xuất:** Vietnix, AZDIGI, CloudFly, TinoHost, KDATA, vHost, hoặc VPS quốc tế (DigitalOcean, Vultr).
- **Cấu hình đề xuất (Phù hợp 10 - 100 nhân viên):**
  - **CPU:** 2 vCPU
  - **RAM:** 2 GB - 4 GB
  - **Ổ cứng:** 25 GB - 50 GB SSD / NVMe
  - **Hệ điều hành (OS):** **Ubuntu 22.04 LTS 64-bit** *(Khuyên dùng)*
  - **Chi phí:** Khoảng `50.000đ - 150.000đ / tháng`.

### 2. Tên miền (Domain)
- Nếu đã có tên miền công ty (VD: `congty.com`), bạn tạo sub-domain như `app.congty.com`.
- Nếu chưa có tên miền, bạn có thể truy cập bằng IP của VPS (VD: `http://103.x.x.x:8000`).

---

## 🌐 BƯỚC 2: TRỎ TÊN MIỀN (DNS) VỀ VPS

Vào trang quản lý tên miền (như Pavietnam, TENTEN, Cloudflare, Mắt Bão, vHost...), tạo bản ghi (A Record):

| Loại (Type) | Tên bản ghi (Host / Name) | Giá trị (Value / IP Address) |
| :--- | :--- | :--- |
| **A** | `app` (hoặc `app.congty.com`) | `IP_CỦA_VPS` (ví dụ: `103.123.45.67`) |
| **A** | `baogia` (hoặc `baogia.congty.com`) | `IP_CỦA_VPS` (ví dụ: `103.123.45.67`) |

---

## 📦 BƯỚC 3: TẢI MÃ NGUỒN & CÀI ĐẶT TRÊN VPS

### 1. Kết nối vào VPS bằng SSH
Mở Command Prompt (Window) hoặc Terminal (Mac) và gõ lệnh:
```bash
ssh root@IP_CỦA_VPS
```

### 2. Cập nhật hệ thống & Chạy script tự động
Upload toàn bộ thư mục dự án lên `/var/www/QLCV_web` rồi cấp quyền và chạy script `deploy_vps.sh`:
```bash
cd /var/www/QLCV_web
chmod +x deploy_vps.sh
./deploy_vps.sh
```

---

## 🔒 BƯỚC 4: CẤU HÌNH NGINX & CẤP SSL (HTTPS) MIỄN PHÍ

Nginx giúp ẩn cổng `8000` và `8502`, cho phép nhân viên gõ tên miền chuẩn SSL bảo mật `https://app.congty.com`.

### 1. Tạo file cấu hình Nginx
```bash
sudo nano /etc/nginx/sites-available/nexus-app
```

Dán nội dung sau vào file:
```nginx
server {
    listen 80;
    server_name app.congty.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name baogia.congty.com;

    location / {
        proxy_pass http://127.0.0.1:8502;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Kích hoạt Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/nexus-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Cấp chứng chỉ SSL (HTTPS) miễn phí
```bash
sudo certbot --nginx -d app.congty.com -d baogia.congty.com
```

---

## ⚙️ BƯỚC 5: KIỂM TRA TRẠNG THÁI DỊCH VỤ

Kiểm tra trạng thái của các service ngầm:
```bash
sudo systemctl status nexus-app
sudo systemctl status nexus-quoteflow
```

---

## 👤 BƯỚC 6: ĐĂNG NHẬP & SỬ DỤNG

1. Mở trình duyệt bất kỳ nhập `https://app.congty.com`.
2. Đăng nhập bằng tài khoản:
   - **Tài khoản:** `CEO` hoặc `ADMIN`
   - **Mật khẩu:** `Ceo@123456` hoặc `admin`
3. Tất cả các phân hệ CRM, Quản lý công việc, Thư mục tài liệu, Sơ đồ tổ chức, JD, Quy trình, Báo giá đều hoạt động đồng bộ 24/7!

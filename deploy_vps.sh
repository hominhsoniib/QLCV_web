#!/bin/bash
# ============================================================
# SCRIPT DEPLOY TỰ ĐỘNG AMS PRO QLCV WEB LÊN CLOUD VPS
# Hỗ trợ OS: Ubuntu 20.04 / 22.04 LTS
# ============================================================

set -e

echo "============================================================"
echo "  BẮT ĐẦU TỰ ĐỘNG TẠO MÔI TRƯỜNG & DEPLOY LÊN VPS"
echo "============================================================"

# Update system packages
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git curl

APP_DIR=$(pwd)
echo "[1/4] Thư mục ứng dụng hiện tại: $APP_DIR"

# Create Python Virtual Environment
echo "[2/4] Đang khởi tạo môi trường ảo venv..."
python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi
pip install uvicorn gunicorn python-docx

# Systemd Service setup for FastAPI
echo "[3/4] Cấu hình Systemd Service cho FastAPI Server (Host 0.0.0.0 - Port 8081)..."
sudo cat <<EOF | sudo tee /etc/systemd/system/nexus-app.service
[Unit]
Description=AMS PRO QLCV Web Service
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8081 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Open Linux UFW Firewall for QLCV and HTTP/HTTPS
if command -v ufw > /dev/null; then
    echo "[3c/4] Mở cổng Tường lửa UFW cho port 8081, 80 và 443..."
    sudo ufw allow 8081/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw reload || true
fi

# Reload and start services
echo "[4/4] Kích hoạt và khởi chạy các dịch vụ..."
sudo systemctl daemon-reload
sudo systemctl enable nexus-app
sudo systemctl restart nexus-app

echo "============================================================"
echo "  DEPLOY THÀNH CÔNG!"
echo "  - Backend FastAPI running on: http://0.0.0.0:8081"
echo "  - Truy cập trực tiếp: http://app.badenfarm.com.vn:8081"
echo "============================================================"

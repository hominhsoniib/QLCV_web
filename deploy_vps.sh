#!/bin/bash
# ============================================================
# SCRIPT DEPLOY TỰ ĐỘNG AMS PRO & NEXUS-CRM WEB LÊN CLOUD VPS
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
if [ -f "Bao-gia/requirements.txt" ]; then
    pip install -r Bao-gia/requirements.txt
fi
pip install uvicorn gunicorn streamlit python-docx

# Systemd Service setup for FastAPI
echo "[3/4] Cấu hình Systemd Service cho FastAPI Server..."
sudo cat <<EOF | sudo tee /etc/systemd/system/nexus-app.service
[Unit]
Description=AMS PRO & NEXUS-CRM Web Service
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Systemd Service setup for Streamlit QuoteFlow
if [ -d "Bao-gia" ]; then
echo "[3b/4] Cấu hình Systemd Service cho Streamlit QuoteFlow Server..."
sudo cat <<EOF | sudo tee /etc/systemd/system/nexus-quoteflow.service
[Unit]
Description=QuoteFlow Streamlit Service
After=network.target

[Service]
User=root
WorkingDirectory=$APP_DIR/Bao-gia
ExecStart=$APP_DIR/venv/bin/python3 -m streamlit run app.py --server.port 8502 --server.address 127.0.0.1 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
EOF
fi

# Reload and start services
echo "[4/4] Kích hoạt và khởi chạy các dịch vụ..."
sudo systemctl daemon-reload
sudo systemctl enable nexus-app
sudo systemctl restart nexus-app

if [ -d "Bao-gia" ]; then
    sudo systemctl enable nexus-quoteflow
    sudo systemctl restart nexus-quoteflow
fi

echo "============================================================"
echo "  DEPLOY THÀNH CÔNG!"
echo "  - Backend FastAPI running on: http://127.0.0.1:8000"
if [ -d "Bao-gia" ]; then
echo "  - Streamlit Báo giá running on: http://127.0.0.1:8502"
fi
echo "============================================================"

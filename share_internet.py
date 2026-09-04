import os
import sys
import urllib.request
import subprocess
import re
import time
import webbrowser

# Tải cấu hình port từ dự án
try:
    from config import Config
    PORT = Config.PORT
except Exception:
    PORT = 8081
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("PORT="):
                    try:
                        PORT = int(line.strip().split("=")[1])
                    except ValueError:
                        pass

CLOUDFLARED_EXE = "cloudflared.exe"
DOWNLOAD_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

def download_cloudflared():
    print("============================================================")
    print("           TAI BO CHIA SE MANG CLOUDFLARED")
    print("============================================================")
    print(f"[*] Dang tai {CLOUDFLARED_EXE} tu GitHub Cloudflare...")
    print("Vui long cho trong giay lat (khoang 30MB-40MB)...")
    
    def progress_hook(count, block_size, total_size):
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write(f"\r[+] Tien trinh tai: {percent}%")
        sys.stdout.flush()

    try:
        urllib.request.urlretrieve(DOWNLOAD_URL, CLOUDFLARED_EXE, progress_hook)
        print("\n[+] Tai thanh cong cloudflared.exe!")
    except Exception as e:
        print(f"\n[ERROR] Khong the tai tu dong: {e}")
        print("Vui long tai thu cong tu link sau va luu vao thu muc du an:")
        print(DOWNLOAD_URL)
        sys.exit(1)

def run_tunnel():
    if not os.path.exists(CLOUDFLARED_EXE):
        download_cloudflared()
        
    print(f"\n[*] Dang khoi tao duong truyen bao mat HTTP2 (Tunnel) cho port {PORT}...")
    
    # Chay cloudflared tunnel voi giao thuc HTTP2 (TCP) hoan toan on dinh tai Viet Nam
    cmd = [CLOUDFLARED_EXE, "tunnel", "--protocol", "http2", "--url", f"http://127.0.0.1:{PORT}"]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    tunnel_url = None
    
    print("[*] Dang cho Cloudflare cap dia chi Web cong khai...")
    start_time = time.time()
    
    while True:
        if process.poll() is not None:
            print("[ERROR] Tien trinh chia se mang da dung dot ngot!")
            stderr_out = process.stderr.read()
            print(stderr_out)
            break
            
        line = process.stderr.readline()
        if not line:
            time.sleep(0.1)
            continue
            
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match:
            tunnel_url = match.group(0)
            print("\n" + "=" * 60)
            print("THANH CONG! DA DUA UNG DUNG LEN INTERNET (HTTP2 MODE):")
            print(f"LIEN KET CUA BAN: {tunnel_url}")
            print("=" * 60 + "\n")
            print("[*] Tu dong mo lien ket tren trinh duyet cua ban...")
            webbrowser.open(tunnel_url)
            print("[*] Bat ky ai tren the gioi cung co the truy cap qua link tren.")
            print("[*] Giu cua so nay chay de duy tri ket noi Internet. Nhan Ctrl+C de dung.")
            print("-" * 60)
            
        if tunnel_url:
            if "HTTP" in line or "error" in line.lower() or "connection" in line.lower():
                print(line.strip())
        else:
            print(line.strip())
            
        if not tunnel_url and time.time() - start_time > 30:
            print("[WARNING] Dang mat nhieu thoi gian de lay lien ket. Vui long kiem tra ket noi mang!")
            start_time = time.time()

if __name__ == "__main__":
    try:
        run_tunnel()
    except KeyboardInterrupt:
        print("\n[+] Dang dung ket noi Internet. Tam biet!")

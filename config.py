import os
import secrets
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


def _resolve_secret_key() -> str:
    """Resolves SECRET_KEY from the environment. NEVER falls back to a fixed,
    hardcoded value — a shared static secret would let anyone forge signed
    session cookies (including role=ADMIN / is_master_admin=True) for every
    deployment that forgot to configure .env.

    If SECRET_KEY is missing, a random key is generated for this process only.
    This keeps the app usable for a quick local test, but all existing
    sessions will be invalidated on every restart until a permanent
    SECRET_KEY is set in .env — the warning below explains why.
    """
    key = os.getenv("SECRET_KEY", "").strip()
    if key:
        return key

    generated = secrets.token_hex(32)
    print("=" * 78)
    print("⚠️  CẢNH BÁO BẢO MẬT: Chưa cấu hình SECRET_KEY trong file .env!")
    print("    Hệ thống đã tự sinh một khóa NGẪU NHIÊN chỉ dùng cho phiên chạy này.")
    print("    -> Mọi session đăng nhập sẽ bị hủy khi restart server.")
    print("    -> Vui lòng thêm dòng sau vào file .env và khởi động lại:")
    print(f"       SECRET_KEY={generated}")
    print("=" * 78)
    return generated


class Config:
    SECRET_KEY = _resolve_secret_key()
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///qlcv.db")
    PORT = int(os.getenv("PORT", 8000))
    HOST = os.getenv("HOST", "0.0.0.0")
    # Set APP_ENV=development in .env to enable uvicorn --reload and other dev conveniences.
    APP_ENV = os.getenv("APP_ENV", "production").strip().lower()
    
    # Google settings
    GOOGLE_SPREADSHEET_ID = os.getenv("GOOGLE_SPREADSHEET_ID", "")
    GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
    
    # Upload settings
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "static/uploads")
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)

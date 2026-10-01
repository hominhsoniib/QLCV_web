import os
import shutil
import uuid
import hashlib
from fastapi import UploadFile
from config import Config
from services.file_registry import FileRegistry, RegistryError

# Google API libraries
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False

class DriveService:
    @staticmethod
    def get_drive_service():
        """Initializes Google Drive API service using service account credentials."""
        if not GOOGLE_API_AVAILABLE:
            return None
            
        cred_path = Config.GOOGLE_APPLICATION_CREDENTIALS
        if not os.path.exists(cred_path):
            print(f"Google credentials file not found at '{cred_path}'. Drive service disabled.")
            return None
            
        try:
            scopes = ['https://www.googleapis.com/auth/drive']
            creds = service_account.Credentials.from_service_account_file(cred_path, scopes=scopes)
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            print("Failed to initialize Google Drive service:", e)
            return None

    @staticmethod
    def rename_drive_file(file_id: str, new_name: str) -> str:
        """Renames a file in Google Drive and returns its web view link.
        Replicates Apps Script's Task_renameFileByMaCV / Task_renameFileBaoCao.
        """
        service = DriveService.get_drive_service()
        if not service:
            # Fallback mock URL if API is disabled
            print(f"Drive API offline. Mock renaming file ID [{file_id}] to '{new_name}'")
            return f"https://drive.google.com/open?id={file_id}"
            
        try:
            file_metadata = {'name': new_name}
            updated_file = service.files().update(
                fileId=file_id,
                body=file_metadata,
                fields='name, webViewLink'
            ).execute()
            return updated_file.get('webViewLink')
        except Exception as e:
            print(f"Error renaming Google Drive file [{file_id}]:", e)
            return f"https://drive.google.com/open?id={file_id}"

    # Extensions explicitly blocked because they can be served back by the browser
    # as active content (stored-XSS) or executed on the server if ever misconfigured.
    _BLOCKED_EXTENSIONS = {
        ".html", ".htm", ".svg", ".js", ".mjs", ".php", ".phtml", ".exe", ".sh",
        ".bat", ".cmd", ".py", ".ps1", ".dll", ".jar", ".vbs", ".msi", ".com"
    }
    _MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB

    @staticmethod
    def upload_local_file(file: UploadFile, *, tenant_id: str, uploader_id: str) -> str:
        """Saves an uploaded file locally to static/uploads/ and returns its access URL.
        Rejects disallowed extensions and enforces a max file size.
        """
        registry=None
        file_id=None
        try:
            filename = file.filename or ""
            # Sanitize filename
            filename_clean = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (".", "_", "-")]).strip()
            if not filename_clean:
                print("Upload rejected: empty/invalid filename after sanitization.")
                return ""

            _, ext = os.path.splitext(filename_clean)
            if ext.lower() in DriveService._BLOCKED_EXTENSIONS:
                print(f"Upload rejected: disallowed file extension '{ext}'.")
                return ""

            registry=FileRegistry()
            registry.initialize_registry()
            # WRITING intent precedes physical creation; locator is server-owned.
            # Exclusive creation prevents overwrites even if a random ID repeats.
            for _ in range(8):
                filename_final = f"{uuid.uuid4().hex}{ext}"
                filepath = os.path.join(Config.UPLOAD_DIR, filename_final)
                if os.path.exists(filepath):
                    continue
                try:
                    if registry.get_storage_record(Config.UPLOAD_STORAGE_ROOT_ID,filename_final):
                        continue
                    file_id=registry.register_writing(tenant_id,uploader_id,Config.UPLOAD_STORAGE_ROOT_ID,
                        filename_final,filename_clean)
                    buffer = open(filepath, "xb")
                    break
                except FileExistsError:
                    registry.mark_revoked(file_id,tenant_id)
                    file_id=None
                    continue
            else:
                print("Upload rejected: could not allocate a unique filename.")
                return ""

            written = 0
            digest=hashlib.sha256()
            with buffer:
                while True:
                    chunk = file.file.read(1024 * 1024)
                    if not chunk:
                        break
                    written += len(chunk)
                    if written > DriveService._MAX_UPLOAD_BYTES:
                        buffer.close()
                        os.remove(filepath)
                        registry.mark_revoked(file_id,tenant_id)
                        print(f"Upload rejected: file exceeds {DriveService._MAX_UPLOAD_BYTES // (1024*1024)}MB limit.")
                        return ""
                    buffer.write(chunk)
                    digest.update(chunk)
                buffer.flush()
                os.fsync(buffer.fileno())

            registry.complete_unbound(file_id,tenant_id,written,digest.hexdigest())

            return f"/static/uploads/{filename_final}"
        except Exception as e:
            if registry and file_id:
                try:
                    registry.mark_revoked(file_id,tenant_id)
                except RegistryError:
                    pass  # WRITING remains unusable; no byte cleanup/auto-claim.
            print("Failed to register/write local upload.")
            return ""
            
    # Bridge functions to match Apps Script function names
    @staticmethod
    def task_rename_file_by_ma_cv(file_id: str, ma_cv: str) -> str:
        return DriveService.rename_drive_file(file_id, f"{ma_cv}_TaiLieuGiaoViec")
        
    @staticmethod
    def task_rename_file_bao_cao(file_id: str, ma_cv: str) -> str:
        return DriveService.rename_drive_file(file_id, f"BC_{ma_cv}_TaiLieuBaoCao")
        
    @staticmethod
    def task_rename_file_uy_quyen(file_id: str, ma_cv: str) -> str:
        return DriveService.rename_drive_file(file_id, f"UQ_{ma_cv}_TaiLieuUyQuyen")

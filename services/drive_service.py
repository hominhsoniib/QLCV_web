import os
import shutil
from fastapi import UploadFile
from config import Config

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

    @staticmethod
    def upload_local_file(file: UploadFile) -> str:
        """Saves an uploaded file locally to static/uploads/ and returns its access URL."""
        try:
            filename = file.filename
            # Sanitize filename
            filename_clean = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in (".", "_", "-")]).strip()
            
            # Append timestamp to prevent overwrite collisions
            import time
            timestamp = int(time.time())
            base, ext = os.path.splitext(filename_clean)
            filename_final = f"{base}_{timestamp}{ext}"
            
            filepath = os.path.join(Config.UPLOAD_DIR, filename_final)
            
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            return f"/static/uploads/{filename_final}"
        except Exception as e:
            print("Failed to upload local file:", e)
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

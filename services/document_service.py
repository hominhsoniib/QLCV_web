from sqlalchemy.orm import Session
from models.models import Document
import datetime

class DocumentService:
    @staticmethod
    def get_document_management_data(db: Session):
        """Retrieves all documents."""
        docs = db.query(Document).all()
        data = []
        for d in docs:
            data.append({
                "maTL": d.ma_tl,
                "tenTL": d.ten_tl,
                "loai": d.loai,
                "ngayCapNhat": d.ngay_cap_nhat or "",
                "linkFile": d.link_file or "",
                "phongBan": d.phong_ban or ""
            })
        return {"success": True, "data": data}

    @staticmethod
    def get_library_data(db: Session):
        """Retrieves documents for read-only library repository."""
        return DocumentService.get_document_management_data(db)

    @staticmethod
    def get_next_doc_code(db: Session, loai: str):
        """Generates next document code based on document type (loai).
        Mapping types to prefixes (e.g. Biểu mẫu -> BM, Quy trình -> QT).
        """
        loai_clean = str(loai or "").strip().lower()
        prefix_map = {
            "biểu mẫu": "BM",
            "bieu mau": "BM",
            "quy trình": "QT",
            "quy trinh": "QT",
            "hợp đồng": "HD",
            "hop dong": "HD",
            "hướng dẫn": "HD",
            "huong dan": "HD",
            "mô tả công việc": "MC",
            "mo ta cong viec": "MC",
            "quy chế": "QC",
            "quy che": "QC",
            "quyết định": "QD",
            "quyet dinh": "QD"
        }
        
        prefix = prefix_map.get(loai_clean, "TL")
        
        # Get all documents starting with prefix
        docs = db.query(Document).filter(Document.ma_tl.like(f"{prefix}%")).all()
        if not docs:
            return f"{prefix}01"
            
        max_num = 0
        for d in docs:
            code = d.ma_tl or ""
            num_part = code.replace(prefix, "")
            try:
                num = int(num_part)
                if num > max_num:
                    max_num = num
            except ValueError:
                continue
                
        next_num = max_num + 1
        # Pad with 2 digits (e.g. BM03)
        return f"{prefix}{str(next_num).zfill(2)}"

    @staticmethod
    def add_document(db: Session, data: dict):
        """Inserts a new document into the database."""
        ma_tl = str(data.get("maTL", "")).strip()
        ten_tl = str(data.get("tenTL", "")).strip()
        loai = str(data.get("loai", "")).strip()
        link_file = str(data.get("linkFile", "")).strip()
        phong_ban = str(data.get("phongBan", "")).strip() or None
        
        if not ma_tl or not ten_tl:
            return "❌ Mã và Tên tài liệu không được trống!"
            
        # Check if code exists
        existing = db.query(Document).filter(Document.ma_tl == ma_tl).first()
        if existing:
            return f"❌ Mã tài liệu [{ma_tl}] đã tồn tại!"
            
        doc = Document(
            ma_tl=ma_tl,
            ten_tl=ten_tl,
            loai=loai,
            ngay_cap_nhat=datetime.date.today().strftime("%d/%m/%Y"),
            link_file=link_file,
            phong_ban=phong_ban
        )
        db.add(doc)
        db.commit()
        return f"✅ Thêm tài liệu [{ma_tl}] thành công!"

    @staticmethod
    def update_document(db: Session, data: dict):
        """Updates document details."""
        ma_tl = str(data.get("maTL", "")).strip()
        ten_tl = str(data.get("tenTL", "")).strip()
        loai = str(data.get("loai", "")).strip()
        link_file = str(data.get("linkFile", "")).strip()
        phong_ban = str(data.get("phongBan", "")).strip() or None
        
        doc = db.query(Document).filter(Document.ma_tl == ma_tl).first()
        if not doc:
            return f"❌ Không tìm thấy tài liệu mã {ma_tl}"
            
        doc.ten_tl = ten_tl
        doc.loai = loai
        doc.ngay_cap_nhat = datetime.date.today().strftime("%d/%m/%Y")
        doc.link_file = link_file
        doc.phong_ban = phong_ban
        
        db.commit()
        return f"✅ Cập nhật tài liệu [{ma_tl}] thành công!"

    @staticmethod
    def delete_document(db: Session, ma_tl: str):
        """Deletes a document from the database."""
        ma_tl_clean = str(ma_tl or "").strip()
        doc = db.query(Document).filter(Document.ma_tl == ma_tl_clean).first()
        if not doc:
            return f"❌ Không tìm thấy tài liệu mã {ma_tl_clean}"
            
        db.delete(doc)
        db.commit()
        return f"✅ Đã xóa tài liệu [{ma_tl_clean}] thành công!"

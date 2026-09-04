from sqlalchemy.orm import Session
from models.models import Department

class DepartmentService:
    @staticmethod
    def get_department_management_data(db: Session):
        """Retrieves all departments from the database."""
        depts = db.query(Department).all()
        data = [{
            "maBP": d.ma_bp, 
            "tenBP": d.ten_bp, 
            "khoi": d.khoi or "",
            "chucNhang": d.chuc_nang or "",
            "nhiemVu": d.nhiem_vu or "",
            "quyenHan": d.quyen_han or "",
            "kpiChinh": d.kpi_chinh or "",
            "kpiPhu": d.kpi_phu or ""
        } for d in depts]
        return {"success": True, "data": data}

    @staticmethod
    def add_department(db: Session, data: dict):
        """Creates a new organizational department."""
        ma_bp = str(data.get("maBP", "")).strip()
        ten_bp = str(data.get("tenBP", "")).strip()
        khoi = str(data.get("khoi", "")).strip()
        chuc_nang = str(data.get("chucNhang", "")).strip()
        nhiem_vu = str(data.get("nhiemVu", "")).strip()
        quyen_han = str(data.get("quyenHan", "")).strip()
        kpi_chinh = str(data.get("kpiChinh", "")).strip()
        kpi_phu = str(data.get("kpiPhu", "")).strip()
        
        if not ma_bp or not ten_bp:
            return {"success": False, "message": "❌ Mã và tên bộ phận không được trống!"}
            
        # Check if department code already exists
        existing = db.query(Department).filter(Department.ma_bp == ma_bp).first()
        if existing:
            return {"success": False, "message": f"❌ Mã bộ phận [{ma_bp}] đã tồn tại!"}
            
        dept = Department(
            ma_bp=ma_bp, ten_bp=ten_bp, khoi=khoi,
            chuc_nang=chuc_nang, nhiem_vu=nhiem_vu, quyen_han=quyen_han,
            kpi_chinh=kpi_chinh, kpi_phu=kpi_phu
        )
        db.add(dept)
        db.commit()
        return {"success": True, "message": f"✅ Thêm bộ phận [{ma_bp}] thành công!"}

    @staticmethod
    def update_department(db: Session, data: dict):
        """Updates department details."""
        ma_bp = str(data.get("maBP", "")).strip()
        ten_bp = str(data.get("tenBP", "")).strip()
        khoi = str(data.get("khoi", "")).strip()
        chuc_nang = str(data.get("chucNhang", "")).strip()
        nhiem_vu = str(data.get("nhiemVu", "")).strip()
        quyen_han = str(data.get("quyenHan", "")).strip()
        kpi_chinh = str(data.get("kpiChinh", "")).strip()
        kpi_phu = str(data.get("kpiPhu", "")).strip()
        
        dept = db.query(Department).filter(Department.ma_bp == ma_bp).first()
        if not dept:
            return {"success": False, "message": f"❌ Không tìm thấy bộ phận mã {ma_bp}"}
            
        dept.ten_bp = ten_bp
        dept.khoi = khoi
        dept.chuc_nang = chuc_nang
        dept.nhiem_vu = nhiem_vu
        dept.quyen_han = quyen_han
        dept.kpi_chinh = kpi_chinh
        dept.kpi_phu = kpi_phu
        db.commit()
        return {"success": True, "message": f"✅ Đã cập nhật thông tin bộ phận [{ma_bp}]"}

    @staticmethod
    def delete_department(db: Session, ma_bp: str):
        """Deletes a department from the database."""
        ma_bp_clean = str(ma_bp or "").strip()
        dept = db.query(Department).filter(Department.ma_bp == ma_bp_clean).first()
        if not dept:
            return {"success": False, "message": f"❌ Không tìm thấy bộ phận mã {ma_bp_clean}"}
            
        db.delete(dept)
        db.commit()
        return {"success": True, "message": f"✅ Đã xóa bộ phận [{ma_bp_clean}] thành công!"}

from sqlalchemy.orm import Session
from models.models import Employee

def sync_global_user(email: str, ma_nv: str, company_mst: str = "0312345678", old_email: str = None):
    """Syncs user email to Master System Global User Index for email authentication."""
    clean_email = str(email or "").strip().lower()
    clean_ma_nv = str(ma_nv or "").strip().upper()
    clean_mst = str(company_mst or "0312345678").strip()
    old_clean = str(old_email or "").strip().lower()

    try:
        from database.multi_tenant import MasterSessionLocal
        from models.master_models import GlobalUserIndex
        master_db = MasterSessionLocal()
        try:
            if old_clean and old_clean != clean_email:
                master_db.query(GlobalUserIndex).filter_by(email=old_clean).delete()

            if clean_email and clean_ma_nv:
                user_idx = master_db.query(GlobalUserIndex).filter_by(email=clean_email).first()
                if user_idx:
                    user_idx.ma_nv = clean_ma_nv
                    user_idx.tax_code = clean_mst
                else:
                    new_idx = GlobalUserIndex(email=clean_email, tax_code=clean_mst, ma_nv=clean_ma_nv)
                    master_db.add(new_idx)
            master_db.commit()
        finally:
            master_db.close()
    except Exception as e:
        print("[GLOBAL USER SYNC WARN]:", e)

class EmployeeService:
    @staticmethod
    def get_employee_management_data(db: Session):
        """Retrieves employee data with passwords masked for security."""
        employees = db.query(Employee).all()
        safe_data = []
        for e in employees:
            safe_data.append({
                "maNV": e.ma_nv,
                "tenNV": e.ten_nv,
                "email": e.email or "",
                "matKhau": "********",  # Masked password
                "quyen": e.quyen,
                "chucDanh": e.chuc_danh or "",
                "chucVu": e.chuc_vu or "",
                "phongBan": e.phong_ban or "",
                "nguoiQL": e.nguoi_ql or ""
            })
        return {"success": True, "data": safe_data}

    @staticmethod
    def add_employee(db: Session, data: dict, company_mst: str = "0312345678"):
        """Creates a new employee account in the database and registers in Global User Index."""
        ma_nv = str(data.get("maNV", "")).strip().upper()
        ten_nv = str(data.get("tenNV", "")).strip()
        email_val = str(data.get("email", "")).strip().lower()
        clean_mst = str(company_mst or "0312345678").strip()
        
        if not ma_nv or not ten_nv:
            return "❌ Mã nhân viên và tên nhân viên không được trống!"
            
        # Check duplicate ma_nv
        existing = db.query(Employee).filter(Employee.ma_nv == ma_nv).first()
        if existing:
            return f"❌ Mã nhân viên [{ma_nv}] đã tồn tại!"
            
        # Check duplicate email if provided
        if email_val:
            existing_email = db.query(Employee).filter(Employee.email == email_val).first()
            if existing_email:
                return f"❌ Email [{email_val}] đã được sử dụng bởi nhân sự khác [{existing_email.ma_nv}]!"
            
        password = str(data.get("matKhau", "")).strip()
        if not password or password == "********":
            password = "123456" # Default password — user should be prompted to change on first login

        from services.security_utils import hash_password
        emp = Employee(
            ma_nv=ma_nv,
            ten_nv=ten_nv,
            email=email_val if email_val else None,
            mat_khau=hash_password(password),
            quyen=str(data.get("quyen", "USER")).strip().upper(),
            chuc_danh=str(data.get("chucDanh", "")).strip(),
            chuc_vu=str(data.get("chucVu", "")).strip(),
            phong_ban=str(data.get("phongBan", "")).strip(),
            nguoi_ql=str(data.get("nguoiQL", "")).strip()
        )
        db.add(emp)
        db.commit()
        
        if email_val:
            sync_global_user(email_val, ma_nv, clean_mst)
            
        return f"✅ Thêm nhân sự [{ma_nv}] ({ten_nv}) thành công!"

    @staticmethod
    def update_employee(db: Session, data: dict, company_mst: str = "0312345678"):
        """Updates employee profile info and syncs Email in Global User Index."""
        ma_nv = str(data.get("maNV", "")).strip().upper()
        email_val = str(data.get("email", "")).strip().lower()
        clean_mst = str(company_mst or "0312345678").strip()
        
        emp = db.query(Employee).filter(Employee.ma_nv == ma_nv).first()
        if not emp:
            return f"❌ Không tìm thấy nhân sự mã {ma_nv}"
            
        old_email = str(emp.email or "").strip().lower()
        
        # Check duplicate email if changed
        if email_val and email_val != old_email:
            dup = db.query(Employee).filter(Employee.email == email_val, Employee.ma_nv != ma_nv).first()
            if dup:
                return f"❌ Email [{email_val}] đã trùng với tài khoản [{dup.ma_nv}]!"
            
        password = str(data.get("matKhau", "")).strip()
        if not password or password == "********":
            new_mat_khau = emp.mat_khau # Keep current (already-hashed) password
        else:
            from services.security_utils import hash_password
            new_mat_khau = hash_password(password)

        emp.ten_nv = str(data.get("tenNV", emp.ten_nv)).strip()
        emp.email = email_val if email_val else None
        emp.mat_khau = new_mat_khau
        emp.quyen = str(data.get("quyen", emp.quyen)).strip().upper()
        emp.chuc_danh = str(data.get("chucDanh", "")).strip()
        emp.chuc_vu = str(data.get("chucVu", "")).strip()
        emp.phong_ban = str(data.get("phongBan", "")).strip()
        emp.nguoi_ql = str(data.get("nguoiQL", "")).strip()
        
        db.commit()
        
        sync_global_user(email_val, ma_nv, clean_mst, old_email=old_email)
            
        return f"✅ Đã cập nhật thông tin nhân sự [{ma_nv}] thành công!"

    @staticmethod
    def get_employees_for_dropdown(db: Session):
        """Returns employee list for populate select elements."""
        employees = db.query(Employee).all()
        return [{
            "maNV": e.ma_nv,
            "tenNV": e.ten_nv,
            "email": e.email or "",
            "phong": e.phong_ban or ""
        } for e in employees]

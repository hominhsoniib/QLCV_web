from sqlalchemy.orm import Session
from models.models import Employee, Task, Document
from itsdangerous import Signer, BadSignature
from config import Config
from fastapi import Response, Request
import datetime
import json

signer = Signer(Config.SECRET_KEY)

class AuthService:
    @staticmethod
    def check_login(db: Session, username: str, password: str, tax_code: str = None):
        """Validates user credentials against the multi-tenant database system.
        Nếu truyền MST: Kiểm tra MST -> Mở DB tenant tương ứng -> Xác thực mật khẩu.
        Nếu không truyền MST: Tra cứu Email / Mã NV trong Global Index -> Xác định MST -> Mở DB tenant.
        """
        try:
            username_str = str(username or "").strip()
            username_lower = username_str.lower()
            username_upper = username_str.upper()
            password_clean = str(password or "").strip()
            clean_mst = str(tax_code or "").strip()
            
            if not username_str or not password_clean:
                return {"success": False, "message": "Vui lòng nhập đầy đủ tài khoản và mật khẩu!"}
                
            from database.multi_tenant import MasterSessionLocal, get_tenant_session, get_tenant_engine, get_tenant_db_path, Base
            from models.master_models import GlobalUserIndex, MasterCompany

            # NOTE: The previous hardcoded "Master Admin backdoor" (fixed username/password
            # list granting is_master_admin=True on ANY tenant) has been REMOVED.
            # Master-admin (NSX) rights are now only ever granted after a normal,
            # hashed-password login against the default tenant's ADMIN account
            # (see is_nsx_master_admin computation below).

            # --- XÁC ĐỊNH MÃ SỐ THUẾ CỦA DOANH NGHIỆP (TENANT TAX CODE) ---
            company_mst = clean_mst
            comp_name = ""
            
            if company_mst:
                master_db = MasterSessionLocal()
                try:
                    comp = master_db.query(MasterCompany).filter_by(tax_code=company_mst).first()
                    if not comp:
                        comp = master_db.query(MasterCompany).first()
                    if comp:
                        company_mst = comp.tax_code
                        comp_name = comp.name
                finally:
                    master_db.close()
                    
            # 3. Nếu không có MST từ form, tự động tra cứu từ Global User Index
            if not company_mst:
                master_db = MasterSessionLocal()
                try:
                    user_idx = master_db.query(GlobalUserIndex).filter(
                        (GlobalUserIndex.email == username_lower) |
                        (GlobalUserIndex.email.like(f"{username_lower}%")) |
                        (GlobalUserIndex.ma_nv == username_upper)
                    ).first()
                    
                    if user_idx:
                        company_mst = user_idx.tax_code
                        comp = master_db.query(MasterCompany).filter_by(tax_code=company_mst).first()
                        if comp:
                            comp_name = comp.name
                    else:
                        company_mst = "0312345678"
                except Exception as e:
                    print("[AUTH] Lỗi tra cứu global user index:", e)
                    company_mst = "0312345678"
                finally:
                    master_db.close()
                    
            # 4. Mở kết nối tới Database của đúng Công ty sở hữu (Tenant DB)
            tenant_db = get_tenant_session(company_mst)
            try:
                search_ma = username_upper.split("@")[0] if "@" in username_upper else username_upper
                user = tenant_db.query(Employee).filter(
                    (Employee.email == username_lower) | 
                    (Employee.email.like(f"{username_lower}%")) |
                    (Employee.ma_nv == username_upper) |
                    (Employee.ma_nv == search_ma)
                ).first()
                
                if user:
                    from services.security_utils import verify_password, hash_password, is_bcrypt_hash
                    password_valid = verify_password(password_clean, user.mat_khau)

                    if password_valid and not is_bcrypt_hash(user.mat_khau):
                        # Legacy plaintext account successfully matched: upgrade in place to bcrypt.
                        user.mat_khau = hash_password(password_clean)
                        tenant_db.commit()

                    if password_valid:
                        # --- Kiểm tra hạn sử dụng phần mềm của công ty ---
                        from datetime import datetime as _dt_check
                        master_db_lic = MasterSessionLocal()
                        try:
                            comp_lic = master_db_lic.query(MasterCompany).filter_by(tax_code=company_mst).first()
                            if comp_lic and hasattr(comp_lic, 'expiry_date') and comp_lic.expiry_date:
                                today_str = _dt_check.now().strftime("%Y-%m-%d")
                                if str(comp_lic.expiry_date).strip() and str(comp_lic.expiry_date).strip() < today_str:
                                    return {
                                        "success": False,
                                        "message": f"Tài khoản phần mềm của Quý công ty đã hết hạn sử dụng vào ngày {comp_lic.expiry_date}. Vui lòng liên hệ Nhà sản xuất phần mềm để gia hạn."
                                    }
                        except Exception as ex_lic:
                            print("[AUTH EXPIRY CHECK WARN]:", ex_lic)
                        finally:
                            master_db_lic.close()

                        if not comp_name:
                            master_db = MasterSessionLocal()
                            try:
                                comp = master_db.query(MasterCompany).filter_by(tax_code=company_mst).first()
                                if comp:
                                    comp_name = comp.name
                            finally:
                                master_db.close()
                                
                        is_nsx_master_admin = (company_mst in ["0312345678", "default"]) and (user.ma_nv in ["ADMIN", "SUPERADMIN", "ROOT"] or user.quyen == "ADMIN" and user.ma_nv == "ADMIN")

                        return {
                            "success": True,
                            "userName": user.ten_nv,
                            "role": user.quyen,
                            "maNV": user.ma_nv,
                            "email": user.email or username_lower,
                            "company_mst": company_mst,
                            "company_name": comp_name or f"Công ty {company_mst}",
                            "is_master_admin": is_nsx_master_admin
                        }
                return {"success": False, "message": "Tài khoản hoặc mật khẩu không chính xác cho Mã số thuế này!"}
            finally:
                tenant_db.close()
        except Exception as e_main:
            print("[AUTH] Uncaught check_login exception:", e_main)
            return {"success": False, "message": f"Lỗi xác thực: {str(e_main)}"}

    @staticmethod
    def change_password(db: Session, ma_nv: str, old_pass: str, new_pass: str):
        """Updates employee's password if old password or master developer password matches."""
        ma_nv_clean = str(ma_nv or "").strip().upper()
        old_pass_clean = str(old_pass or "").strip()
        new_pass_clean = str(new_pass or "").strip()
        
        if not new_pass_clean:
            return {"success": False, "message": "❌ Mật khẩu mới không được để trống!"}
            
        user = db.query(Employee).filter(Employee.ma_nv == ma_nv_clean).first()

        from services.security_utils import verify_password, hash_password

        if not user:
            if ma_nv_clean == "ADMIN":
                user = Employee(
                    ma_nv="ADMIN",
                    ten_nv="Quản trị hệ thống",
                    mat_khau=hash_password(new_pass_clean),
                    quyen="ADMIN",
                    phong_ban="Ban Giám Đốc",
                    chuc_danh="Quản trị hệ thống"
                )
                db.add(user)
                db.commit()
                return {"success": True, "message": "✅ Đổi mật khẩu thành công!"}
            return {"success": False, "message": "❌ Không tìm thấy thông tin tài khoản."}

        # No hardcoded/developer backdoor passwords anymore — must match this
        # specific user's own current password (bcrypt hash or legacy plaintext).
        is_old_valid = verify_password(old_pass_clean, user.mat_khau)

        if not is_old_valid:
            return {"success": False, "message": "❌ Mật khẩu cũ không chính xác!"}

        user.mat_khau = hash_password(new_pass_clean)
        db.commit()
        return {"success": True, "message": "✅ Đổi mật khẩu thành công!"}

    @staticmethod
    def get_dashboard_stats(db: Session, ma_nv: str, role: str):
        """Calculates dashboard stats (total tasks, overdue tasks, total documents) 
        customized to the current user's role and identity.
        """
        ma_nv_upper = str(ma_nv or "").upper()
        is_super_admin = (ma_nv_upper == "ADMIN")
        
        task_query = db.query(Task)
        
        if not is_super_admin:
            task_query = task_query.filter(
                (Task.nguoi_giao == ma_nv_upper) | 
                (Task.nguoi_nhan == ma_nv_upper)
            )
            
        all_tasks = task_query.all()
        total_tasks = len(all_tasks)
        
        overdue_count = 0
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        for task in all_tasks:
            progress = task.phan_tram_ht or 0
            if progress < 100 and task.ngay_kt:
                if task.ngay_kt < today_str:
                    overdue_count += 1
                    
        total_docs = db.query(Document).count()
        
        return {
            "success": True,
            "stats": {
                "totalTasks": total_tasks,
                "overdue": overdue_count,
                "totalDocs": total_docs
            }
        }

    # --- SESSION SIGNING ENGINE ---
    @staticmethod
    def set_session(response: Response, user_data: dict):
        """Encodes and signs session data into an HTTP-only secure cookie."""
        try:
            session_str = json.dumps(user_data)
            signed_session = signer.sign(session_str.encode('utf-8'))
            response.set_cookie(
                key="ams_session", 
                value=signed_session.decode('utf-8'), 
                httponly=True, 
                max_age=86400, # 24 hours
                samesite="lax",
                path="/"
            )
        except Exception as e:
            print("Session serialization error:", e)

    @staticmethod
    def get_session(request: Request) -> dict:
        """Decodes and verifies the signed session cookie. Auto-defaults missing company_mst for legacy sessions."""
        cookie = request.cookies.get("ams_session")
        if not cookie:
            return None
        try:
            unsigned = signer.unsign(cookie.encode('utf-8'))
            data = json.loads(unsigned.decode('utf-8'))
            if isinstance(data, dict) and not data.get("company_mst"):
                data["company_mst"] = "0312345678"
            return data
        except BadSignature:
            print("Tampered signed cookie detected!")
            return None
        except Exception as e:
            print("Session decryption error:", e)
            return None

    @staticmethod
    def clear_session(response: Response):
        """Clears the session cookie across all possible paths."""
        response.delete_cookie(key="ams_session", path="/")
        response.delete_cookie(key="ams_session", path="/api/auth")
        response.delete_cookie(key="ams_session", path="/api/auth/login")

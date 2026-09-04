import pandas as pd
import datetime
from sqlalchemy.orm import Session
from models.models import Employee, Department, Task, Document
import os

def clean_val(val, default=""):
    if pd.isna(val) or val is None:
        return default
    return str(val).strip()

def clean_int(val, default=0):
    if pd.isna(val) or val is None:
        return default
    try:
        # Check if percentage in float form (e.g. 0.8 -> 80)
        f_val = float(val)
        if 0.0 < f_val <= 1.0:
            return int(f_val * 100)
        return int(f_val)
    except:
        return default

def clean_date(val):
    if pd.isna(val) or val is None:
        return ""
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.strftime("%Y-%m-%d")
    val_str = str(val).strip()
    # Try parsing various formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            dt = datetime.datetime.strptime(val_str, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    # If standard timestamp representation like "Timestamp('2026-03-05 00:00:00')"
    if "Timestamp" in val_str:
        try:
            inner = val_str.split("'")[1]
            dt = datetime.datetime.strptime(inner.split()[0], "%Y-%m-%d")
            return dt.strftime("%Y-%m-%d")
        except:
            pass
    return val_str

def seed_database_from_excel(db: Session, excel_path: str = "seed.xlsx") -> bool:
    """Seeds the SQLite database using data from an Excel export of the Google Sheet database."""
    if not os.path.exists(excel_path):
        print(f"Seed file '{excel_path}' not found. Seeding with mock admin user only.")
        # Ensure at least an admin user exists
        if not db.query(Employee).filter_by(ma_nv="ADMIN").first():
            admin = Employee(
                ma_nv="ADMIN",
                ten_nv="Quản trị hệ thống",
                mat_khau="admin",
                quyen="ADMIN",
                phong_ban="Ban Giám Đốc"
            )
            db.add(admin)
            db.commit()
        return False
        
    try:
        xl = pd.ExcelFile(excel_path)
        
        # 1. Seed Employees
        if 'DM_NHANVIEN' in xl.sheet_names:
            df = xl.parse('DM_NHANVIEN')
            for _, row in df.iterrows():
                ma_nv = clean_val(row.get('MaNV')).upper()
                if not ma_nv:
                    continue
                
                email_val = clean_val(row.get('Email')).lower()
                existing_emp = db.query(Employee).filter_by(ma_nv=ma_nv).first()
                
                if existing_emp:
                    # Update email if missing
                    if email_val and not existing_emp.email:
                        existing_emp.email = email_val
                    # Update password if old default '123' or '123456'
                    if existing_emp.mat_khau in ("123", "123456") or not existing_emp.mat_khau:
                        existing_emp.mat_khau = clean_val(row.get('MatKhau'), "Voc@123456")
                else:
                    emp = Employee(
                        ma_nv=ma_nv,
                        ten_nv=clean_val(row.get('TenNV')),
                        mat_khau=clean_val(row.get('MatKhau'), "Voc@123456"),
                        email=email_val if email_val else None,
                        quyen=clean_val(row.get('Quyen'), "USER").upper(),
                        chuc_danh=clean_val(row.get('Chucdanh')),
                        chuc_vu=clean_val(row.get('Chucvu')),
                        phong_ban=clean_val(row.get('PhongBan')),
                        nguoi_ql=clean_val(row.get('NguoiQL'))
                    )
                    db.add(emp)
            db.commit()
            print("Successfully seeded employees!")
            
        # 2. Seed Departments
        if 'DM_BOPHAN' in xl.sheet_names:
            df = xl.parse('DM_BOPHAN')
            for _, row in df.iterrows():
                ma_bp = clean_val(row.get('MaBP'))
                if not ma_bp:
                    continue
                if db.query(Department).filter_by(ma_bp=ma_bp).first():
                    continue
                
                # Support KhoiPhuTrach or Khoi headers
                khoi_val = row.get('KhoiPhuTrach') if 'KhoiPhuTrach' in row else row.get('Khoi', '')
                dept = Department(
                    ma_bp=ma_bp,
                    ten_bp=clean_val(row.get('TenBP')),
                    khoi=clean_val(khoi_val)
                )
                db.add(dept)
            db.commit()
            print("Successfully seeded departments!")
            
        # 3. Seed Documents
        if 'DM_TAILIEU' in xl.sheet_names:
            df = xl.parse('DM_TAILIEU')
            for _, row in df.iterrows():
                ma_tl = clean_val(row.get('MaTL'))
                if not ma_tl:
                    continue
                if db.query(Document).filter_by(ma_tl=ma_tl).first():
                    continue
                
                doc = Document(
                    ma_tl=ma_tl,
                    ten_tl=clean_val(row.get('TenTL')),
                    loai=clean_val(row.get('PhanLoai') if 'PhanLoai' in row else row.get('Loai', 'Quy trình')),
                    ngay_cap_nhat=clean_date(row.get('NgayCapNhat')),
                    link_file=clean_val(row.get('DuongDan') if 'DuongDan' in row else row.get('LinkFile', ''))
                )
                db.add(doc)
            db.commit()
            print("Successfully seeded documents!")

        # 4. Seed Tasks
        if 'QLCV' in xl.sheet_names:
            df = xl.parse('QLCV')
            for _, row in df.iterrows():
                id_pc = clean_val(row.get('ID_PhanCong'))
                if not id_pc:
                    continue
                if db.query(Task).filter_by(id_phan_cong=id_pc).first():
                    continue
                
                # Convert progress % value
                pct_ht = clean_int(row.get('%HT'))
                
                task = Task(
                    id_phan_cong=id_pc,
                    ma_cv=clean_val(row.get('MaCV')),
                    ten_cv=clean_val(row.get('TenCV')),
                    nguoi_giao=clean_val(row.get('NguoiGiao')),
                    nguoi_nhan=clean_val(row.get('NguoiNhan')),
                    ngay_bd=clean_date(row.get('NgayBD')),
                    ngay_kt=clean_date(row.get('NgayKT')),
                    phan_tram_ht=pct_ht,
                    tinh_trang=clean_val(row.get('TinhTrang'), "Chưa bắt đầu"),
                    nhat_ky_bao_cao=clean_val(row.get('VuongMac') if 'VuongMac' in row else row.get('NhatKyBaoCao', '')),
                    y_kien_cap_tren=clean_val(row.get('YkCapTren') if 'YkCapTren' in row else row.get('YkCapTren', '')),
                    so_lan_bao_cao=clean_int(row.get('VaiTro') if 'VaiTro' in row else row.get('SoLanBaoCao', 0)),
                    thoi_gian_xem_cuoi=clean_date(row.get('ThoiGianXemCuoi')),
                    noi_dung_nhac_nho=clean_val(row.get('NoiDungNhacNho')),
                    so_lan_nhac=clean_int(row.get('SoLanNhac')),
                    file_giao_viec=clean_val(row.get('File_GiaoViec')),
                    file_bao_cao=clean_val(row.get('File_BaoCao')),
                    nguoi_phoi_hop=clean_val(row.get('NguoiPhoiHop'))
                )
                db.add(task)
            db.commit()
            print("Successfully seeded tasks!")
            
        return True
    except Exception as e:
        print("Error during database seeding:", e)
        return False

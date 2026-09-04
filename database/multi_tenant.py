import os
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Request
from models.master_models import MasterBase, MasterCompany, GlobalUserIndex
from models.models import Base, Employee
from config import Config

# Master System DB path
MASTER_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
os.makedirs(MASTER_DB_DIR, exist_ok=True)
MASTER_DB_PATH = os.path.join(MASTER_DB_DIR, "master_system.db")

TENANTS_DIR = os.path.join(MASTER_DB_DIR, "tenants")
os.makedirs(TENANTS_DIR, exist_ok=True)

# Master Engine & SessionMaker
master_engine = create_engine(f"sqlite:///{MASTER_DB_PATH}", connect_args={"check_same_thread": False})
MasterSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=master_engine)

# Cache for tenant SQLAlchemy engines: {tax_code: engine}
_tenant_engines = {}

def get_master_db():
    """Dependency to get a Master DB session"""
    db = MasterSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tenant_db_path(tax_code: str) -> str:
    """Returns absolute path to tenant SQLite database file and ensures directory exists."""
    clean_mst = str(tax_code or "").strip()
    if clean_mst in ["0312345678", "default", ""]:
        return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "qlcv.db"))
    
    p = os.path.abspath(os.path.join(TENANTS_DIR, f"{clean_mst}.db"))
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
    except Exception:
        pass
    return p

def get_tenant_engine(tax_code: str):
    """Retrieves or creates a cached SQLAlchemy engine for a given tenant tax_code."""
    tax_code_clean = str(tax_code or "0312345678").strip()
    if not tax_code_clean:
        tax_code_clean = "0312345678"
        
    if tax_code_clean in _tenant_engines:
        return _tenant_engines[tax_code_clean]
    
    db_path = get_tenant_db_path(tax_code_clean)
    db_url = f"sqlite:///{db_path}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    _tenant_engines[tax_code_clean] = engine
    return engine

def get_tenant_session(tax_code: str) -> Session:
    """Creates a new DB session for the specified tenant tax_code."""
    engine = get_tenant_engine(tax_code)
    TenantSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return TenantSessionLocal()

def init_master_and_default_tenant():
    """Initializes Master DB tables and auto-registers existing default company & employees."""
    # 1. Create master system tables
    MasterBase.metadata.create_all(bind=master_engine)
    
    db: Session = MasterSessionLocal()
    try:
        # Schema migration check for master_companies table columns
        try:
            cursor = db.execute(text("PRAGMA table_info(master_companies)"))
            cols = [row[1] for row in cursor.fetchall()]
            for col in ['code', 'short_name', 'legal_rep', 'website', 'business_field']:
                if col not in cols:
                    db.execute(text(f"ALTER TABLE master_companies ADD COLUMN {col} TEXT DEFAULT ''"))
            db.commit()
        except Exception as e:
            print("[MULTI-TENANT] Master migration warning:", e)

        # 2. Check if default company exists
        default_mst = "0312345678"
        default_comp = db.query(MasterCompany).filter_by(tax_code=default_mst).first()
        if not default_comp:
            default_path = get_tenant_db_path(default_mst)
            default_comp = MasterCompany(
                tax_code=default_mst,
                code="DEFAULT",
                name="CÔNG TY TNHH GIẢI PHÁP CÔNG NGHIỆP VIỆT",
                short_name="VIET INDUS",
                legal_rep="Nguyễn Văn Quản Trị",
                address="123 Đường Công Nghiệp, Q. Bình Tân, TP.HCM",
                phone="(028) 3838 3838",
                email="sales@congty.vn",
                website="https://congty.vn",
                business_field="Giải pháp công nghiệp & Công nghệ",
                db_path=default_path,
                status="ACTIVE"
            )
            db.add(default_comp)
            db.commit()
            print(f"[MULTI-TENANT] Registered default company: {default_comp.name} ({default_mst})")
            
        # 3. Sync all employees across all registered tenants into GlobalUserIndex
        all_companies = db.query(MasterCompany).all()
        for comp in all_companies:
            comp_mst = comp.tax_code
            try:
                t_engine = get_tenant_engine(comp_mst)
                Base.metadata.create_all(bind=t_engine)
                
                t_db = get_tenant_session(comp_mst)
                try:
                    employees = t_db.query(Employee).all()
                    for emp in employees:
                        email = str(emp.email or "").strip().lower()
                        ma_nv = str(emp.ma_nv or "").strip().upper()
                        
                        if not email and ma_nv:
                            # Generate default domain email if empty
                            email = f"{ma_nv.lower()}@{comp_mst}.com"
                            emp.email = email
                            t_db.commit()
                            
                        if email and ma_nv:
                            existing_user = db.query(GlobalUserIndex).filter_by(email=email).first()
                            if not existing_user:
                                global_user = GlobalUserIndex(
                                    email=email,
                                    tax_code=comp_mst,
                                    ma_nv=ma_nv
                                )
                                db.add(global_user)
                            else:
                                existing_user.tax_code = comp_mst
                                existing_user.ma_nv = ma_nv
                    db.commit()
                finally:
                    t_db.close()
            except Exception as ex:
                print(f"[MULTI-TENANT] Warning syncing employees for {comp_mst}: {ex}")
                
        print("[MULTI-TENANT] Synchronized all tenant employees to Global User Index!")
    finally:
        db.close()

def create_company_tenant(
    tax_code: str, 
    name: str, 
    code: str = "",
    short_name: str = "",
    legal_rep: str = "",
    address: str = "", 
    phone: str = "", 
    email: str = "", 
    website: str = "",
    business_field: str = "",
    admin_email: str = "", 
    admin_pass: str = "Admin@123"
):
    """Creates a new Company Tenant database, runs schema migrations, creates default admin, and updates master index."""
    clean_mst = str(tax_code or "").strip()
    if not clean_mst:
        raise ValueError("Mã số thuế không được để trống!")
        
    master_db: Session = MasterSessionLocal()
    try:
        if master_db.query(MasterCompany).filter_by(tax_code=clean_mst).first():
            raise ValueError(f"Mã số thuế '{clean_mst}' đã tồn tại trong hệ thống!")
            
        clean_admin_email = str(admin_email or f"admin@{clean_mst}.com").strip().lower()
        if master_db.query(GlobalUserIndex).filter_by(email=clean_admin_email).first():
            raise ValueError(f"Email admin '{clean_admin_email}' đã được đăng ký ở công ty khác!")
            
        db_path = get_tenant_db_path(clean_mst)
        
        # 1. Initialize Tenant Database Engine & Tables
        engine = get_tenant_engine(clean_mst)
        Base.metadata.create_all(bind=engine)
        
        # 2. Create Default Admin user in Tenant DB
        tenant_db = get_tenant_session(clean_mst)
        try:
            admin_emp = Employee(
                ma_nv="ADMIN",
                ten_nv=f"Quản trị viên ({name})",
                mat_khau=admin_pass,
                email=clean_admin_email,
                quyen="ADMIN",
                phong_ban="Ban Giám Đốc",
                chuc_danh="Quản trị hệ thống",
                chuc_vu="Admin"
            )
            tenant_db.add(admin_emp)
            tenant_db.commit()
        finally:
            tenant_db.close()
            
        # 3. Save Company to Master Database
        company = MasterCompany(
            tax_code=clean_mst,
            code=code or f"CTY-{clean_mst[:4]}",
            name=name,
            short_name=short_name,
            legal_rep=legal_rep,
            address=address,
            phone=phone,
            email=email,
            website=website,
            business_field=business_field,
            db_path=db_path,
            status="ACTIVE"
        )
        master_db.add(company)
        
        # 4. Save Global User Index
        user_index = GlobalUserIndex(
            email=clean_admin_email,
            tax_code=clean_mst,
            ma_nv="ADMIN"
        )
        master_db.add(user_index)
        master_db.commit()
        
        return {
            "success": True,
            "tax_code": clean_mst,
            "name": name,
            "admin_email": clean_admin_email,
            "db_path": db_path
        }
    except Exception as e:
        master_db.rollback()
        raise e
    finally:
        master_db.close()

def delete_company_tenant(tax_code: str):
    """Deletes a company tenant, all associated global user index entries, and removes its SQLite DB file."""
    clean_mst = str(tax_code or "").strip()
    if not clean_mst:
        raise ValueError("Mã số thuế không được để trống!")
        
    if clean_mst in ["0312345678", "default"]:
        raise ValueError("Không được phép xóa công ty mặc định của Nhà Sản Xuất!")
        
    master_db: Session = MasterSessionLocal()
    try:
        comp = master_db.query(MasterCompany).filter_by(tax_code=clean_mst).first()
        if not comp:
            raise ValueError(f"Không tìm thấy công ty với Mã số thuế '{clean_mst}'!")
            
        comp_name = comp.name
        
        # 1. Dispose cached engine if any
        if clean_mst in _tenant_engines:
            try:
                _tenant_engines[clean_mst].dispose()
                del _tenant_engines[clean_mst]
            except Exception as e:
                print(f"[MULTI-TENANT] Warning disposing engine for {clean_mst}: {e}")
                
        # 2. Delete all Global User Index entries for this tenant
        master_db.query(GlobalUserIndex).filter_by(tax_code=clean_mst).delete()
        
        # 3. Delete Company from Master DB
        master_db.delete(comp)
        master_db.commit()
        
        # 4. Delete SQLite DB file if exists
        db_path = get_tenant_db_path(clean_mst)
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception as e:
                print(f"[MULTI-TENANT] Warning removing DB file {db_path}: {e}")
                
        return {
            "success": True,
            "message": f"✅ Đã xóa hoàn toàn công ty '{comp_name}' (MST: {clean_mst}) và toàn bộ cơ sở dữ liệu!"
        }
    except Exception as e:
        master_db.rollback()
        raise e
    finally:
        master_db.close()


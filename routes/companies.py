from fastapi import APIRouter, Depends, Request, Response, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from services.auth_service import AuthService
from database.multi_tenant import (
    MasterSessionLocal, 
    create_company_tenant, 
    delete_company_tenant,
    get_tenant_session,
    get_tenant_db_path,
    TENANTS_DIR
)
from models.master_models import MasterCompany, GlobalUserIndex
from models.models import Employee

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def check_master_system_admin(request: Request):
    """Enforces strict Master System Admin access rights.
    Chỉ Admin NSX (Nhà Sản Xuất - có cờ is_master_admin) mới có quyền truy cập.
    CEO hoặc Admin của công ty người sử dụng KHÔNG có quyền này.
    """
    session = AuthService.get_session(request)
    if not session:
        raise HTTPException(status_code=401, detail="Chưa đăng nhập hệ thống!")
        
    is_master = session.get("is_master_admin", False)
    if not is_master:
        raise HTTPException(status_code=403, detail="Chỉ Admin NSX (Nhà Sản Xuất) mới có quyền quản trị công ty & database!")
        
    return session

@router.get("/master/companies", response_class=HTMLResponse)
def get_companies_page(request: Request):
    """Renders Multi-Tenant Company & Database Management UI (Master Super Admin NSX Only)."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
        
    if not session.get("is_master_admin", False):
        return RedirectResponse(url="/dashboard")
        
    return templates.TemplateResponse(request, "master/companies.html", {
        "user": session
    })

@router.get("/api/companies/list")
def api_list_companies(request: Request):
    """Returns detailed list of registered companies, file sizes, and employee counts."""
    check_master_system_admin(request)
    
    master_db: Session = MasterSessionLocal()
    try:
        companies = master_db.query(MasterCompany).all()
        result = []
        
        for comp in companies:
            db_file_path = get_tenant_db_path(comp.tax_code)
            file_size_kb = 0
            if os.path.exists(db_file_path):
                file_size_kb = round(os.path.getsize(db_file_path) / 1024, 1)
                
            emp_count = 0
            try:
                t_db = get_tenant_session(comp.tax_code)
                emp_count = t_db.query(Employee).count()
                t_db.close()
            except Exception:
                pass
                
            result.append({
                "tax_code": comp.tax_code,
                "code": comp.code or f"CTY-{comp.tax_code[:4]}",
                "name": comp.name,
                "short_name": comp.short_name or "",
                "legal_rep": comp.legal_rep or "",
                "address": comp.address or "",
                "phone": comp.phone or "",
                "email": comp.email or "",
                "website": comp.website or "",
                "business_field": comp.business_field or "",
                "db_path": comp.db_path,
                "db_size_kb": file_size_kb,
                "emp_count": emp_count,
                "status": comp.status,
                "created_at": comp.created_at.strftime("%Y-%m-%d %H:%M") if comp.created_at else ""
            })
            
        return {"success": True, "companies": result}
    finally:
        master_db.close()

@router.post("/api/companies/create")
def api_create_company(
    request: Request,
    tax_code: str = Form(...),
    code: str = Form(""),
    name: str = Form(...),
    short_name: str = Form(""),
    legal_rep: str = Form(""),
    address: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    business_field: str = Form(""),
    admin_email: str = Form(...),
    admin_pass: str = Form("Admin@123")
):
    """Creates a new Company entity, initializes dedicated tenant SQLite database, and seeds admin."""
    check_master_system_admin(request)
    
    try:
        res = create_company_tenant(
            tax_code=tax_code,
            code=code,
            name=name,
            short_name=short_name,
            legal_rep=legal_rep,
            address=address,
            phone=phone,
            email=email,
            website=website,
            business_field=business_field,
            admin_email=admin_email,
            admin_pass=admin_pass
        )
        return {"success": True, "message": f"✅ Đã tạo thành công công ty '{name}' (MST: {tax_code}) và cơ sở dữ liệu riêng!", "data": res}
    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    except Exception as e:
        return {"success": False, "message": f"❌ Lỗi tạo công ty: {str(e)}"}

@router.post("/api/companies/update")
def api_update_company(
    request: Request,
    tax_code: str = Form(...),          # Original Tax Code
    new_tax_code: str = Form(None),     # Optional updated Tax Code
    code: str = Form(""),
    name: str = Form(...),
    short_name: str = Form(""),
    legal_rep: str = Form(""),
    address: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    website: str = Form(""),
    business_field: str = Form("")
):
    """Updates company profile metadata in Master DB according to real-world information."""
    check_master_system_admin(request)
    
    old_mst = str(tax_code or "").strip()
    target_mst = str(new_tax_code or old_mst).strip()
    
    master_db: Session = MasterSessionLocal()
    try:
        comp = master_db.query(MasterCompany).filter_by(tax_code=old_mst).first()
        if not comp:
            return {"success": False, "message": "Không tìm thấy thông tin công ty để sửa!"}
            
        if target_mst and target_mst != old_mst:
            existing = master_db.query(MasterCompany).filter_by(tax_code=target_mst).first()
            if existing:
                return {"success": False, "message": f"Mã Số Thuế mới '{target_mst}' đã trùng với công ty khác!"}
                
            old_db_path = get_tenant_db_path(old_mst)
            new_db_path = get_tenant_db_path(target_mst)
            
            if os.path.exists(old_db_path) and old_mst not in ["0312345678", "default"]:
                try:
                    os.rename(old_db_path, new_db_path)
                except Exception as ex:
                    print("[MULTI-TENANT] Rename DB file warning:", ex)
                    
            user_idxs = master_db.query(GlobalUserIndex).filter_by(tax_code=old_mst).all()
            for uidx in user_idxs:
                uidx.tax_code = target_mst
                
            comp.tax_code = target_mst
            comp.db_path = new_db_path
            
        comp.code = code or f"CTY-{target_mst[:4]}"
        comp.name = name
        comp.short_name = short_name
        comp.legal_rep = legal_rep
        comp.address = address
        comp.phone = phone
        comp.email = email
        comp.website = website
        comp.business_field = business_field
        
        master_db.commit()
        return {"success": True, "message": f"✅ Đã cập nhật thành công thông tin công ty '{name}' theo thực tế!"}
    except Exception as e:
        master_db.rollback()
        return {"success": False, "message": f"❌ Lỗi cập nhật công ty: {str(e)}"}
    finally:
        master_db.close()

@router.post("/api/companies/add-employee")
def api_add_employee(
    request: Request,
    tax_code: str = Form(...),
    ma_nv: str = Form(...),
    ten_nv: str = Form(...),
    email: str = Form(...),
    mat_khau: str = Form(...),
    quyen: str = Form("USER"),
    phong_ban: str = Form("")
):
    """Adds a new employee to a target company's tenant DB and registers in Global User Index."""
    check_master_system_admin(request)
    
    clean_tax_code = str(tax_code or "").strip()
    clean_email = str(email or "").strip().lower()
    clean_ma_nv = str(ma_nv or "").strip().upper()
    
    if not clean_tax_code or not clean_email or not clean_ma_nv:
        return {"success": False, "message": "Vui lòng điền đầy đủ Mã công ty, Email và Mã NV!"}
        
    master_db: Session = MasterSessionLocal()
    try:
        existing_global = master_db.query(GlobalUserIndex).filter_by(email=clean_email).first()
        if existing_global:
            return {"success": False, "message": f"Địa chỉ Email '{clean_email}' đã được đăng ký trong hệ thống!"}
            
        t_db = get_tenant_session(clean_tax_code)
        try:
            emp = Employee(
                ma_nv=clean_ma_nv,
                ten_nv=ten_nv,
                mat_khau=mat_khau,
                email=clean_email,
                quyen=quyen,
                phong_ban=phong_ban
            )
            t_db.add(emp)
            t_db.commit()
        except Exception as e:
            t_db.rollback()
            return {"success": False, "message": f"Lỗi tạo nhân viên trong DB công ty: {str(e)}"}
        finally:
            t_db.close()
            
        user_idx = GlobalUserIndex(
            email=clean_email,
            tax_code=clean_tax_code,
            ma_nv=clean_ma_nv
        )
        master_db.add(user_idx)
        master_db.commit()
        
        return {"success": True, "message": f"✅ Khai báo thành công nhân viên '{ten_nv}' cho công ty {clean_tax_code}!"}
    finally:
        master_db.close()

@router.post("/api/companies/toggle-status")
def api_toggle_company_status(
    request: Request,
    tax_code: str = Form(...)
):
    """Toggles ACTIVE / INACTIVE status of a company."""
    check_master_system_admin(request)
    
    master_db: Session = MasterSessionLocal()
    try:
        comp = master_db.query(MasterCompany).filter_by(tax_code=tax_code).first()
        if not comp:
            return {"success": False, "message": "Không tìm thấy thông tin công ty!"}
            
        new_status = "INACTIVE" if comp.status == "ACTIVE" else "ACTIVE"
        comp.status = new_status
        master_db.commit()
        return {"success": True, "message": f"Đã cập nhật trạng thái công ty '{comp.name}' thành {new_status}!"}
    finally:
        master_db.close()

@router.post("/api/companies/delete")
def api_delete_company(
    request: Request,
    tax_code: str = Form(...)
):
    """Deletes a company tenant, all associated global user index entries, and removes its SQLite DB file."""
    check_master_system_admin(request)
    
    clean_mst = str(tax_code or "").strip()
    try:
        res = delete_company_tenant(clean_mst)
        return res
    except ValueError as ve:
        return {"success": False, "message": str(ve)}
    except Exception as e:
        return {"success": False, "message": f"❌ Lỗi xóa công ty: {str(e)}"}

@router.post("/api/companies/switch-tenant")
def api_switch_tenant(
    request: Request,
    response: Response,
    tax_code: str = Form(...)
):
    """Allows Master Admin NSX to instantly switch active tenant session to any company."""
    session = check_master_system_admin(request)
    target_mst = str(tax_code or "").strip()
    
    master_db: Session = MasterSessionLocal()
    try:
        comp = master_db.query(MasterCompany).filter_by(tax_code=target_mst).first()
        if not comp:
            return {"success": False, "message": f"Không tìm thấy công ty có MST {target_mst}!"}
            
        new_session = {
            "ma": "ADMIN",
            "ten": f"Admin NSX ({comp.name})",
            "role": "ADMIN",
            "email": session.get("email", "admin@ams.vn"),
            "company_mst": comp.tax_code,
            "company_name": comp.name,
            "is_master_admin": True
        }
        AuthService.set_session(response, new_session)
        return {
            "success": True, 
            "message": f"✅ Đã chuyển sang làm việc tại công ty '{comp.name}' (MST: {comp.tax_code})!",
            "redirect_url": "/dashboard"
        }
    finally:
        master_db.close()



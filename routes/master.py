from fastapi import APIRouter, Depends, Request, Response, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from services.department_service import DepartmentService
from services.employee_service import EmployeeService
from services.ai_service import AIService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Web Pages
@router.get("/master/departments", response_class=HTMLResponse)
def get_departments_page(request: Request):
    """Renders the department master data page. Requires admin/manager role."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if session["role"] not in ["ADMIN", "CEO", "MANAGER"]:
        return RedirectResponse(url="/dashboard")
        
    return templates.TemplateResponse(request, "master/departments.html", {
        "user": session
    })

@router.get("/master/employees", response_class=HTMLResponse)
def get_employees_page(request: Request):
    """Renders the employee master data page. Requires admin/ceo role."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if session["role"] not in ["ADMIN", "CEO"]:
        return RedirectResponse(url="/dashboard")
        
    return templates.TemplateResponse(request, "master/employees.html", {
        "user": session
    })

# JSON APIs

# 1. Department Endpoints
@router.get("/api/departments")
def api_get_departments(request: Request, db: Session = Depends(get_db)):
    """API to fetch all departments."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
    return DepartmentService.get_department_management_data(db)

def _require_dept_admin(request: Request):
    """Enforces login + ADMIN/CEO/MANAGER role for department write operations.
    Returns the session dict, or an error dict to be returned directly by the caller.
    """
    session = AuthService.get_session(request)
    if not session:
        return None, {"success": False, "message": "🚨 Chưa đăng nhập!"}
    if session.get("role") not in ["ADMIN", "CEO", "MANAGER"]:
        return None, {"success": False, "message": "🚨 Không có quyền truy cập!"}
    return session, None


@router.post("/api/departments")
def api_add_department(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to add a new department."""
    session, err = _require_dept_admin(request)
    if err:
        return err
    return DepartmentService.add_department(db, payload)

@router.post("/api/departments/update")
def api_update_department(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to update a department."""
    session, err = _require_dept_admin(request)
    if err:
        return err
    return DepartmentService.update_department(db, payload)

@router.delete("/api/departments/{ma_bp}")
def api_delete_department(ma_bp: str, request: Request, db: Session = Depends(get_db)):
    """API to delete a department."""
    session, err = _require_dept_admin(request)
    if err:
        return err
    return DepartmentService.delete_department(db, ma_bp)

@router.post("/api/departments/generate")
def api_generate_department_functions(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to generate department functions and duties via AI."""
    session, err = _require_dept_admin(request)
    if err:
        return err
    prompt = payload.get("prompt", "").strip()
    if not prompt:
        return {"success": False, "message": "Nội dung yêu cầu không được trống!"}
        
    try:
        data = AIService.generate_department_functions(db, prompt)
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "message": f"AI Generation Error: {str(e)}"}


# 2. Employee Endpoints
@router.get("/api/employees")
def api_get_employees(request: Request, dropdown: bool = False, db: Session = Depends(get_db)):
    """API to fetch employees (either for management grid or for selection dropdowns)."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
        
    if dropdown:
        return EmployeeService.get_employees_for_dropdown(db)
        
    if session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Không có quyền truy cập!"}
        
    return EmployeeService.get_employee_management_data(db)

@router.post("/api/employees")
def api_add_employee(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to add a new employee."""
    session = AuthService.get_session(request)
    if not session or session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Không có quyền truy cập!"}
    company_mst = session.get("company_mst", "0312345678")
    msg = EmployeeService.add_employee(db, payload, company_mst=company_mst)
    return {"success": "thành công" in msg.lower() or "✅" in msg, "message": msg}

@router.post("/api/employees/update")
def api_update_employee(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to update employee details."""
    session = AuthService.get_session(request)
    if not session or session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Không có quyền truy cập!"}
    company_mst = session.get("company_mst", "0312345678")
    msg = EmployeeService.update_employee(db, payload, company_mst=company_mst)
    return {"success": "thành công" in msg.lower() or "✅" in msg, "message": msg}


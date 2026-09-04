from fastapi import APIRouter, Depends, Request, Response, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Web Pages
@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    """Root URL redirects to dashboard, which acts as the SPA home."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/dashboard")

@router.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    """Renders the login page. Redirects to dashboard if already authenticated."""
    session = AuthService.get_session(request)
    if session:
        return RedirectResponse(url="/dashboard")
    return templates.TemplateResponse(request, "login.html")

@router.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    """Renders the main dashboard menu (MainForm). Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "dashboard.html", {
        "user": session
    })

@router.get("/auth/change-password", response_class=HTMLResponse)
def get_change_password(request: Request):
    """Renders the change password page. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "auth/change_password.html", {
        "user": session
    })

# Public Lookup APIs
@router.get("/api/auth/company-lookup")
def api_company_lookup(tax_code: str = Query("")):
    """Public lookup for company metadata and status based on Tax Code (MST)."""
    clean_mst = str(tax_code or "").strip()
    if not clean_mst:
        return {"success": False, "message": "Vui lòng nhập Mã số thuế!"}
        
    from database.multi_tenant import MasterSessionLocal
    from models.master_models import MasterCompany
    master_db = MasterSessionLocal()
    try:
        comp = master_db.query(MasterCompany).filter_by(tax_code=clean_mst).first()
        if not comp:
            return {"success": False, "message": "Mã số thuế chưa đăng ký hệ thống!"}
        if comp.status != "ACTIVE":
            return {"success": False, "message": f"Công ty '{comp.name}' đang tạm khóa!"}
        return {
            "success": True,
            "tax_code": comp.tax_code,
            "name": comp.name,
            "short_name": comp.short_name or "",
            "status": comp.status
        }
    finally:
        master_db.close()

@router.get("/api/auth/lookup-user-tenant")
def api_lookup_user_tenant(username: str = Query("")):
    """Public lookup to discover user's registered company MST ONLY by unique email."""
    clean_user = str(username or "").strip().lower()
    if not clean_user or "@" not in clean_user:
        return {"success": False}
        
    from database.multi_tenant import MasterSessionLocal
    from models.master_models import GlobalUserIndex, MasterCompany
    master_db = MasterSessionLocal()
    try:
        user_idx = master_db.query(GlobalUserIndex).filter(
            GlobalUserIndex.email == clean_user
        ).first()
        if user_idx:
            comp = master_db.query(MasterCompany).filter_by(tax_code=user_idx.tax_code).first()
            return {
                "success": True,
                "tax_code": user_idx.tax_code,
                "company_name": comp.name if comp else ""
            }
        return {"success": False}
    finally:
        master_db.close()

# API JSON Endpoints
@router.post("/api/auth/login")
async def api_login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Universal login endpoint supporting Form Data, JSON payloads, and Query Params."""
    username = ""
    password = ""
    tax_code = None
    
    # 1. Check if request is JSON
    content_type = request.headers.get("content-type", "").lower()
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                username = str(body.get("username", "") or "").strip()
                password = str(body.get("password", "") or "").strip()
                tax_code = body.get("tax_code", None)
        except Exception:
            pass
            
    # 2. Check if request is Form Data
    if not username and not password:
        try:
            form = await request.form()
            username = str(form.get("username", "") or "").strip()
            password = str(form.get("password", "") or "").strip()
            tax_code = form.get("tax_code", None)
        except Exception:
            pass
            
    # 3. Fallback to Query Parameters
    if not username:
        username = str(request.query_params.get("username", "") or "").strip()
    if not password:
        password = str(request.query_params.get("password", "") or "").strip()
    if not tax_code:
        tax_code = request.query_params.get("tax_code", None)
        
    if tax_code is not None:
        tax_code = str(tax_code).strip()
        if not tax_code:
            tax_code = None
            
    try:
        import anyio
        res = await anyio.to_thread.run_sync(AuthService.check_login, db, username, password, tax_code)
        if res and res.get("success"):
            session_data = {
                "ma": res.get("maNV", "ADMIN"),
                "ten": res.get("userName", "Quản trị viên"),
                "role": res.get("role", "ADMIN"),
                "email": res.get("email", ""),
                "company_mst": res.get("company_mst", "0312345678"),
                "company_name": res.get("company_name", ""),
                "is_master_admin": res.get("is_master_admin", False)
            }
            AuthService.set_session(response, session_data)
            return {
                "success": True, 
                "userName": res.get("userName", "Quản trị viên"), 
                "role": res.get("role", "ADMIN"),
                "company_name": res.get("company_name", "")
            }
        return {"success": False, "message": (res and res.get("message")) or "Tài khoản hoặc mật khẩu không chính xác!"}
    except Exception as e_login:
        print("[API_LOGIN] Error:", repr(e_login))
        return {"success": False, "message": f"Lỗi đăng nhập: {str(e_login)}"}

@router.post("/api/auth/change-password")
def api_change_password(
    request: Request,
    oldPass: str = Form(...),
    newPass: str = Form(...),
    db: Session = Depends(get_db)
):
    """API endpoint to process password changes."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập hệ thống!"}
        
    res = AuthService.change_password(db, session["ma"], oldPass, newPass)
    return res

@router.post("/api/auth/logout")
@router.get("/logout")
def logout():
    """Clears the authentication session and redirects to login."""
    response = RedirectResponse(url="/login", status_code=303)
    AuthService.clear_session(response)
    return response

@router.get("/api/dashboard/stats")
def api_dashboard_stats(request: Request, db: Session = Depends(get_db)):
    """Retrieves session dashboard statistics for current user."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa xác thực!"}
        
    stats = AuthService.get_dashboard_stats(db, session["ma"], session["role"])
    return stats

# Helper API to bridge getCurrentUser in front-end
@router.get("/api/auth/current-user")
def api_current_user(request: Request):
    """Helper to return current logged-in user info to frontend."""
    session = AuthService.get_session(request)
    if not session:
        return {"ma": "", "ten": "Khách", "role": "USER", "company_mst": "", "company_name": ""}
    return session

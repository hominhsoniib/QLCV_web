from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from models.models import Employee, Department

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/org-chart", response_class=HTMLResponse)
def get_org_chart_page(request: Request, db: Session = Depends(get_db)):
    """Renders the organization chart page. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
        
    employees = db.query(Employee).all()
    departments = db.query(Department).all()
    
    # Format employees to simple list of dicts for JSON serialization in JS
    emp_list = []
    for e in employees:
        emp_list.append({
            "ma_nv": e.ma_nv,
            "ten_nv": e.ten_nv,
            "chuc_danh": e.chuc_danh or e.chuc_vu or "Nhân sự",
            "phong_ban": e.phong_ban,
            "nguoi_ql": e.nguoi_ql
        })
        
    return templates.TemplateResponse(request, "org_chart.html", {
        "user": session,
        "employees": emp_list,
        "departments": departments
    })

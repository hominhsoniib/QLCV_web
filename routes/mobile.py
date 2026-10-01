from fastapi import APIRouter, Depends, Request, Response, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from services.task_service import TaskService
from models.models import Task, Employee
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/mobile", response_class=HTMLResponse)
@router.get("/mobile/dashboard", response_class=HTMLResponse)
def get_mobile_dashboard(request: Request, db: Session = Depends(get_db)):
    """Màn hình chính của phiên bản điện thoại."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/mobile/login")
    
    ma_nv = str(session.get("ma", "")).strip().upper()
    role = str(session.get("role", "")).strip().upper()

    # Query tasks for user
    query = db.query(Task)
    if role != "ADMIN" and ma_nv != "ADMIN":
        query = query.filter((Task.nguoi_nhan == ma_nv) | (Task.nguoi_giao == ma_nv))
    
    all_tasks = query.all()
    
    total_count = len(all_tasks)
    done_count = sum(1 for t in all_tasks if str(t.trang_thai or "").lower() in ["hoàn thành", "done", "đã hoàn thành"])
    in_progress_count = sum(1 for t in all_tasks if str(t.trang_thai or "").lower() in ["đang làm", "đang thực hiện", "in_progress"])
    late_count = sum(1 for t in all_tasks if str(t.trang_thai or "").lower() in ["quá hạn", "trễ hạn", "overdue"])
    
    # Recent 5 tasks
    recent_tasks = sorted(all_tasks, key=lambda x: x.id or 0, reverse=True)[:5]
    
    return templates.TemplateResponse(request, "mobile/dashboard.html", {
        "user": session,
        "total_count": total_count,
        "done_count": done_count,
        "in_progress_count": in_progress_count,
        "late_count": late_count,
        "recent_tasks": recent_tasks,
        "active_tab": "dashboard"
    })

@router.get("/mobile/login", response_class=HTMLResponse)
def get_mobile_login(request: Request):
    """Màn hình đăng nhập di động."""
    session = AuthService.get_session(request)
    if session:
        return RedirectResponse(url="/mobile/dashboard")
    return templates.TemplateResponse(request, "mobile/login.html")

@router.get("/mobile/tasks", response_class=HTMLResponse)
def get_mobile_tasks(request: Request, status: str = Query("all"), db: Session = Depends(get_db)):
    """Màn hình Quản lý Công việc di động."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/mobile/login")
    
    ma_nv = str(session.get("ma", "")).strip().upper()
    role = str(session.get("role", "")).strip().upper()

    query = db.query(Task)
    if role != "ADMIN" and ma_nv != "ADMIN":
        query = query.filter((Task.nguoi_nhan == ma_nv) | (Task.nguoi_giao == ma_nv))
    
    if status == "doing":
        query = query.filter(Task.trang_thai.ilike("%đang%"))
    elif status == "done":
        query = query.filter(Task.trang_thai.ilike("%hoàn thành%"))
    elif status == "late":
        query = query.filter(Task.trang_thai.ilike("%quá hạn%"))

    tasks = query.order_by(Task.id.desc()).all()
    
    return templates.TemplateResponse(request, "mobile/tasks.html", {
        "user": session,
        "tasks": tasks,
        "current_status": status,
        "active_tab": "tasks"
    })

@router.get("/mobile/ai", response_class=HTMLResponse)
def get_mobile_ai(request: Request):
    """Màn hình Trợ lý AI di động."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/mobile/login")
        
    return templates.TemplateResponse(request, "mobile/ai.html", {
        "user": session,
        "active_tab": "ai"
    })

@router.get("/mobile/menu", response_class=HTMLResponse)
def get_mobile_menu(request: Request):
    """Màn hình Menu di động."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/mobile/login")
        
    return templates.TemplateResponse(request, "mobile/menu.html", {
        "user": session,
        "active_tab": "menu"
    })

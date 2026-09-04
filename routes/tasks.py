from fastapi import APIRouter, Depends, Request, Response, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from services.task_service import TaskService
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Web Pages
@router.get("/tasks", response_class=HTMLResponse)
def get_tasks_page(request: Request):
    """Renders the main task board page (FormIndex). Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "tasks/index.html", {
        "user": session
    })

@router.get("/tasks/personal", response_class=HTMLResponse)
def get_personal_tasks_page(request: Request):
    """Renders personal task planner page. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "tasks/personal.html", {
        "user": session
    })

@router.get("/tasks/overdue", response_class=HTMLResponse)
def get_overdue_tasks_page(request: Request):
    """Renders overdue warnings radar page. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "tasks/overdue.html", {
        "user": session
    })

@router.get("/tasks/report", response_class=HTMLResponse)
def get_task_report_page(request: Request, id: str = None):
    """Renders the task reporting page. Fallbacks to session variable if id is omitted."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    
    # If id is not in query parameters, check if it's stored in session cookie
    task_id = id or session.get("temp_task_id", "")
    
    return templates.TemplateResponse(request, "tasks/report.html", {
        "user": session,
        "taskId": task_id
    })

@router.get("/tasks/forward", response_class=HTMLResponse)
def get_task_forward_page(request: Request, id: str = None):
    """Renders the delegation/forwarding page. Fallbacks to session if ID omitted."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
        
    task_id = id or session.get("temp_task_id", "")
    
    return templates.TemplateResponse(request, "tasks/forward.html", {
        "user": session,
        "taskId": task_id
    })

@router.get("/tasks/remind", response_class=HTMLResponse)
def get_task_remind_page(request: Request, id: str = None):
    """Renders task reminder manager. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
        
    task_id = id or session.get("temp_task_id", "")
    
    return templates.TemplateResponse(request, "tasks/remind.html", {
        "user": session,
        "taskId": task_id
    })

@router.get("/tasks/report-center", response_class=HTMLResponse)
def get_report_center_page(request: Request):
    """Renders the report analytics center. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "tasks/report_center.html", {
        "user": session
    })

from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
import os

@router.get("/guide", response_class=HTMLResponse)
@router.get("/tasks/guide", response_class=HTMLResponse)
def get_full_guide_page(request: Request):
    """Renders the full standalone HTML user guide page."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "help_guide.html", {
        "user": session
    })

@router.get("/download-guide-word")
def download_guide_word():
    """Serves the Huong_Dan_Su_Dung_AMS_PRO_5.0.docx file for direct download."""
    file_path = "Huong_Dan_Su_Dung_AMS_PRO_5.0.docx"
    if os.path.exists(file_path):
        return FileResponse(
            path=file_path,
            filename="Huong_Dan_Su_Dung_AMS_PRO_5.0.docx",
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    return {"success": False, "message": "File Word chưa được tạo."}

@router.get("/VALUECHAIN-PB.png")
def get_value_chain_img():
    """Serves the VALUECHAIN-PB.png image file."""
    file_path = "VALUECHAIN-PB.png"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    return {"success": False, "message": "Image not found."}

@router.get("/so-do-gia-pha.png")
@router.get("/so_do_gia_pha.png")
def get_so_do_gia_pha_img():
    """Serves the so do gia pha.png image file."""
    file_path = "so do gia pha.png"
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="image/png")
    return {"success": False, "message": "Image not found."}






# API Endpoints
@router.get("/api/tasks")
def api_get_tasks(request: Request, db: Session = Depends(get_db)):
    """API to fetch all tasks visible to the current logged-in user."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
    return TaskService.get_index_init_data(db, session["ma"], session["role"])

@router.post("/api/tasks")
def api_save_task(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to save or update task data."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
    return TaskService.save_task_data(db, payload)

@router.get("/api/tasks/suggested-code")
def api_suggested_code(prefix: str, db: Session = Depends(get_db)):
    """API to generate the next suggested task code (MaCV)."""
    return TaskService.get_suggested_ma_cv(db, prefix)

@router.get("/api/tasks/{task_id}")
def api_get_task_by_id(task_id: str, db: Session = Depends(get_db)):
    """API to get details of a specific task."""
    task = TaskService.get_task_by_id(db, task_id)
    if not task:
        return {"success": False, "message": f"Task [{task_id}] not found"}
    return task

@router.post("/api/tasks/{task_id}/report")
def api_update_report(task_id: str, payload: dict, db: Session = Depends(get_db)):
    """API to submit a progress report for a task."""
    payload["id"] = task_id
    return TaskService.update_bao_cao(db, payload)

@router.post("/api/tasks/{task_id}/remind")
def api_update_remind(task_id: str, payload: dict, db: Session = Depends(get_db)):
    """API to post a management directive or reminder."""
    message = payload.get("message", "")
    return TaskService.update_nhac_nho(db, task_id, message)

@router.post("/api/tasks/forward")
def api_forward_task(payload: dict, db: Session = Depends(get_db)):
    """API to forward/delegate a task to another employee."""
    return TaskService.save_forward(db, payload)


# Temporary ID session bridge (to match Apps Script Task_setTempId & Task_getTempId)
@router.post("/api/tasks/set-temp-id")
def api_set_temp_id(response: Response, request: Request, payload: dict):
    """Sets a temporary task ID in the user session cookie."""
    session = AuthService.get_session(request)
    if session:
        session["temp_task_id"] = payload.get("id", "")
        AuthService.set_session(response, session)
        return {"success": True}
    return {"success": False}

@router.get("/api/tasks/get-temp-id")
def api_get_temp_id(request: Request):
    """Retrieves the temporary task ID from the user session."""
    session = AuthService.get_session(request)
    if session:
        return session.get("temp_task_id", "")
    return ""

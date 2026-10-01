from fastapi import APIRouter, Depends, Request, Response, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from services.document_service import DocumentService
from services.drive_service import DriveService
from models.models import Department, Employee, Document
from services.file_registry import FileRegistry, RegistryError
from services.file_binding_service import FileBindingService
from config import Config

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Web Pages
@router.get("/documents", response_class=HTMLResponse)
def get_documents_page(request: Request, db: Session = Depends(get_db)):
    """Renders the document management admin page. Requires ADMIN or CEO role."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if session["role"] not in ["ADMIN", "CEO"]:
        return RedirectResponse(url="/documents/repository")
        
    departments = db.query(Department).order_by(Department.ten_bp).all()
    return templates.TemplateResponse(request, "documents/index.html", {
        "user": session,
        "departments": departments
    })

@router.get("/documents/repository", response_class=HTMLResponse)
def get_repository_page(request: Request):
    """Renders the internal read-only document repository page. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "documents/repository.html", {
        "user": session
    })


# JSON APIs

# 1. Document CRUD Endpoints
@router.get("/api/documents")
def api_get_documents(request: Request, db: Session = Depends(get_db)):
    """API to fetch all documents. Requires ADMIN or CEO role."""
    session = AuthService.get_session(request)
    if not session or session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Bạn không có quyền thực hiện hành động này!"}
    return DocumentService.get_document_management_data(db)

@router.post("/api/documents")
def api_add_document(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to add a document. Requires ADMIN or CEO role."""
    session = AuthService.get_session(request)
    if not session or session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Bạn không có quyền thực hiện hành động này!"}
    return _save_document_binding(db,session,payload,create=True)

@router.post("/api/documents/update")
def api_update_document(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to update document details. Requires ADMIN or CEO role."""
    session = AuthService.get_session(request)
    if not session or session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Bạn không có quyền thực hiện hành động này!"}
    return _save_document_binding(db,session,payload,create=False)


def _save_document_binding(db,session,payload,*,create):
    ma=str(payload.get('maTL','')).strip()
    row=db.query(Document).filter(Document.ma_tl==ma).first()
    if (create and row is not None) or (not create and row is None) or not db.query(Employee).filter(Employee.ma_nv==session.get('ma')).first():
        return {'success':False,'message':'Dữ liệu không hợp lệ.'}
    url=str(payload.get('linkFile','')).strip()
    old=row.link_file or '' if row else ''
    def mutate():
        msg=(DocumentService.add_document if create else DocumentService.update_document)(db,payload)
        return {'success':'Thành công' in msg or '✅' in msg,'message':msg}
    try:
        return FileBindingService(db,session.get('company_mst'),session.get('ma')).run(
            Document,'DOCUMENT',ma,'link_file',url,old,mutate)
    except RegistryError:
        db.rollback()
        return {'success':False,'message':'Không thể xác thực/lưu liên kết tệp.'}

@router.delete("/api/documents/{ma_tl}")
def api_delete_document(ma_tl: str, request: Request, db: Session = Depends(get_db)):
    """API to delete a document. Requires ADMIN or CEO role."""
    session = AuthService.get_session(request)
    if not session or session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Bạn không có quyền thực hiện hành động này!"}
    msg = DocumentService.delete_document(db, ma_tl)
    return {"success": "Thành công" in msg or "✅" in msg, "message": msg}

@router.get("/api/documents/next-code")
def api_get_next_code(loai: str, db: Session = Depends(get_db)):
    """API to generate the next document code for a given type (e.g. 'Biểu mẫu')."""
    code = DocumentService.get_next_doc_code(db, loai)
    return code

def readable_documents_query(db, session):
    """Unchanged library READ predicate, shared with the private gateway."""
    role = session.get("role", "USER")
    username = session.get("ma", "")
    
    # 1. Admin and CEO can see all documents
    if role in ["ADMIN", "CEO"]:
        docs = db.query(Document)
    else:
        from sqlalchemy import or_
        # Get employee's department
        emp = db.query(Employee).filter(Employee.ma_nv == username).first()
        user_dept = emp.phong_ban if emp else ""
        
        conds = [
            (Document.phong_ban == None),
            (Document.phong_ban == ""),
            (Document.phong_ban == "Tất cả")
        ]
        
        if role == "MANAGER":
            # Manager sees their own department + subordinates' departments
            subordinates = db.query(Employee).filter(Employee.nguoi_ql == username).all()
            sub_depts = {sub.phong_ban for sub in subordinates if sub.phong_ban}
            if user_dept:
                sub_depts.add(user_dept)
                
            if sub_depts:
                conds.append(Document.phong_ban.in_(list(sub_depts)))
        else:
            # Regular USER sees their own department + general documents
            if user_dept:
                conds.append(Document.phong_ban == user_dept)
                
        docs = db.query(Document).filter(or_(*conds))
    return docs


@router.get("/api/documents/library")
def api_get_library(request: Request, db: Session = Depends(get_db)):
    """Library and gateway use the same existing READ predicate."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
    role = session.get("role", "USER")
    docs = readable_documents_query(db, session).all()

    import re
    
    def get_safe_preview_url(link: str) -> str:
        """Converts a raw document link to a clean in-app preview URL."""
        if not link:
            return ""
        
        url = link.strip()
        
        # 1. Rewrite local file path (file:///D:/POWER%20BI-VBA%20EXCEL/... -> /local_docs/...)
        if url.startswith("file:///D:/POWER%20BI-VBA%20EXCEL/QLCV-QT-MTCV/") or url.startswith("file:///D:/POWER BI-VBA EXCEL/QLCV-QT-MTCV/"):
            url = url.replace("file:///D:/POWER%20BI-VBA%20EXCEL/QLCV-QT-MTCV/", "/local_docs/").replace("file:///D:/POWER BI-VBA EXCEL/QLCV-QT-MTCV/", "/local_docs/")
        elif url.startswith("D:/POWER BI-VBA EXCEL/QLCV-QT-MTCV/") or url.startswith("D:\\POWER BI-VBA EXCEL\\QLCV-QT-MTCV\\"):
            url = url.replace("D:/POWER BI-VBA EXCEL/QLCV-QT-MTCV/", "/local_docs/").replace("D:\\POWER BI-VBA EXCEL\\QLCV-QT-MTCV\\", "/local_docs/").replace("\\", "/")
        
        # 2. Google Drive Folders (embed as grid view)
        if "drive.google.com" in url and "/folders/" in url:
            match = re.search(r"/folders/([a-zA-Z0-9-_]+)", url)
            if match:
                return f"https://drive.google.com/embeddedfolderview?id={match.group(1)}#grid"
                
        # 3. Google Sheets / Docs / Slides (replace /edit or /view with /preview)
        if "docs.google.com" in url:
            if "/edit" in url:
                return url.split("/edit")[0] + "/preview"
            if "/view" in url:
                return url.split("/view")[0] + "/preview"
                
        return url

    data = []
    for d in docs:
        raw_link = d.link_file or ""
        preview_url = get_safe_preview_url(raw_link)
        data.append({
            "maTL": d.ma_tl,
            "tenTL": d.ten_tl,
            "loai": d.loai,
            "ngayCapNhat": d.ngay_cap_nhat or "",
            "linkFile": raw_link if role == "ADMIN" else "",
            "previewUrl": preview_url,
            "phongBan": d.phong_ban or "Tất cả"
        })
    return {"success": True, "data": data}


# 2. File Upload & Drive Integration Endpoints
def _require_file_session(request: Request) -> dict:
    """Use only the signed QLCV identity; never accept a client-supplied tenant."""
    session = AuthService.get_session(request)
    if (not isinstance(session, dict)
            or not isinstance(session.get("ma"), str) or not session["ma"].strip()
            or not isinstance(session.get("company_mst"), str) or not session["company_mst"].strip()):
        raise HTTPException(status_code=401, detail="Authentication required.")
    return session


def _deny_unverified_drive_mutation():
    # Task/Document URLs are editable references, not proof of Drive ownership.
    # Global service-account access and client fileId/maCV cannot authorize a
    # tenant-scoped rename. Fail closed until trusted ownership metadata exists.
    raise HTTPException(status_code=403, detail="Drive file ownership cannot be verified; operation disabled.")


@router.post("/api/drive/upload-local")
def api_upload_local(file: UploadFile = File(...), session: dict = Depends(_require_file_session), db: Session = Depends(get_db)):
    """Handles standard local file uploads. Saves file in upload folder and returns path."""
    if not db.query(Employee).filter(Employee.ma_nv==session['ma']).first():
        raise HTTPException(status_code=401,detail='Authentication required.')
    url = DriveService.upload_local_file(file,tenant_id=session['company_mst'],uploader_id=session['ma'])
    if url:
        record=FileRegistry().get_file_by_storage(session['company_mst'],Config.UPLOAD_STORAGE_ROOT_ID,url.rsplit('/',1)[1])
        return {"success": True, "url": url, "name": file.filename,"file_id":record['file_id']}
    return {"success": False, "message": "Lỗi lưu file cục bộ."}

@router.post("/api/drive/rename-task-file")
def api_rename_task_file(payload: dict, session: dict = Depends(_require_file_session)):
    """API to rename a file picked from Google Drive for task assignment."""
    _deny_unverified_drive_mutation()

@router.post("/api/drive/rename-report-file")
def api_rename_report_file(payload: dict, session: dict = Depends(_require_file_session)):
    """API to rename a file picked from Google Drive for progress reporting."""
    _deny_unverified_drive_mutation()

@router.post("/api/drive/rename-forward-file")
def api_rename_forward_file(payload: dict, session: dict = Depends(_require_file_session)):
    """API to rename a file picked from Google Drive for task delegation."""
    _deny_unverified_drive_mutation()

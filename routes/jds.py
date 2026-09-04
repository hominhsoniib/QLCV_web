from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from services.ai_service import AIService
from models.models import JobDescription, Employee, Department
import json
import io
from urllib.parse import quote
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/job-descriptions", response_class=HTMLResponse)
def get_jds_page(request: Request, db: Session = Depends(get_db)):
    """Renders the Job Descriptions management page. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
        
    employees = db.query(Employee).order_by(Employee.ten_nv).all()
    departments = db.query(Department).all()
    return templates.TemplateResponse(request, "jds.html", {
        "user": session,
        "employees": employees,
        "departments": departments
    })

@router.get("/api/jds/employee/{ma_nv}")
def api_get_employee_jd(ma_nv: str, request: Request, db: Session = Depends(get_db)):
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập!"}
        
    ma_nv_upper = ma_nv.strip().upper()
    
    # 1. Look for employee-specific JD
    jd = db.query(JobDescription).filter(JobDescription.ma_nv == ma_nv_upper).first()
    
    # 2. If not found, look for generic title JD if employee has a title (or fallback to chuc_vu/ten_nv)
    emp = db.query(Employee).filter(Employee.ma_nv == ma_nv_upper).first()
    emp_chuc_danh = ""
    if emp:
        emp_chuc_danh = emp.chuc_danh.strip() if emp.chuc_danh else (emp.chuc_vu.strip() if emp.chuc_vu else emp.ten_nv.strip())
        
    if not jd and emp_chuc_danh:
        jd = db.query(JobDescription).filter(
            (JobDescription.chuc_danh == emp_chuc_danh) & 
            ((JobDescription.ma_nv == None) | (JobDescription.ma_nv == ""))
        ).first()
        
    if not jd:
        return {"success": True, "data": None, "employee": {
            "ma_nv": emp.ma_nv if emp else ma_nv_upper,
            "ten_nv": emp.ten_nv if emp else "",
            "chuc_danh": emp_chuc_danh
        } if emp else None}
        
    try:
        responsibilities = json.loads(jd.responsibilities)
    except:
        responsibilities = []
        
    try:
        authority = json.loads(jd.authority)
    except:
        authority = []
        
    try:
        kpi = json.loads(jd.kpi)
    except:
        kpi = []
        
    try:
        competencies = json.loads(jd.competencies)
    except:
        competencies = []
        
    return {
        "success": True,
        "data": {
            "id": jd.id,
            "ma_nv": jd.ma_nv,
            "chuc_danh": jd.chuc_danh,
            "objective": jd.objective,
            "responsibilities": responsibilities,
            "authority": authority,
            "kpi": kpi,
            "competencies": competencies,
            "reports_to": jd.reports_to
        },
        "employee": {
            "ma_nv": emp.ma_nv,
            "ten_nv": emp.ten_nv,
            "chuc_danh": emp_chuc_danh
        } if emp else None
    }

@router.post("/api/jds/generate")
def api_generate_jd_draft(request: Request, payload: dict, db: Session = Depends(get_db)):
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập!"}
        
    prompt = payload.get("prompt", "").strip()
    if not prompt:
        return {"success": False, "message": "Nội dung yêu cầu không được trống!"}
        
    try:
        draft = AIService.generate_jd(db, prompt)
        return {"success": True, "data": draft}
    except Exception as e:
        return {"success": False, "message": f"AI Generation Error: {str(e)}"}

@router.post("/api/jds")
def api_save_jd(request: Request, payload: dict, db: Session = Depends(get_db)):
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập!"}
    if session["role"] not in ["ADMIN", "CEO", "MANAGER"]:
        return {"success": False, "message": "Chỉ có Admin/CEO/Manager mới có quyền cập nhật Mô tả công việc!"}
        
    try:
        ma_nv = payload.get("ma_nv", "").strip().upper() or None
        chuc_danh = payload.get("chuc_danh", "").strip() or None
        
        if not ma_nv and not chuc_danh:
            return {"success": False, "message": "Vui lòng chọn nhân sự hoặc điền chức danh để lưu!"}
            
        # Check if record exists
        jd = None
        if ma_nv:
            jd = db.query(JobDescription).filter(JobDescription.ma_nv == ma_nv).first()
        elif chuc_danh:
            jd = db.query(JobDescription).filter(
                (JobDescription.chuc_danh == chuc_danh) & 
                ((JobDescription.ma_nv == None) | (JobDescription.ma_nv == ""))
            ).first()
            
        if not jd:
            jd = JobDescription(ma_nv=ma_nv, chuc_danh=chuc_danh)
            db.add(jd)
            
        jd.objective = payload.get("objective", "")
        jd.responsibilities = json.dumps(payload.get("responsibilities", []))
        jd.authority = json.dumps(payload.get("authority", []))
        jd.kpi = json.dumps(payload.get("kpi", []))
        jd.competencies = json.dumps(payload.get("competencies", []))
        jd.reports_to = payload.get("reports_to", "")
        
        db.commit()
        return {"success": True, "message": "✅ Lưu Mô tả công việc thành công!"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Lỗi lưu MTCV: {str(e)}"}

def set_cell_background(cell, fill_hex):
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shd)

@router.get("/api/jds/employee/{ma_nv}/export-word")
def api_export_jd_to_word(ma_nv: str, request: Request, db: Session = Depends(get_db)):
    """Exports employee job description (JD) into a styled, professional Word docx file."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
        
    ma_nv_upper = ma_nv.strip().upper()
    
    # 1. Fetch employee
    emp = db.query(Employee).filter(Employee.ma_nv == ma_nv_upper).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Nhân sự không tồn tại")
        
    # 2. Fetch Job Description
    jd = db.query(JobDescription).filter(JobDescription.ma_nv == ma_nv_upper).first()
    
    # Fallback title if JD not found or has no title
    emp_chuc_danh = emp.chuc_danh.strip() if emp.chuc_danh else (emp.chuc_vu.strip() if emp.chuc_vu else emp.ten_nv.strip())
    
    if not jd:
        raise HTTPException(status_code=404, detail="Bản mô tả công việc chưa được thiết lập")
        
    # Create docx Document
    doc = Document()
    
    # Document Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("BẢN MÔ TẢ CÔNG VIỆC")
    run_title.font.name = 'Arial'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(11, 37, 69) # Dark Navy
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_sub = p_sub.add_run(f"VỊ TRÍ: {(jd.chuc_danh or emp_chuc_danh).upper()}")
    run_sub.font.name = 'Arial'
    run_sub.font.size = Pt(13)
    run_sub.font.bold = True
    run_sub.font.color.rgb = RGBColor(11, 37, 69)
    
    # Spacing
    doc.add_paragraph()
    
    # Section: Meta Info (General Details Table)
    table_meta = doc.add_table(rows=4, cols=2)
    table_meta.style = 'Light Shading Accent 1'
    
    meta_headers = ["NHÂN SỰ THỰC HIỆN", "CHỨC DANH / VỊ TRÍ", "BÁO CÁO TRỰC TIẾP CHO", "MỤC TIÊU CÔNG VIỆC CHÍNH"]
    meta_values = [
        f"{emp.ten_nv} ({emp.ma_nv})",
        jd.chuc_danh or emp_chuc_danh,
        jd.reports_to or "N/A",
        jd.objective or "N/A"
    ]
    
    for i in range(4):
        row = table_meta.rows[i]
        
        cell_lbl = row.cells[0]
        cell_lbl.text = meta_headers[i]
        set_cell_background(cell_lbl, "EBF4F6")
        cell_lbl.paragraphs[0].runs[0].font.bold = True
        cell_lbl.paragraphs[0].runs[0].font.size = Pt(10)
        
        cell_val = row.cells[1]
        cell_val.text = meta_values[i]
        cell_val.paragraphs[0].runs[0].font.size = Pt(10)
        
    doc.add_paragraph()
    
    # Helper to write list sections
    def add_section_list(title_text, items_json_str):
        try:
            items = json.loads(items_json_str)
        except:
            items = []
            
        p_sec = doc.add_paragraph()
        run_sec = p_sec.add_run(title_text.upper())
        run_sec.font.bold = True
        run_sec.font.size = Pt(14)
        run_sec.font.color.rgb = RGBColor(11, 37, 69)
        
        if items:
            for item in items:
                p_item = doc.add_paragraph(style='List Bullet')
                run_item = p_item.add_run(item)
                run_item.font.size = Pt(10)
        else:
            p_none = doc.add_paragraph()
            run_none = p_none.add_run("Chưa có thông tin thiết lập.")
            run_none.font.size = Pt(10)
            run_none.font.italic = True
            
        doc.add_paragraph()
        
    add_section_list("1. Trách nhiệm & Nhiệm vụ chính", jd.responsibilities)
    add_section_list("2. Quyền hạn được giao", jd.authority)
    add_section_list("3. Chỉ số đo lường hiệu quả (KPIs)", jd.kpi)
    add_section_list("4. Khung năng lực & Yêu cầu kinh nghiệm", jd.competencies)
    
    # Save document to memory stream
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    
    encoded_filename = quote(f"JD_{emp.ten_nv}.docx")
    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"}
    )

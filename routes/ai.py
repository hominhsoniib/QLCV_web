from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from services.ai_service import AIService
from models.models import AIConfig
import markdown

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/ai-chat", response_class=HTMLResponse)
def get_ai_chat_page(request: Request):
    """Renders the AI assistant page. Requires login."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse(request, "ai_chat.html", {
        "user": session
    })

@router.post("/api/ai/chat")
def api_ai_chat(
    request: Request,
    payload: dict,
    db: Session = Depends(get_db)
):
    """Processes natural language chat query from user about their tasks."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
        
    query_text = payload.get("message", "").strip()
    if not query_text:
        return {"success": False, "message": "Nội dung câu hỏi không được trống."}
        
    try:
        response_md = AIService.ask_ai(db, session["ma"], session["role"], query_text)
        # Convert Markdown to HTML for nicer display
        response_html = markdown.markdown(response_md, extensions=['extra', 'tables'])
        return {
            "success": True,
            "response_md": response_md,
            "response_html": response_html
        }
    except Exception as e:
        return {"success": False, "message": f"Lỗi xử lý câu hỏi: {str(e)}"}

@router.get("/master/ai-config", response_class=HTMLResponse)
def get_ai_config_page(request: Request, db: Session = Depends(get_db)):
    """Renders the AI configuration management page. Requires admin/manager role."""
    session = AuthService.get_session(request)
    if not session:
        return RedirectResponse(url="/login")
    if session["role"] not in ["ADMIN", "CEO"]:
        return RedirectResponse(url="/dashboard")
        
    # Get current AI configuration or create a default one
    config = db.query(AIConfig).first()
    if not config:
        import os
        from config import Config
        config = AIConfig(
            provider="gemini",
            gemini_api_key=os.getenv("GEMINI_API_KEY") or getattr(Config, "GEMINI_API_KEY", ""),
            gemini_model="gemini-2.5-flash",
            claude_api_key=os.getenv("CLAUDE_API_KEY") or getattr(Config, "CLAUDE_API_KEY", ""),
            claude_model="claude-sonnet-5"
        )
        db.add(config)
        db.commit()
        db.refresh(config)
        
    return templates.TemplateResponse(request, "master/ai_config.html", {
        "user": session,
        "config": config
    })

@router.get("/api/ai-config")
def api_get_ai_config(request: Request, db: Session = Depends(get_db)):
    """API to fetch the current AI configuration."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
    if session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Không có quyền truy cập!"}
        
    config = db.query(AIConfig).first()
    if not config:
        return {"success": True, "data": None}
    return {
        "success": True,
        "data": {
            "provider": config.provider,
            "gemini_api_key": config.gemini_api_key,
            "gemini_model": config.gemini_model,
            "claude_api_key": config.claude_api_key,
            "claude_model": config.claude_model
        }
    }

@router.post("/api/ai-config")
def api_save_ai_config(request: Request, payload: dict, db: Session = Depends(get_db)):
    """API to save or update the AI configuration."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
    if session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Không có quyền truy cập!"}
        
    config = db.query(AIConfig).first()
    if not config:
        config = AIConfig()
        db.add(config)
        
    config.provider = payload.get("provider", "gemini")
    config.gemini_api_key = payload.get("gemini_api_key", "").strip()
    config.gemini_model = payload.get("gemini_model", "gemini-1.5-flash").strip()
    config.claude_api_key = payload.get("claude_api_key", "").strip()
    config.claude_model = payload.get("claude_model", "claude-3-5-sonnet-20241022").strip()
    
    try:
        db.commit()
        return {"success": True, "message": "✅ Lưu cấu hình AI thành công!"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": f"Lỗi lưu cấu hình: {str(e)}"}

@router.post("/api/ai-config/test")
def api_test_ai_config(request: Request, payload: dict):
    """API to test the connection to an AI provider with specified credentials."""
    session = AuthService.get_session(request)
    if not session:
        return {"success": False, "message": "🚨 Chưa đăng nhập!"}
    if session["role"] not in ["ADMIN", "CEO"]:
        return {"success": False, "message": "🚨 Không có quyền truy cập!"}
        
    provider = payload.get("provider")
    api_key = payload.get("api_key", "").strip()
    model = payload.get("model", "").strip()
    
    if not api_key:
        return {"success": False, "message": "Vui lòng nhập API Key trước khi kiểm thử!"}
        
    test_prompt = "Hãy trả lời từ 'OK' ngắn gọn nhất nếu bạn nhận được tin nhắn này."
    
    try:
        if provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            genai_model = genai.GenerativeModel(model or 'gemini-1.5-flash')
            response = genai_model.generate_content(test_prompt)
            if response and response.text:
                return {"success": True, "message": f"Kết nối Gemini thành công! Phản hồi: {response.text.strip()}"}
            else:
                return {"success": False, "message": "Không nhận được phản hồi từ Gemini."}
                
        elif provider == "claude":
            import urllib.request
            import json
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": model or "claude-3-5-sonnet-20241022",
                "max_tokens": 10,
                "messages": [
                    {"role": "user", "content": test_prompt}
                ]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                response_text = res_data["content"][0]["text"]
                return {"success": True, "message": f"Kết nối Claude thành công! Phản hồi: {response_text.strip()}"}
        else:
            return {"success": False, "message": "Provider không hợp lệ!"}
    except Exception as e:
        return {"success": False, "message": f"Lỗi kết nối: {str(e)}"}


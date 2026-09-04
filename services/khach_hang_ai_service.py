import os
import json
import httpx
from datetime import datetime
from config_khach_hang import Config, Tables, AI_CONFIG
import database.db_khach_hang as db
import services.khach_hang_auth as auth

def get_ai_provider() -> str:
    # Truy vấn bảng Config trong SQLite xem có override không
    cfg = db.find_by_id(Tables.CONFIG, "ai_provider")
    return cfg["value"] if cfg and cfg["value"] else AI_CONFIG["PROVIDER"]

def get_secret(key_name: str) -> str:
    # 1) Kiểm tra trong biến môi trường
    val = os.environ.get(key_name)
    if val:
        return val
    # 2) Kiểm tra trong bảng cấu hình DB
    cfg = db.find_by_id(Tables.CONFIG, key_name)
    if cfg:
        return cfg["value"]
    # 3) Kiểm tra trong bảng ai_configs của qlcv.db
    try:
        import sys
        if getattr(sys, 'frozen', False):
            qlcv_db_path = os.path.join(os.getcwd(), "qlcv.db")
        else:
            qlcv_db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "qlcv.db")
            
        if os.path.exists(qlcv_db_path):
            import sqlite3
            conn = sqlite3.connect(qlcv_db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT provider, gemini_api_key, claude_api_key FROM ai_configs LIMIT 1")
            row = cursor.fetchone()
            conn.close()
            if row:
                provider, gemini_key, claude_key = row
                if key_name == "CLAUDE_API_KEY" and claude_key:
                    return claude_key
                elif key_name == "GEMINI_API_KEY" and gemini_key:
                    return gemini_key
    except Exception as e:
        print(f"[CRM AI SECRET] Warning: Could not read qlcv.db: {e}")
    return ""

def llm(system: str, user: str) -> str:
    provider = get_ai_provider()
    if provider == "openai":
        return call_openai(system, user)
    return call_claude(system, user)

def call_claude(system: str, user: str) -> str:
    key = get_secret("CLAUDE_API_KEY")
    if not key:
        raise Exception("Chưa cấu hình CLAUDE_API_KEY. Hãy cấu hình biến môi trường hoặc chạy trong trang Cấu hình.")
        
    headers = {
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": AI_CONFIG["CLAUDE_MODEL"],
        "max_tokens": AI_CONFIG["MAX_TOKENS"],
        "system": system,
        "messages": [{"role": "user", "content": user}]
    }
    
    with httpx.Client() as client:
        res = client.post(AI_CONFIG["CLAUDE_URL"], headers=headers, json=payload, timeout=30.0)
        
    if res.status_code >= 300:
        try:
            data = res.json()
            err_msg = data.get("error", {}).get("message", res.text)
        except Exception:
            err_msg = res.text
        raise Exception(f"Claude API Error: {err_msg}")
        
    data = res.json()
    content = data.get("content", [])
    return "".join([b.get("text", "") for b in content]).strip()

def call_openai(system: str, user: str) -> str:
    key = get_secret("OPENAI_API_KEY")
    if not key:
        raise Exception("Chưa cấu hình OPENAI_API_KEY. Hãy cấu hình biến môi trường hoặc chạy trong trang Cấu hình.")
        
    headers = {
        "Authorization": f"Bearer {key}",
        "content-type": "application/json"
    }
    payload = {
        "model": AI_CONFIG["OPENAI_MODEL"],
        "max_tokens": AI_CONFIG["MAX_TOKENS"],
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user}
        ]
    }
    
    with httpx.Client() as client:
        res = client.post(AI_CONFIG["OPENAI_URL"], headers=headers, json=payload, timeout=30.0)
        
    if res.status_code >= 300:
        try:
            data = res.json()
            err_msg = data.get("error", {}).get("message", res.text)
        except Exception:
            err_msg = res.text
        raise Exception(f"OpenAI API Error: {err_msg}")
        
    data = res.json()
    return data["choices"][0]["message"]["content"].strip()

def build_context(customer_id: str) -> tuple[dict, str]:
    c = db.find_by_id(Tables.CUSTOMERS, customer_id)
    if not c:
        raise Exception("Không tìm thấy khách hàng.")
        
    all_care = db.read_all(Tables.CARE)
    care = [r for r in all_care if r["customerId"] == customer_id]
    care.sort(key=lambda x: str(x["date"]))
    
    all_deals = db.read_all(Tables.DEALS)
    deals = [d for d in all_deals if d["customerId"] == customer_id]
    
    ctx = "KHÁCH HÀNG:\n"
    ctx += f"- Tên: {c['name']}\n- Nguồn: {c['source']}\n- Trạng thái: {c['status']}\n"
    ctx += f"- Tag hiện tại: {c['tags'] or 'chưa có'}\n"
    ctx += "\nDEALS:\n"
    if deals:
        ctx += "\n".join([f"- {d['title']} | {d['stage']} | {d['value']}đ" for d in deals])
    else:
        ctx += "- (chưa có deal)"
    ctx += f"\n\nLỊCH SỬ CHĂM SÓC ({len(care)} lần):\n"
    if care:
        ctx += "\n".join([f"- [{str(r['date'])[:10]}] {r['content']}" + (f" → {r['result']}" if r['result'] else "") for r in care])
    else:
        ctx += "- (chưa có lịch sử)"
        
    return c, ctx

def log_ai(customer_id: str, feature: str, prompt: str, result: str, user: str):
    try:
        db.insert(Tables.AILOG, {
            "id": auth.gen_id("AI"),
            "customerId": customer_id,
            "feature": feature,
            "model": get_ai_provider(),
            "prompt": str(prompt)[:500],
            "result": str(result)[:2000],
            "user": user,
            "createdAt": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"aiLog_ fail: {e}")

# API Endpoints implementation
def api_ai_suggest(token: str, customer_id: str) -> dict:
    try:
        me = auth.guard(token, "ai.suggest")
        c, ctx_text = build_context(customer_id)
        system_prompt = (
            "Bạn là chuyên gia CSKH/Sales B2C tại Việt Nam. Dựa trên hồ sơ và lịch sử, "
            "đề xuất kịch bản chăm sóc TIẾP THEO ngắn gọn, thực tế, bằng tiếng Việt. "
            "Trả về: (1) Mục tiêu lần liên hệ tới, (2) 3 ý chính nên nói, (3) 1 tin nhắn mẫu có thể gửi ngay."
        )
        out = llm(system_prompt, ctx_text)
        log_ai(customer_id, "suggest", ctx_text, out, me["email"])
        return {"ok": True, "data": out}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def api_ai_score(token: str, customer_id: str) -> dict:
    try:
        me = auth.guard(token, "ai.score")
        c, ctx_text = build_context(customer_id)
        system_prompt = (
            "Bạn là hệ thống chấm điểm tiềm năng khách hàng (lead scoring). "
            "Dựa trên mức độ tương tác, trạng thái, giá trị deal, hãy chấm điểm 0-100. "
            "TRẢ VỀ DUY NHẤT JSON: {\"score\": <số 0-100>, \"reason\": \"<1 câu lý do tiếng Việt>\"} không thêm chữ nào khác."
        )
        raw = llm(system_prompt, ctx_text)
        
        # Parse JSON output
        try:
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(cleaned)
        except Exception:
            parsed = {"score": 0, "reason": raw[:200]}
            
        score = max(0, min(100, int(parsed.get("score", 0))))
        db.update_by_id(Tables.CUSTOMERS, customer_id, {"score": str(score), "updatedAt": datetime.now().isoformat()})
        
        log_ai(customer_id, "score", ctx_text, raw, me["email"])
        return {"ok": True, "data": {"score": score, "reason": parsed.get("reason", "")}}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def api_ai_autotag(token: str, customer_id: str) -> dict:
    try:
        me = auth.guard(token, "ai.tag")
        c, ctx_text = build_context(customer_id)
        system_prompt = (
            "Phân tích khách hàng và sinh 2-4 tag ngắn gọn (tiếng Việt, mỗi tag 1-2 từ) "
            "mô tả đặc điểm/giai đoạn/độ ưu tiên. TRẢ VỀ DUY NHẤT JSON mảng chuỗi, vd [\"VIP\",\"Quan tâm cao\"] không thêm chữ nào."
        )
        raw = llm(system_prompt, ctx_text)
        
        try:
            cleaned = raw.replace("```json", "").replace("```", "").strip()
            tags = json.loads(cleaned)
        except Exception:
            tags = [t.strip() for t in raw.split(",") if t.strip()][:4]
            
        if not isinstance(tags, list):
            tags = []
            
        tag_str = ", ".join([str(t).replace("[", "").replace("]", "").replace('"', '').strip() for t in tags if str(t).strip()])
        db.update_by_id(Tables.CUSTOMERS, customer_id, {"tags": tag_str, "updatedAt": datetime.now().isoformat()})
        
        log_ai(customer_id, "tag", ctx_text, raw, me["email"])
        return {"ok": True, "data": {"tags": tag_str}}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def api_ai_summary(token: str, customer_id: str) -> dict:
    try:
        me = auth.guard(token, "ai.summary")
        c, ctx_text = build_context(customer_id)
        system_prompt = (
            "Tóm tắt hành trình khách hàng này bằng tiếng Việt trong 4-6 câu: "
            "họ là ai, đã tương tác gì, đang ở giai đoạn nào, điểm cần lưu ý. Văn phong gọn, chuyên nghiệp."
        )
        out = llm(system_prompt, ctx_text)
        log_ai(customer_id, "summary", ctx_text, out, me["email"])
        return {"ok": True, "data": out}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def api_ai_status(token: str) -> dict:
    try:
        auth.guard(token, "ai.suggest")
        p = get_ai_provider()
        key = get_secret("OPENAI_API_KEY") if p == "openai" else get_secret("CLAUDE_API_KEY")
        return {"ok": True, "data": {"provider": p, "configured": bool(key)}}
    except Exception as e:
        return {"ok": False, "error": str(e)}

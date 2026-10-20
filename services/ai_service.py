import os
import datetime
from sqlalchemy.orm import Session
from models.models import Task, Employee, AIConfig
from config import Config

class AIService:
    @staticmethod
    def get_user_tasks(db: Session, ma_nv: str, role: str):
        """Gets tasks relevant to the user, similar to TaskService.get_index_init_data."""
        ma_nv_upper = str(ma_nv or "").strip().upper()
        is_super_admin = (ma_nv_upper == "ADMIN")
        
        query = db.query(Task)
        if not is_super_admin:
            query = query.filter(
                (Task.nguoi_giao == ma_nv_upper) | 
                (Task.nguoi_nhan == ma_nv_upper)
            )
        if ma_nv_upper == "CEO":
            from services.task_policy import TaskActor, can_view_task
            return [t for t in db.query(Task).all()
                    if can_view_task(TaskActor("CEO", role == "ADMIN"), t)]
        return query.all()

    @staticmethod
    def run_fallback_ai(query_text: str, tasks: list, ma_nv: str, ten_nv: str) -> str:
        """Rule-based Vietnamese NLP fallback parser to query tasks."""
        query_lower = query_text.lower()
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        # Determine filter criteria
        filter_incomplete = False
        filter_urgent = False
        filter_overdue = False
        filter_complete = False
        
        # Check keywords
        if any(w in query_lower for w in ["chưa hoàn thành", "chưa xong", "chua hoan thanh", "chua xong", "đang làm", "dang lam"]):
            filter_incomplete = True
        if any(w in query_lower for w in ["gấp", "khẩn", "ngay lập tức", "uu tien", "ưu tiên", "giai quyet gap", "giải quyết gấp"]):
            filter_urgent = True
        if any(w in query_lower for w in ["trễ hạn", "quá hạn", "tre han", "qua han", "trễ", "muộn"]):
            filter_overdue = True
        if any(w in query_lower for w in ["đã hoàn thành", "đã xong", "da hoan thanh", "hoàn thành", "hoan thanh"]):
            filter_complete = True
            
        # Default to incomplete if they ask about "giải quyết gấp" or similar but didn't specify complete
        if filter_urgent and not filter_complete:
            filter_incomplete = True
            
        print(f"[DEBUG] query_text={repr(query_text)}")
        print(f"[DEBUG] filters: incomplete={filter_incomplete}, urgent={filter_urgent}, overdue={filter_overdue}, complete={filter_complete}")
        print(f"[DEBUG] tasks len={len(tasks)}")
        
        filtered_tasks = []
        for t in tasks:
            match = True
            
            # Progress status
            progress = t.phan_tram_ht or 0
            is_done = progress >= 100 or t.tinh_trang == "Hoàn thành"
            
            if filter_incomplete and is_done:
                match = False
            if filter_complete and not is_done:
                match = False
                
            # Overdue status
            is_overdue = False
            if t.ngay_kt:
                # Compare YYYY-MM-DD
                is_overdue = t.ngay_kt < today_str and not is_done
            
            if filter_overdue and not is_overdue:
                match = False
                
            # Urgent status (deadline close, overdue, or has "gấp" keyword in title/desc)
            is_urgent = False
            if not is_done:
                title_lower = (t.ten_cv or "").lower()
                has_gap_kw = any(w in title_lower for w in ["gấp", "khẩn", "hỏa tốc", "quan trọng", "urg", "gap", "khan"])
                is_near_deadline = False
                if t.ngay_kt:
                    try:
                        due_date = datetime.datetime.strptime(t.ngay_kt, "%Y-%m-%d").date()
                        days_left = (due_date - datetime.date.today()).days
                        is_near_deadline = 0 <= days_left <= 3
                    except:
                        pass
                is_urgent = has_gap_kw or is_overdue or is_near_deadline
                
            if filter_urgent and not is_urgent:
                match = False
                
            if match:
                filtered_tasks.append((t, is_overdue, is_urgent))
                
        # Generate markdown response
        if not filtered_tasks:
            return f"Chào **{ten_nv}** ({ma_nv}), tôi không tìm thấy công việc nào khớp với yêu cầu của bạn."
            
        response = f"Chào **{ten_nv}** ({ma_nv}), dưới đây là danh sách công việc phù hợp với câu hỏi của bạn:\n\n"
        response += "| Mã CV | Tên Công Việc | Người Giao | Hạn Hoàn Thành | Tiến Độ | Trạng Thái | Ghi Chú |\n"
        response += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
        for t, is_overdue, is_urgent in filtered_tasks:
            # Format status badge
            status_text = t.tinh_trang or "Chưa rõ"
            progress_text = f"{t.phan_tram_ht or 0}%"
            
            note = ""
            if is_overdue:
                note += "⚠️ **QUÁ HẠN** "
            if is_urgent:
                note += "🔥 **GẤP**"
                
            response += f"| `{t.ma_cv}` | {t.ten_cv} | {t.nguoi_giao} | {t.ngay_kt or 'N/A'} | {progress_text} | {status_text} | {note} |\n"
            
        response += f"\n*Tổng số công việc tìm thấy: {len(filtered_tasks)}*"
        return response

    @staticmethod
    def ask_ai(db: Session, ma_nv: str, role: str, query_text: str) -> str:
        # Fetch employee details
        emp = db.query(Employee).filter(Employee.ma_nv == ma_nv).first()
        ten_nv = emp.ten_nv if emp else ma_nv
        chuc_vu = emp.chuc_vu if emp else "Nhân viên"
        
        # Get tasks
        tasks = AIService.get_user_tasks(db, ma_nv, role)
        
        # Fetch AI configuration from database
        config = db.query(AIConfig).first()
        if not config:
            config = AIConfig(
                provider="gemini",
                gemini_api_key=os.getenv("GEMINI_API_KEY") or getattr(Config, "GEMINI_API_KEY", ""),
                gemini_model="gemini-3.5-flash",
                claude_api_key=os.getenv("CLAUDE_API_KEY") or getattr(Config, "CLAUDE_API_KEY", ""),
                claude_model="claude-sonnet-5"
            )
            db.add(config)
            try:
                db.commit()
                db.refresh(config)
            except Exception as e:
                db.rollback()
                print("Failed to auto-create AIConfig on query:", e)
                
        # Format task list for prompt
        task_data = []
        for t in tasks:
            task_data.append({
                "ma_cv": t.ma_cv,
                "ten_cv": t.ten_cv,
                "nguoi_giao": t.nguoi_giao,
                "nguoi_nhan": t.nguoi_nhan,
                "ngay_bd": t.ngay_bd,
                "ngay_kt": t.ngay_kt,
                "tiendo_phantram": t.phan_tram_ht or 0,
                "tinh_trang": t.tinh_trang,
                "nhac_nho": t.noi_dung_nhac_nho,
                "so_lan_nhac": t.so_lan_nhac
            })
        
        system_prompt = (
            "Bạn là trợ lý ảo AI chuyên nghiệp của hệ thống AMS PRO 5.0 (Quản Lý Công Việc).\n"
            f"Người dùng hiện tại: {ten_nv} (Mã số: {ma_nv}, Chức vụ: {chuc_vu}, Vai trò hệ thống: {role}).\n"
            "Dưới đây là danh sách công việc liên quan đến người dùng này trong hệ thống:\n"
            f"{task_data}\n\n"
            "Hãy trả lời câu hỏi của người dùng một cách chính xác, lịch sự bằng tiếng Việt.\n"
            "Dựa vào ngày hiện tại là: " + datetime.date.today().strftime("%Y-%m-%d") + ".\n"
            "Phân tích đúng các công việc chưa hoàn thành (tiến độ < 100%), quá hạn (hạn kết thúc đã qua), hoặc việc gấp (có ghi chú gấp/hỏa tốc, hoặc trễ hạn cần làm ngay).\n"
            "Hãy trình bày câu trả lời rõ ràng dưới dạng Markdown, có thể sử dụng bảng (table) hoặc danh sách nếu có nhiều công việc."
        )

        provider = config.provider if config else "gemini"
        
        if provider == "gemini":
            api_key = config.gemini_api_key if config else None
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY") or getattr(Config, "GEMINI_API_KEY", None)
            
            if api_key:
                try:
                    proxy_url = getattr(config, "gemini_proxy_url", None)
                    model_name = (config.gemini_model if config and config.gemini_model else 'gemini-2.0-flash').strip()
                    return AIService.call_gemini_api(
                        api_key=api_key,
                        model_name=model_name,
                        contents=[system_prompt, query_text],
                        proxy_url=proxy_url
                    )
                except Exception as e:
                    print("[AI_SERVICE] Gemini API error:", e)
                    return AIService.run_fallback_ai(query_text, tasks, ma_nv, ten_nv)
            else:
                return AIService.run_fallback_ai(query_text, tasks, ma_nv, ten_nv)
                
        elif provider == "claude":
            api_key = config.claude_api_key if config else None
            if not api_key:
                api_key = os.getenv("CLAUDE_API_KEY") or getattr(Config, "CLAUDE_API_KEY", None)
                
            if api_key:
                try:
                    import urllib.request
                    import json
                    url = "https://api.anthropic.com/v1/messages"
                    headers = {
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    }
                    model_name = config.claude_model if config else 'claude-3-5-sonnet-20241022'
                    data = {
                        "model": model_name,
                        "max_tokens": 4096,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": query_text}
                        ]
                    }
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(data).encode("utf-8"),
                        headers=headers,
                        method="POST"
                    )
                    with urllib.request.urlopen(req, timeout=30) as response:
                        res_data = json.loads(response.read().decode("utf-8"))
                        return res_data["content"][0]["text"]
                except Exception as e:
                    print("[AI_SERVICE] Claude API error:", e)
                    return AIService.run_fallback_ai(query_text, tasks, ma_nv, ten_nv)
            else:
                return AIService.run_fallback_ai(query_text, tasks, ma_nv, ten_nv)
                
        else:
            # Fallback when AI provider is set to 'none' (disabled)
            return AIService.run_fallback_ai(query_text, tasks, ma_nv, ten_nv)

    @staticmethod
    def call_gemini_api(api_key: str, model_name: str, contents: list, proxy_url: str = None, response_mime_type: str = None, timeout: int = 40) -> str:
        """Call Gemini REST API directly or through a reverse proxy (e.g. Cloudflare Worker)."""
        import urllib.request
        import urllib.error
        import json
        
        base = (proxy_url or "").strip().rstrip("/") or "https://generativelanguage.googleapis.com"
        if not base.startswith("http"):
            base = "https://" + base
            
        clean_model = (model_name or "gemini-3.5-flash").strip()
        
        # Build candidate models to try: selected model first, then ultra-stable fallbacks
        models_to_try = [clean_model]
        for fallback in ["gemini-3.5-flash", "gemini-2.5-flash-lite", "gemini-3.5-flash-lite", "gemini-2.5-flash"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)
                
        last_error = None
        for current_model in models_to_try:
            url = f"{base}/v1beta/models/{current_model}:generateContent?key={api_key}"
            
            parts = []
            for item in contents:
                if isinstance(item, str) and item:
                    parts.append({"text": item})
                elif isinstance(item, dict):
                    parts.append(item)
                    
            payload = {
                "contents": [{"parts": parts}]
            }
            if response_mime_type:
                payload["generationConfig"] = {"responseMimeType": response_mime_type}
                
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=timeout) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    candidates = res_data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts_resp = candidates[0]["content"].get("parts", [])
                        if parts_resp and "text" in parts_resp[0]:
                            return parts_resp[0]["text"]
                    raise Exception("Không nhận được nội dung từ Gemini API. Phản hồi: " + json.dumps(res_data))
            except urllib.error.HTTPError as err:
                err_msg = str(err)
                try:
                    err_body = json.loads(err.read().decode("utf-8"))
                    api_msg = err_body.get("error", {}).get("message")
                    if api_msg:
                        err_msg = f"{err.code} {api_msg}"
                except Exception:
                    pass
                last_error = err_msg
                # If Google returns 400 (location/capability error), 429 (quota exceeded), 503 (high demand) or 404 (model not found), try next fallback model
                if err.code in (400, 404, 429, 503):
                    print(f"[AI_SERVICE] Model {current_model} returned {err.code} ({err_msg}), falling back to next candidate model...")
                    continue
                else:
                    raise Exception(f"Lỗi kết nối Gemini: {err_msg}")
            except Exception as e:
                last_error = str(e)
                continue
                
        raise Exception(f"Lỗi kết nối Gemini: {last_error}")

    @staticmethod
    def call_ai_structured(db: Session, prompt: str, system_prompt: str) -> str:
        """Call the active AI provider to generate structured JSON text."""
        config = db.query(AIConfig).first()
        provider = config.provider if config else "gemini"
        
        # Ensure we request JSON in prompt with strict guidelines
        full_system_prompt = system_prompt + (
            "\nBắt buộc trả về kết quả CHỈ là chuỗi JSON hợp lệ, không bao gồm các ký tự đánh dấu markdown như ```json hay bất kỳ chữ giải thích nào bên ngoài.\n"
            "CHÚ Ý QUAN TRỌNG VỀ ĐỊNH DẠNG JSON:\n"
            "1. Tuyệt đối KHÔNG dùng dấu ngoặc kép kép trần (\") bên trong các chuỗi giá trị. Nếu cần viết dấu ngoặc kép, hãy dùng dấu ngoặc đơn (') hoặc escape nó thành (\\\").\n"
            "2. Không được chứa ký tự xuống dòng thực tế trần bên trong chuỗi giá trị JSON, hãy dùng ký tự escape '\\n' để thay thế.\n"
            "3. Hãy đóng tất cả dấu ngoặc nhọn, ngoặc vuông và dấu phẩy ngăn cách tuyệt đối chính xác."
        )
        
        if provider == "gemini":
            api_key = config.gemini_api_key if config else None
            if not api_key:
                api_key = os.getenv("GEMINI_API_KEY") or getattr(Config, "GEMINI_API_KEY", None)
            if not api_key:
                raise Exception("Chưa cấu hình GEMINI_API_KEY!")
                
            proxy_url = getattr(config, "gemini_proxy_url", None)
            model_name = (config.gemini_model if config and config.gemini_model else 'gemini-2.0-flash').strip()
            
            return AIService.call_gemini_api(
                api_key=api_key,
                model_name=model_name,
                contents=[full_system_prompt, prompt],
                proxy_url=proxy_url,
                response_mime_type="application/json"
            )
            
        elif provider == "claude":
            api_key = config.claude_api_key if config else None
            if not api_key:
                api_key = os.getenv("CLAUDE_API_KEY") or getattr(Config, "CLAUDE_API_KEY", None)
            if not api_key:
                raise Exception("Chưa cấu hình CLAUDE_API_KEY!")
                
            import urllib.request
            import json
            url = "https://api.anthropic.com/v1/messages"
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            model_name = config.claude_model if config else 'claude-sonnet-5'
            data = {
                "model": model_name,
                "max_tokens": 4000,
                "system": full_system_prompt,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=40) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                return res_data["content"][0]["text"]
        else:
            raise Exception("AI Provider đang bị tắt. Hãy bật AI trong phần Cấu hình AI Claude & Gemini.")

    @staticmethod
    def generate_process(db: Session, prompt: str) -> dict:
        system_prompt = (
            "Bạn là một chuyên gia ISO 9001 và Tư vấn quản trị vận hành doanh nghiệp.\n"
            "Hãy phân tích yêu cầu viết quy trình và xuất ra cấu trúc JSON sau:\n"
            "{\n"
            "  \"process_name\": \"Tên quy trình (viết hoa, ngắn gọn, tiếng Việt, VD: QUY TRÌNH THI CÔNG CÔNG TRÌNH)\",\n"
            "  \"objective\": \"Mục tiêu quy trình\",\n"
            "  \"scope\": \"Phạm vi áp dụng\",\n"
            "  \"steps\": [\n"
            "    {\n"
            "      \"step_no\": 1,\n"
            "      \"name\": \"Tên bước\",\n"
            "      \"owner\": \"Chức danh người phụ trách (VD: Giám đốc dự án, Chỉ huy trưởng công trình, Kế toán...)\",\n"
            "      \"input\": \"Đầu vào bước\",\n"
            "      \"output\": \"Đầu ra bước\",\n"
            "      \"template_form\": \"Mẫu biểu / Biểu mẫu / Văn bản hồ sơ đính kèm bắt buộc cho bước này theo chuẩn ISO (Ví dụ: Quyết định bổ nhiệm Chỉ huy trưởng công trình, Biên bản nghiệm thu bàn giao, Phiếu yêu cầu cấp vật tư, Kế hoạch thi công chi tiết... Nếu không có mẫu biểu thì ghi '---')\",\n"
            "      \"sla\": \"Thời gian SLA hoàn thành định mức (VD: 2 giờ, 1 ngày, 3 ngày làm việc...)\"\n"
            "    }\n"
            "  ],\n"
            "  \"flowchart_mermaid\": \"Mã vẽ sơ đồ Mermaid.js dạng graph TD trực quan thể hiện luồng các bước trên. QUY TẮC CÚ PHÁP BẮT BUỘC: 1. Bắt đầu bằng 'graph TD'. 2. Nhãn node PHẢI bọc trong dấu ngoặc kép bên trong ngoặc vuông, VD: A[\\\"Yêu cầu\\\"] --> B[\\\"Duyệt\\\"]. 3. Điều kiện rẽ nhánh dùng ngoặc nhọn có nháy kép C{\\\"Hợp lệ?\\\"} và mũi tên C -->|Đồng ý| D. 4. Tuyệt đối không được có ký tự xuống dòng bên trong nhãn node.\",\n"
            "  \"checklist\": [\"Công việc kiểm tra 1\", \"Công việc kiểm tra 2\"],\n"
            "  \"kpi_suggestions\": [\"KPI đo lường hiệu quả quy trình 1\", \"KPI đo lường hiệu quả quy trình 2\"]\n"
            "}\n"
            "LƯU Ý ĐẶC BIỆT: Bắt buộc mỗi bước (steps) phải điền rõ trường 'template_form' với tên mẫu biểu hoặc văn bản, quyết định, biên bản pháp lý/hành chính/kỹ thuật tương ứng của bước đó."
        )
        raw_json = AIService.call_ai_structured(db, f"Hãy viết quy trình chi tiết cho: {prompt}", system_prompt)
        return AIService.clean_and_parse_json(raw_json)

    @staticmethod
    def generate_department_functions(db: Session, prompt: str) -> dict:
        system_prompt = (
            "Bạn là một chuyên gia Tư vấn tổ chức nhân sự doanh nghiệp.\n"
            "Hãy phân tích tên phòng ban/bộ phận và xuất ra cấu trúc chức năng nhiệm vụ dạng JSON sau:\n"
            "{\n"
            "  \"name\": \"Tên phòng ban/bộ phận\",\n"
            "  \"function\": \"Chức năng cốt lõi chính của bộ phận này\",\n"
            "  \"responsibilities\": [\"Nhiệm vụ cụ thể 1\", \"Nhiệm vụ cụ thể 2\", \"Nhiệm vụ cụ thể 3...\"],\n"
            "  \"kpi_main\": [\"KPI chính đo lường hiệu quả hoạt động phòng ban 1\", \"KPI chính 2...\"],\n"
            "  \"kpi_secondary\": [\"KPI phụ đo lường phòng ban 1\", \"KPI phụ 2...\"]\n"
            "}"
        )
        raw_json = AIService.call_ai_structured(db, f"Hãy mô tả chức năng nhiệm vụ cho bộ phận: {prompt}", system_prompt)
        return AIService.clean_and_parse_json(raw_json)

    @staticmethod
    def generate_jd(db: Session, prompt: str) -> dict:
        system_prompt = (
            "Bạn là một chuyên gia nhân sự và xây dựng khung năng lực cấp cao (Senior HR Specialist & Competency Framework Architect).\n"
            "Nhiệm vụ của bạn là phân tích chức danh/vị trí công việc và đặc biệt lưu ý định hướng, mô tả đặc thù chuyên môn hoặc ngành nghề mà người dùng cung cấp để xây dựng bản mô tả công việc (JD) chính xác tuyệt đối, tránh nhầm lẫn giữa các ngành nghề khác nhau (Ví dụ: 'Nhân viên thiết kế' nếu có ghi chú về công trình/thi công/dự toán thì TUYỆT ĐỐI KHÔNG viết về thiết kế đồ họa hay nhãn mác bao bì mà phải viết chuẩn về thiết kế kỹ thuật công trình, hồ sơ thiết kế thi công, bóc tách khối lượng và lập dự toán xây dựng).\n\n"
            "Hãy xuất ra bản mô tả công việc (JD) dạng JSON sau (không kèm lời dẫn ngoài JSON):\n"
            "{\n"
            "  \"position_title\": \"Tên chức danh/vị trí chuẩn xác\",\n"
            "  \"objective\": \"Mục tiêu công việc chính (gắn liền với lĩnh vực chuyên môn được chỉ định)\",\n"
            "  \"responsibilities\": [\"Trách nhiệm/Nhiệm vụ chính 1 (chi tiết, chuyên nghiệp theo đúng định hướng ngành nghề)\", \"Trách nhiệm/Nhiệm vụ chính 2...\"],\n"
            "  \"authority\": [\"Quyền hạn vị trí này được phép thực hiện 1\", \"Quyền hạn 2...\"],\n"
            "  \"kpi\": [\"Chỉ số đánh giá hiệu quả KPI chính của vị trí này 1\", \"KPI 2...\"],\n"
            "  \"competencies\": [\"Năng lực chuyên môn/Kỹ năng/Phần mềm bắt buộc (VD: AutoCAD, Revit, Dự toán GXD, Sketchup, hoặc phần mềm chuyên ngành tương ứng) 1\", \"Yêu cầu năng lực 2...\"],\n"
            "  \"reports_to\": \"Chức danh cấp trên trực tiếp quản lý vị trí này (VD: Trưởng phòng Kỹ thuật, Chỉ huy trưởng, Giám đốc Dự án, v.v.)\"\n"
            "}"
        )
        raw_json = AIService.call_ai_structured(db, f"Hãy viết bản mô tả công việc (JD) chi tiết cho: {prompt}", system_prompt)
        return AIService.clean_and_parse_json(raw_json)

    @staticmethod
    def clean_and_parse_json(text: str) -> dict:
        import json
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        # Look for JSON boundaries
        start = text.find("{")
        end = text.rfind("}")
        json_candidate = text
        if start != -1 and end != -1:
            json_candidate = text[start:end+1]
            
        try:
            return json.loads(json_candidate)
        except Exception as first_err:
            try:
                parts = json_candidate.split('"')
                for i in range(1, len(parts), 2):
                    # Replace actual literal newlines inside string values
                    parts[i] = parts[i].replace('\n', '\\n').replace('\r', '\\r')
                cleaned = '"'.join(parts)
                return json.loads(cleaned)
            except Exception as second_err:
                raise Exception(
                    f"Lỗi phân tích JSON từ AI: {str(first_err)}\n"
                    f"Cố gắng sửa lỗi tự động thất bại: {str(second_err)}\n"
                    f"Nội dung AI trả về: {text}"
                )


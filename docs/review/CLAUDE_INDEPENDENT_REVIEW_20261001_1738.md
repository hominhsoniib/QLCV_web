# CLAUDE INDEPENDENT REVIEW — PHẦN 2: các vùng CHƯA ai audit

Reviewer: Claude (independent security reviewer — chỉ kiểm chứng, không sửa code/test/log).
Báo cáo này tự chứa evidence; mọi trích dẫn có số dòng, dữ liệu nhạy cảm không được in.
Phần 1 (`docs/review/CLAUDE_INDEPENDENT_REVIEW_20261001_1708.md`, 850 dòng) đã kiểm chứng
Batch 3D/4B1–4B5, replacement invariant, gateway, SW logic, provenance, test integrity, fresh run 2396/2,
SEC-01/SEC-05, NEW-01..NEW-06. Phần này chỉ tham chiếu các ID đó, **không phân tích lại**.
Trọng tâm: SEC-06/07, SEC-02 (chuỗi tấn công kết hợp), HARD-01 XSS, các module chưa xem, BUG-02/04..07/09,
mobile ngoài SW, deployment, và hướng sửa NEW-03.

---

## 0. Metadata

| Mục | Giá trị |
|---|---|
| Thời gian review | 2026-10-01 17:20 → 17:38 (Asia/Ho_Chi_Minh) |
| Branch | `security/codex-batches-20261001` |
| Git HEAD | `66fa8a8f93d8b8dbebc686716664890f73f28521` ("docs: mobile app guide, Windows port helper, original Codex audit prompt") |
| `git diff HEAD` trên file code (.py/.html/.js/.conf) | **KHÔNG CÓ** (diff rỗng) → điều kiện STOP không kích hoạt |
| Tracked-modified | 0 (working tree khớp HEAD, trừ CRLF do `core.autocrlf=true`) |
| Untracked | 8 entry (các file `cleanup_*`, `ket_qua_don_rac_dot1.md` của tiến trình dọn rác khác — không thuộc review) |
| Nguồn đọc file log/checklist | đọc từ **working tree** = khớp byte với HEAD (đã đối chiếu: working tree so manifest = 0 mismatch); các file này không đổi so HEAD |
| Fresh run tham chiếu (phần 1) | `.test_runtime/run-7b9d17133d294f419996f96d9bdc1576/` — KHÔNG chạy lại trong phần này |
| CODEX_AUDIT_FIX_LOG.md @HEAD | 2089 dòng, sha256 `30abd7b2fce9287e…` |
| audit_codex_v4.md @HEAD | 285 dòng, `1b7816642511f8cc…` |

Lưu ý phương pháp: HEAD lưu blob theo LF, working tree là CRLF (autocrlf), nên `git show HEAD:<file>` khác hash
working tree ở 12 file. Khi so **bytes working tree** với `source_manifest.json` của fresh run: **0 mismatch** cho cả 34
file Core → source đang review đúng là source đã test. Không chạy guarded runner trong phần này (không có finding P0/P1
nào cần runtime để xác nhận; tất cả xác minh được bằng đọc code).

---

## 1. Summary JSON

```json
{
  "review_decision": "INCOMPLETE",
  "scope": "unaudited-areas: SEC-06, SEC-07, SEC-02-chains, HARD-01-XSS, modules, BUG-02/04-07/09, mobile, deployment",
  "critical_rejection_found": false,
  "code_changed_vs_HEAD": false,
  "fresh_run": {"reused_from_part1": true, "run_dir": ".test_runtime/run-7b9d17133d294f419996f96d9bdc1576", "pass": 2396, "fail": 2},
  "production_integrity_unchanged": true,
  "findings_confirmed": {
    "SEC-06": "OPEN-CONFIRMED",
    "SEC-07": "OPEN-CONFIRMED",
    "SEC-02": "OPEN-CONFIRMED",
    "HARD-01": "OPEN-CONFIRMED",
    "HARD-02": "OPEN-CONFIRMED",
    "HARD-05": "OPEN-CONFIRMED",
    "BUG-01": "OPEN-CONFIRMED",
    "BUG-02": "OPEN-CONFIRMED",
    "BUG-03": "OPEN-CONFIRMED",
    "BUG-08": "PARTIALLY-FIXED (list fixed, dashboard/mobile not)",
    "BUG-09": "DISAGREE-LIKELY-FIXED"
  },
  "new_findings": [
    {"id": "NEW-07", "severity": "P1", "title": "Toàn bộ /api/personal/* không cô lập tenant: user_id là mã NV, trùng mã giữa các công ty → đọc/sửa/xóa dữ liệu cá nhân xuyên tenant"},
    {"id": "NEW-08", "severity": "P1", "title": "Chuỗi SEC-02 + SEC-01 + NEW-02: cookie sao chép/không hết hạn + switch-tenant ký ma=ADMIN → đặt lại tài khoản MASTER"},
    {"id": "NEW-09", "severity": "P2", "title": "HARD-01 XSS được xác nhận: innerHTML dựng từ dữ liệu người dùng không escape ở tasks/index, documents, processes, master/*, personal; mermaid securityLevel:'loose'; AI Markdown render thô"},
    {"id": "NEW-10", "severity": "P2", "title": "SEC-07: login dùng prefix match email (LIKE 'x%') + fallback tách @ + first-match, có thể xác thực sai danh tính khi mã NV/email trùng tiền tố"},
    {"id": "NEW-11", "severity": "P2", "title": "Công ty INACTIVE vẫn đăng nhập được: check_login không kiểm tra MasterCompany.status (chỉ kiểm expiry_date)"},
    {"id": "NEW-12", "severity": "P2", "title": "templates/mobile/crm.html còn trong repo; mobile menu không link nhưng cần xác nhận không route nào render (hiện KHÔNG có route mobile CRM)"},
    {"id": "NEW-13", "severity": "P3", "title": "AI config GET trả về gemini/claude API key dạng thô cho ADMIN/CEO mọi tenant (AIConfig không tách tenant rõ ràng)"},
    {"id": "NEW-14", "severity": "P3", "title": "Deployment: systemd chạy uvicorn --workers 2 nhưng SECRET_KEY sinh ngẫu nhiên mỗi process nếu .env thiếu → session không hợp lệ chéo worker (HARD-05); deploy_vps chạy User=root, HTTP 8081 mở cổng"}
  ],
  "batch_order_recommendation": ["SEC-01", "NEW-07/personal-tenant", "SEC-02+session", "HARD-01/XSS", "SEC-07/login-identity", "SEC-06", "BUG-01/mobile", "NEW-11/company-status"]
}
```

`review_decision = INCOMPLETE`: đây là audit vùng chưa ai xem, phát hiện thêm lỗ hổng (NEW-07..NEW-14) cần USER quyết
định hướng xử lý; không phải APPROVE/REJECT một batch cụ thể.

---

## 2. Executive summary

1. Không có thay đổi code so với HEAD; working tree khớp byte với source đã test ở phần 1 → kết luận phần 1 vẫn hiệu lực.
2. **NEW-07 (P1):** mọi route `/api/personal/*` lọc theo `user_id = session["ma"]` (mã NV). Mã NV chỉ là duy nhất trong một tenant; hai công ty có thể cùng mã (ví dụ "ADMIN", "NV01"). Dữ liệu cá nhân (task, nhật ký, chi tiêu, sức khỏe…) do đó rò rỉ/sửa/xóa xuyên công ty nếu một người ở công ty A trùng mã với người ở công ty B — nhưng cả hai dùng cùng tenant DB? Thực tế personal dùng `get_db` (tenant DB theo cookie), nên rủi ro là: user chuyển tenant (switch-tenant → ma="ADMIN") sẽ thao tác trên dữ liệu personal của ma "ADMIN" trong tenant đích. Chi tiết §4.1.
3. **NEW-08 (P1):** chuỗi khai thác SEC-02 + SEC-01 + NEW-02 — mô tả ở §5, không có exploit thực thi.
4. **HARD-01 XSS xác nhận (NEW-09, P2):** nhiều `innerHTML = data.map(...)` chèn trực tiếp giá trị do người dùng nhập (tên CV, tên tài liệu, tên công ty, nhật ký) không escape; `mermaid.initialize({securityLevel:'loose'})` ở org_chart/processes; AI trả Markdown→HTML render thô bằng `innerHTML`.
5. **SEC-07 xác nhận (NEW-10, P2):** `check_login` dùng `Employee.email.like(f"{username_lower}%")` và `ma_nv == username_upper.split("@")[0]` + `.first()`.
6. **NEW-11 (P2):** `check_login` chỉ chặn hết hạn (`expiry_date`), không chặn `status != ACTIVE`; endpoint public `/api/auth/company-lookup` lại chặn status — bất nhất.
7. SEC-06: resolver path (`get_tenant_db_path`) chỉ ghép `TENANTS_DIR/{mst}.db`; mã số thuế từ cookie có thể chứa ký tự path. Đánh giá §4.2 — rủi ro thấp vì cookie đã ký, nhưng không có validation ký tự.
8. BUG xác minh lại: BUG-01/02/03 CONFIRMED; BUG-08 PARTIALLY (list đã lọc bằng `can_view_task`); BUG-09 nhiều khả năng đã sửa (export có fallback title).
9. Module master/companies/employees: tầng authz dựa `check_master_system_admin` (cờ `is_master_admin`) — kế thừa rủi ro SEC-01; personal thiếu cô lập tenant là lỗ hổng mới nghiêm trọng nhất.
10. Đề xuất thứ tự batch: SEC-01 → personal tenant isolation → SEC-02 → XSS → SEC-07 → SEC-06.

---

## 3. Batch/area decisions

| Vùng | Decision | Lý do | Evidence chính |
|---|---|---|---|
| SEC-06 tenant path | OPEN (xác nhận) | Không validate ký tự MST khi dựng path; nhưng input từ cookie đã ký | `multi_tenant.py:33-44` |
| SEC-07 login identity | OPEN (xác nhận) | prefix LIKE + split@ + first() | `auth_service.py:57-85` |
| SEC-02 session | OPEN (xác nhận) | không hạn/thu hồi server-side; chuỗi NEW-08 | `auth_service.py:240-249`, `routes/companies.py:299-320` |
| HARD-01 XSS | OPEN (xác nhận) | innerHTML thô + mermaid loose + AI markdown | §4.3 |
| Personal module | FAIL (NEW-07) | thiếu cô lập tenant/định danh | `routes/personal.py` + `personal_service.py` |
| Companies/Master/Employees | OPEN (kế thừa SEC-01) | authz = cờ is_master_admin | `routes/companies.py:22-33` |
| Processes/JD/OrgChart/AI | PASS (authz cơ bản ổn) | đều check session + role ghi | `routes/processes.py:182-187`, `jds.py:122-128`, `ai.py:104-108` |
| Mobile (ngoài SW) | FAIL (BUG-01/02) | field sai + payload AI sai + strip() | `routes/mobile.py:73-79`, `templates/mobile/*` |
| Deployment | OPEN (HARD-04/05) | root, HTTP 8081, workers 2 + SECRET ngẫu nhiên | `deploy_vps.sh`, `run_vps.bat` |

---

## 4. Chi tiết trọng tâm 1, 3, 4 (SEC-06/07, XSS, modules)

### 4.1 NEW-07 — Personal module thiếu cô lập định danh (P1)

`routes/personal.py:22-27` lấy định danh:

```python
22    def _check_auth(request: Request):
23        """Returns (session_dict, user_id) or (None, None) if not logged in."""
24        session = AuthService.get_session(request)
25        if not session:
26            return None, None
27        return session, session.get("ma", "")
```

Service lọc theo `user_id` = `session["ma"]` (ví dụ `personal_service.py:160-163`):

```python
160    def update_task(db: Session, user_id: str, task_id: int, data: dict):
161        task = db.query(PersonalTask).filter(PersonalTask.id == task_id, PersonalTask.user_id == user_id).first()
```

Vấn đề:
- `ma` không phải định danh toàn cục; nó là mã NV tenant-local. Dữ liệu personal nằm trong tenant DB (qua `get_db`).
- Qua `switch-tenant` (`routes/companies.py:313-320`), master admin được cấp session `ma="ADMIN"` trên tenant đích. Mọi `/api/personal/*` khi đó thao tác dữ liệu personal của record `user_id="ADMIN"` trong tenant đó — tức master đọc/sửa/xóa nhật ký, chi tiêu, sức khỏe cá nhân của ADMIN công ty khách. Không có ràng buộc "chỉ chủ sở hữu".
- Ngay trong một tenant: `user_id` chỉ là chuỗi `ma`; nếu hai nhân sự có cùng `ma` (hệ thống chỉ ràng buộc `ma_nv` duy nhất mỗi tenant, nhưng personal record không FK tới Employee) thì vẫn gom chung. Rủi ro nội tenant thấp hơn, nhưng thiết kế "user_id = text ma" không có khóa ngoại là mong manh.

Mức độ P1 vì phạm vi dữ liệu nhạy cảm (chi tiêu, sức khỏe, nhật ký) và khả năng truy cập xuyên tenant qua master switch — vốn là tính năng được dùng.

### 4.2 SEC-06 — tenant path confinement

`database/multi_tenant.py:33-44`:

```python
33    def get_tenant_db_path(tax_code: str) -> str:
35        clean_mst = str(tax_code or "").strip()
36        if clean_mst in ["0312345678", "default", ""]:
37            return os.path.abspath(os.path.join(..., "qlcv.db"))
39        p = os.path.abspath(os.path.join(TENANTS_DIR, f"{clean_mst}.db"))
```

- Không có validation ký tự: `clean_mst` chỉ `.strip()`. Nếu `clean_mst` chứa `../` hoặc dấu phân tách, `os.path.join` + `abspath` có thể trỏ ra ngoài `TENANTS_DIR` (ví dụ `..\\..\\qlcv` → tạo/mở file `.db` khác chỗ).
- Nguồn `tax_code`: chủ yếu từ `session["company_mst"]` (cookie đã ký — kẻ tấn công không tự đặt được nếu SECRET_KEY an toàn). Trong `check_login`, `company_mst` được chuẩn hóa về MST hợp lệ từ `MasterCompany` trước khi ký. Do đó khả năng khai thác thực tế **thấp** nếu SECRET_KEY an toàn + không có SEC-02.
- Nhưng kết hợp SEC-02 (cookie giả nếu lộ SECRET) hoặc bất kỳ đường nào nhận `tax_code` chưa qua master lookup, thiếu allowlist ký tự `[0-9]` là điểm yếu còn mở. Đồng ý SEC-06 OPEN.

### 4.3 HARD-01 — Danh sách sink XSS (NEW-09, P2)

Không tìm thấy hàm escape/DOMPurify nào trong các template ngoài CRM (grep: chỉ `crm_components.html`, `crm_script.html` có escape — mà CRM đã tắt). Các sink dựng HTML từ dữ liệu người dùng:

| File:dòng | Sink | Dữ liệu nguồn | Escape? |
|---|---|---|---|
| `tasks/index.html:358` | `tbody.innerHTML = data.map(t => \`…${t.idPhanCong}…${t.tenCV}…\`)` | tên CV, mã (user nhập) | KHÔNG |
| `tasks/index.html:415-416` | `innerHTML = item.noiDungNhacNho.replace(/\n/g,"<br>")` | nhật ký chỉ đạo/báo cáo | KHÔNG |
| `documents/index.html:240` | `tbody.innerHTML = data.map(d => …)` | tên tài liệu | KHÔNG |
| `documents/repository.html:182` | `container.innerHTML = data.map(d => …)` | tên/loại tài liệu | KHÔNG |
| `processes.html:314,365,569,708` | `innerHTML = …map(p => …)` | tên quy trình, bước | KHÔNG |
| `master/companies.html:565,599` | `tbody.innerHTML = html` / `…${comp.name}` | tên công ty (master nhập) | KHÔNG |
| `master/employees.html:249` | `tbody.innerHTML = data.map(e => …)` | tên nhân sự | KHÔNG |
| `master/departments.html:181` | `tbody.innerHTML = data.map(d => …)` | tên bộ phận | KHÔNG |
| `tasks/personal.html:1482..2493` (≈25 chỗ) | `el.innerHTML = …map(...)` | tên task/sự kiện/chi tiêu/nhật ký cá nhân | KHÔNG |
| `tasks/overdue.html:123`, `report_center.html:235`, `forward.html:278`, `jds.html:234,258` | `innerHTML = …map` | dữ liệu CV/nhân sự | KHÔNG |
| `ai_chat.html:257` | `msgDiv.innerHTML = contentHtml` (res.response_html) | AI Markdown → HTML (`routes/ai.py:42` `markdown.markdown(...)`) | KHÔNG sanitize |
| `mobile/ai.html:85` | `appendMessage('bot', data.reply.replace(/\n/g,'<br>'))` | AI reply | KHÔNG |
| `org_chart.html:391` | `div.innerHTML = mText` (mermaid source) + `securityLevel:'loose'` (`:136`) | tên nhân sự nhúng vào node | KHÔNG |
| `processes.html:110` | `mermaid.initialize({securityLevel:'loose'})` | — | mermaid loose |

Lưu ý giảm nhẹ: `ai_chat.html:294` có `escapedText` cho tin nhắn user, nhưng `response_html` từ server (Markdown) không được sanitize; `markdown` của Python không loại bỏ HTML thô nhúng trong câu trả lời AI → nếu AI (hoặc prompt injection qua tên task) sinh `<img onerror>` thì render. Stored-XSS khả thi: kẻ tấn công nhập `<script>`/`<img onerror>` vào tên CV, tên tài liệu, nhật ký → nạn nhân xem danh sách bị chạy script trong phiên của họ. Mức P2 (cần quyền ghi để chèn; nhưng USER thường có quyền tạo task). Đồng ý HARD-01 OPEN và nâng cấp evidence cụ thể.

### 4.4 Module companies/master/employees/dashboard (authz)

- `check_master_system_admin` (`routes/companies.py:22-33`) chặn bằng cờ `is_master_admin` — đúng về cấu trúc, nhưng kế thừa SEC-01 (cờ này tính từ mã NV reserved).
- `routes/master.py` employees/departments: `/api/employees` (POST/update) chỉ cần `role in [ADMIN,CEO]` — đây chính là đường leo thang SEC-01 (đã nêu phần 1).
- `get_dashboard_stats` (`auth_service.py:181-189`): lọc task theo `nguoi_giao|nguoi_nhan`, bỏ CC → lệch với `can_view_task` (CC được xem) → củng cố đánh giá BUG-08 PARTIALLY.
- `AIConfig` (`routes/ai.py:84-101`): trả khóa API thô cho ADMIN/CEO; `db.query(AIConfig).first()` không lọc tenant rõ ràng (lưu trong tenant DB theo cookie). NEW-13.

---

## 5. SEC-02 — Chuỗi tấn công kết hợp (NEW-08, P1) — chỉ mô tả

Tiền đề (đều từ source, không thực thi exploit):
- **SEC-02:** `get_session` (`auth_service.py:240-249`) chỉ verify chữ ký; cookie `max_age=86400` (`:225-233`) là hạn phía browser. Server không lưu phiên, không thu hồi, không revalidate role/tenant. Cookie bị sao chép vẫn dùng được tới khi SECRET_KEY đổi.
- **NEW-11:** công ty INACTIVE vẫn đăng nhập (không chặn status) → phiên tồn tại kể cả sau khi NSX khóa công ty.
- **SEC-01 / NEW-02:** mã NV reserved ở default tenant ⇒ master; `change_password` tự tạo lại ADMIN không cần mật khẩu cũ.

Chuỗi:
1. Kẻ tấn công có một phiên hợp lệ bất kỳ ở default tenant (hoặc lấy được cookie qua XSS HARD-01 / thiết bị dùng chung). Vì SEC-02, cookie này sống lâu và không thể thu hồi.
2. Nếu phiên có `ma="ADMIN"` (ví dụ do master `switch-tenant` ký sẵn `ma=ADMIN` — `routes/companies.py:313-320`, hoặc tài khoản ADMIN công ty), gọi `POST /api/auth/change-password` với `oldPass` bất kỳ: nếu tenant đó **chưa có** employee ADMIN, nhánh `auth_service.py:156-168` tạo mới ADMIN với mật khẩu kẻ tấn công chọn, **bỏ qua** kiểm tra mật khẩu cũ (NEW-02).
3. Ở default tenant, tài khoản ADMIN vừa tạo/đổi khi đăng nhập được tính `is_nsx_master_admin=True` (`auth_service.py:123`) → toàn quyền master: tạo/xóa công ty, thêm nhân sự mọi tenant, switch-tenant.
4. Vì SEC-02, kể cả khi bị phát hiện và khóa công ty (NEW-11) hay đổi role, cookie cũ vẫn hiệu lực đến khi đổi SECRET_KEY (và đổi SECRET_KEY lại vô hiệu hóa toàn bộ phiên — HARD-05).

Điểm mấu chốt: ba điểm yếu riêng lẻ (session không thu hồi + tạo lại ADMIN không cần mật khẩu + master phái sinh từ mã NV) cộng lại biến một phiên rò rỉ thành chiếm quyền master vĩnh viễn. Khắc phục SEC-01 (phương án hẹp phần 1 §11, gồm bỏ nhánh tự tạo ADMIN) cắt được bước 2–3; SEC-02 (phiên có hạn/thu hồi) cắt bước 1,4.

---

## 6. BUG re-verify (BUG-02, 04..07, 09) trên source hiện tại

| BUG | Status log | Kiểm chứng | Kết luận |
|---|---|---|---|
| BUG-02 | OPEN | `mobile/ai.html:76` gửi `{prompt:text}` nhưng `/api/ai/chat` đọc `payload.get("message")` (`routes/ai.py:36`) → luôn "câu hỏi trống"; `mobile/ai.html:85` đọc `data.reply` nhưng API trả `response_html`; `mobile/tasks.html:85` `.toLowerCase().strip()` (JS không có `.strip()`) → ném lỗi; `mobile/menu.html:88` logout bằng `GET /api/auth/logout` (có route GET `/logout` nhưng không `/api/auth/logout` GET — chỉ POST) | CONFIRMED (nhiều mismatch) |
| BUG-03 | OPEN | `routes/tasks.py:214` `@router.get("/api/tasks/{task_id}")` khai báo trước `:282` `/api/tasks/get-temp-id` → route động nuốt `get-temp-id` | CONFIRMED |
| BUG-04 | OPEN | Drive rename đã fail-closed 403 (`routes/documents.py:208-212`); phần "MST rename không chặn master/index update" vẫn đúng cho `api_update_company` (`routes/companies.py:261-266` rename DB file lỗi chỉ `print`, vẫn commit master) | CONFIRMED (một phần ở companies update) |
| BUG-05 | OPEN | `config.py:38` `DATABASE_URL` mặc định `sqlite:///qlcv.db`; `get_db` resolver (`connection.py:20`) mặc định `0312345678` → cùng trỏ qlcv.db; nếu đặt `DATABASE_URL` khác thì startup (`app.py:127` dùng `engine` từ DATABASE_URL) lệch với request resolver (dùng tenant path) | CONFIRMED |
| BUG-06 | OPEN | `create_company_tenant` (`multi_tenant.py:151-241`): tạo tenant DB + admin commit, rồi master commit; nếu master commit lỗi, tenant DB/admin đã tồn tại → partial. `init_...` sync nhiều commit | CONFIRMED |
| BUG-07 | OPEN | `init_master_and_default_tenant` chạy ở startup (`app.py:124`), ghi `emp.email` + GlobalUserIndex; với `--workers 2` (deploy_vps) nhiều process cùng init → đua | CONFIRMED (tăng rủi ro do workers 2) |
| BUG-09 | OPEN | `jds.py` export (`:183-188`) có fallback `emp_chuc_danh` và dùng `jd.chuc_danh or emp_chuc_danh` (`:205,221`); view (`:45-63`) cũng fallback. Export vẫn 404 nếu không có JD record, nhưng title fallback tồn tại | KHÔNG ĐỒNG Ý: phần "JD view fallback absent in export" dường như đã có fallback title; nên hạ xuống "LIKELY FIXED / cần test" |

---

## 7. Mobile/PWA ngoài SW

- `templates/mobile/crm.html` **vẫn tồn tại** trong repo (và tracked). Grep toàn bộ `routes/*.py`, `app.py`, `main_launcher.py`: **không có** route nào render `mobile/crm.html`. `routes/mobile.py` chỉ render dashboard/login/tasks/ai/menu. `routes/khach_hang.py` (CRM desktop) render `crm.html`/`crm_index.html` ở `/crm`, `/crm/spa` — nhưng router này không được include trong `app.py` (chỉ 11 router QLCV). Kết luận NEW-12: file CRM mobile là dead template, hiện không truy cập được qua app QLCV; nên xóa để tránh nhầm lẫn, nhưng không phải lỗ hổng đang mở.
- `routes/mobile.py:28,33-35,73-79` dùng `Task.trang_thai` và `Task.id` — model không có hai cột này (`Task.tinh_trang`, khóa `id_phan_cong`) → `/mobile`, `/mobile/tasks` 500 (BUG-01, khớp 2 FAIL fresh run).
- `static/manifest.json`: `start_url` `/mobile`; icon thiếu (HARD-03, đã ghi).

---

## 8. Fresh run so với claimed

Không chạy lại runner trong phần này. Tham chiếu phần 1: fresh `run-7b9d1713…` = 2396 PASS / 2 FAIL, khớp claimed
`run-44c3751c…`, 2 FAIL là mobile 500. Harness **không có** test nào cho personal tenant isolation, SEC-02 session,
XSS, SEC-06/07 → các finding ở báo cáo này nằm ngoài vùng phủ của bộ test (xác minh: grep tên nhóm test không có
`PERSONAL_`, `SESSION_`, `XSS_`, `SEC06_`, `SEC07_`).

---

## 9. Production integrity

Không chạy app, không mở DB, chỉ đọc source và template. Working tree khớp byte với `source_manifest.json` fresh run
(0 mismatch / 34 file). `git diff HEAD` rỗng với mọi file code. 10 file production được bảo vệ + `qlcv_khach_hang.db`
không đổi kể từ phần 1 (đã xác nhận 17:14 ở phần 1). Không có thao tác ghi nào trong phần này.

---

## 10. Finding status (bổ sung phần 1)

| ID | Status log | Ý kiến reviewer | Lý do + evidence |
|---|---|---|---|
| SEC-06 | OPEN | ĐỒNG Ý | `multi_tenant.py:35-39` không validate ký tự MST; rủi ro thực tế thấp (cookie đã ký) nhưng thiếu allowlist |
| SEC-07 | OPEN | ĐỒNG Ý + NEW-10 | `auth_service.py:57-85` prefix LIKE + split@ + first() |
| SEC-02 | OPEN | ĐỒNG Ý + NEW-08 | `auth_service.py:240-249`; chuỗi §5 |
| HARD-01 | OPEN | ĐỒNG Ý + NEW-09 | §4.3 |
| HARD-02 | OPEN | ĐỒNG Ý | `app.py:38-44` CORS `*`+credentials; cookie không Secure (`auth_service.py:225-233`) |
| HARD-04 | OPEN | ĐỒNG Ý | `deploy_vps.sh` HTTP 8081, systemd `User=root`, không TLS trong template |
| HARD-05 | OPEN | ĐỒNG Ý + NEW-13 | `config.py:25-33` SECRET ngẫu nhiên/process + `--workers 2` |
| BUG-08 | OPEN | KHÔNG ĐỒNG Ý → PARTIALLY | list đã lọc `can_view_task` (CC) nhưng `get_dashboard_stats` + mobile bỏ CC |
| BUG-09 | OPEN | KHÔNG ĐỒNG Ý → LIKELY FIXED | export có fallback title (`jds.py:205,221`) |

### Finding mới (code)

Xem Summary JSON NEW-07..NEW-14. Trích chính:

NEW-11 — `services/auth_service.py` không chặn status công ty (chỉ expiry); đối chiếu endpoint public lại chặn:

```python
# routes/auth.py:63 (company-lookup, public) — CHẶN status:
63        if comp.status != "ACTIVE":
# auth_service.py (check_login) — KHÔNG có nhánh tương tự cho status; chỉ kiểm expiry_date (dòng 100-108)
```

NEW-10 — `services/auth_service.py:79-85`:

```python
79                search_ma = username_upper.split("@")[0] if "@" in username_upper else username_upper
80                user = tenant_db.query(Employee).filter(
81                    (Employee.email == username_lower) |
82                    (Employee.email.like(f"{username_lower}%")) |
83                    (Employee.ma_nv == username_upper) |
84                    (Employee.ma_nv == search_ma)
85                ).first()
```

---

## 11. Nhận xét đề xuất SEC-01 (bổ sung)

Giữ nguyên đánh giá phần 1 §11 (phương án hẹp: sửa `auth_service.py:123`, `employee_service.py`, bỏ nhánh tự tạo ADMIN
`auth_service.py:156-168`, chặn reserved ID ở default tenant). Bổ sung từ phần này:
- Phương án hẹp đồng thời **cắt bước 2–3 của chuỗi NEW-08**, nên ưu tiên cao hơn vì vá cả SEC-01 lẫn một nhánh của chuỗi leo thang.
- File sửa (cập nhật): `services/auth_service.py`, `services/employee_service.py`, `routes/master.py`; kèm test. Không đụng session format (để SEC-02 xử lý riêng).

---

## 12. Câu hỏi cần USER quyết định

1. **Personal tenant/định danh (NEW-07, P1).**
   - A: Ràng buộc personal theo `(company_mst, ma)` hoặc thêm FK tới Employee + chặn thao tác khi `is_master_admin` đang switch-tenant. Hệ quả: sửa `personal_service.py` + routes; thêm cột/filter.
   - B: Chấp nhận rủi ro (master xem được personal của tenant khách). Hệ quả: rò rỉ dữ liệu nhạy cảm.
   - Khuyến nghị: **A**.
2. **SEC-02 session (gốc của NEW-08).**
   - A: Thêm server-side session store (hoặc jti + hạn + danh sách thu hồi) và revalidate role/tenant mỗi request.
   - B: Chỉ rút ngắn `max_age` + rotate SECRET định kỳ. Hệ quả: giảm thiểu, không triệt để.
   - Khuyến nghị: **A** (gộp với SEC-01 ở cùng đợt xác thực).
3. **HARD-01 XSS (NEW-09).**
   - A: Thêm hàm escape dùng chung + sanitize AI HTML (bleach/DOMPurify) + `mermaid securityLevel:'strict'`.
   - B: Chỉ escape các trường hiển thị tên. Hệ quả: bỏ sót AI/mermaid.
   - Khuyến nghị: **A**; ưu tiên AI render và danh sách task/tài liệu trước.
4. **SEC-07 + NEW-11.** A: login so khớp định danh chính xác (bỏ prefix LIKE, bỏ split@ fallback) + chặn `status!=ACTIVE`. B: giữ nguyên. Khuyến nghị: **A**.
5. **SEC-06.** A: validate MST bằng allowlist `^[0-9]{10,14}$` trước khi dựng path. B: dựa vào cookie đã ký. Khuyến nghị: **A** (chi phí thấp).
6. **CRM mobile dead template (NEW-12).** A: xóa `templates/mobile/crm.html` + `templates/crm*.html` nếu không dùng. B: giữ. Khuyến nghị: **A** để giảm bề mặt nhầm lẫn.

---

## 13. Giới hạn của review này

- Không chạy app/browser/DB; chỉ đọc source, template, script.
- Không chạy guarded runner trong phần này (không cần cho các finding; harness không phủ các vùng này).
- XSS: xác định sink bằng grep + đọc ngữ cảnh, **không** chứng minh khai thác thực tế (không render thật).
- NEW-07/NEW-08 là phân tích luồng code; chưa dựng PoC. Mức severity dựa trên khả năng và phạm vi dữ liệu.
- `routes/khach_hang.py` (CRM) đọc để xác nhận không được include; không audit bảo mật CRM (ngoài phạm vi, CRM đã tắt).
- Không audit lại toàn bộ `personal_service.py` (460 dòng) — chỉ các hàm đại diện (task/update/delete) đủ để xác nhận mẫu `user_id`.
- Deployment: chỉ đọc script, không kiểm chứng trên VPS thật.

---

## 14. Đề xuất thứ tự batch sau SEC-01 (rủi ro × effort)

Thang: Rủi ro P1 cao nhất; Effort S/M/L.

| Hạng | Batch | Rủi ro | Effort | Lý do xếp hạng |
|---|---|---|---|---|
| 1 | **SEC-01** (phương án hẹp, phần 1 §11) | P0 | S–M | Chiếm master; vá luôn một nhánh chuỗi NEW-08; sửa 3 file |
| 2 | **NEW-07 personal tenant isolation** | P1 | M | Rò rỉ dữ liệu cá nhân xuyên tenant; sửa service+routes, có thể thêm cột |
| 3 | **SEC-02 session (store + revalidate)** | P1 | M–L | Gốc của chuỗi leo thang và phiên không thu hồi; nên làm cùng SEC-01 |
| 4 | **HARD-01 XSS** | P2 | M | Stored-XSS nhiều nơi; escape dùng chung + sanitize AI + mermaid strict |
| 5 | **SEC-07 + NEW-11 login identity/status** | P2 | S | Bỏ prefix LIKE/split@, chặn INACTIVE; thay đổi khu trú ở check_login |
| 6 | **SEC-06 path allowlist** | P2 | S | Thêm regex MST; chi phí thấp |
| 7 | **BUG-01/02/03 mobile** | P1 (chức năng) | M | Mobile đang 500; cần sửa field + payload + route order; nhiều việc UI |
| 8 | **NEW-12 dọn template CRM + NEW-13 AI key** | P3 | S | Giảm bề mặt; che khóa API |
| 9 | **HARD-04/05 deployment** | P2 | M | TLS, bỏ root, SECRET cố định, workers; phụ thuộc hạ tầng |

Ghi chú: gộp 1+3 (SEC-01 + SEC-02) vào một đợt "identity & session" là hiệu quả nhất vì chúng chia sẻ file
(`auth_service.py`, `routes/companies.py`) và cùng vá chuỗi NEW-08. BUG mobile (#7) tách riêng vì thuần chức năng,
không chặn các vá bảo mật.

# QLCV_web — Quy tắc làm việc cho Claude Code

## Vai trò
Claude Code là executor duy nhất cho app QLCV.
Codex KHÔNG làm việc trong repo này (Codex chỉ dọn ổ C: ở thư mục khác).

## Git
- Branch: security/codex-batches-20261001. HEAD = baseline đã review.
- Delta batch = git diff HEAD + git status. Ghi danh sách vào log.
- KHÔNG commit / reset / restore / clean / stash / checkout / push. USER commit sau review.
- Đầu batch: working tree có thay đổi không thuộc batch → STOP, liệt kê, chờ USER.
- Ngoại lệ: file untracked của tiến trình dọn ổ C (cleanup_*, free_c_*, ket_qua_don_rac*, don_rac*,
  ke_hoach_xoa*, c-storage-audit-*/, cleanup-verification-*/) KHÔNG thuộc QLCV:
  không đọc, không sửa, không STOP vì chúng. File lạ khác → liệt kê và STOP.

## Test & integrity
- Runner duy nhất: .\venv\Scripts\python.exe -B tests/runtime_sandbox.py
  Chạy fresh. Đọc runtime_results.json, preflight.json, integrity.json. Không tin exit code.
- Baseline FAIL hợp lệ duy nhất: /mobile và /mobile/tasks trả 500 (BUG-01). Mọi FAIL khác = NEW REGRESSION.
- KHÔNG nới assertion, skip test, đổi expected hay fixture để PASS.
- Production integrity: SHA-256/size/mtime_ns của protected DB/data/uploads, qlcv_khach_hang.db, private_metadata/
  phải khớp trước và sau.

## Cấm
- Khởi động app production (uvicorn, chay_app.bat, run_vps.bat, main_launcher.py).
- Ghi DB production; seed/migration; pip install; gọi network/Drive/AI provider; deploy.
- In secret, mật khẩu, nội dung .env hay dữ liệu nhân viên thật.

## Tài liệu
- Log trung tâm: CODEX_AUDIT_FIX_LOG.md (giữ tên để liên tục). Mỗi entry mới ghi "Executor: Claude Code".
- Mỗi batch có checklist riêng: CODEX_REVIEW_CHECKLIST_<BATCH>.md.
- Prompt của từng batch nằm ở docs/prompts/<BATCH>.md.
- Báo cáo handoff cho reviewer bên ngoài: docs/review/HANDOFF_<BATCH>_<YYYYMMDD_HHMM>.md.
  Báo cáo phải tự chứa: summary JSON, delta file, trích code chính có số dòng,
  bảng test theo nhóm (claimed vs fresh), danh sách FAIL nguyên văn, integrity, rủi ro còn lại.
- Ngoài phạm vi file được duyệt, hoặc gặp điều kiện cần USER quyết định → STOP.

## Trạng thái hiện tại
Xem CODEX_AUDIT_FIX_LOG.md, docs/review/CLAUDE_INDEPENDENT_REVIEW_20261001_1708.md và _1738.md.
Roadmap: DOC-1 → SEC-01 → PWA-2+4B6 → DEPLOY GATE → AUTH-QUICK → XSS → SEC-02 → MOBILE → OPS.

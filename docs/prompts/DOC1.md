# Batch DOC-1 — Làm mới tài liệu (USER-authorized, CHỈ TÀI LIỆU)
Tuân thủ CLAUDE.md. Executor: Claude Code.

## Nguồn
- docs/review/CLAUDE_INDEPENDENT_REVIEW_20261001_1708.md (§5, §6.5, §7.3, §10)
- docs/review/CLAUDE_INDEPENDENT_REVIEW_20261001_1738.md

## Phạm vi được sửa
CODEX_AUDIT_FIX_LOG.md, CODEX_REVIEW_CHECKLIST_4B5.md, và file handoff mới trong docs/review/.
Không sửa file nào khác.

## Việc cần làm
1. Sửa đủ 16 mục stale theo bảng §5 của review 1708. Đưa các entry 4B5-stop / 4B5A / 4B5 / SEC-01 vào bảng §13.
   Bỏ heading cấp `#` sai cấu trúc.
2. Ghi nhận việc đổi nhãn 4 test PWA_4B3_INTEGRATION → PROVENANCE_PWA_INTEGRATION ở 4B5A.
   Sửa mô tả attempt-1 (file đổi thật là services/file_registry.py).
   Liệt kê 3 attempt run của Resumed 4B5 kèm số liệu.
3. Cập nhật status:
   - BUG-08 → PARTIALLY FIXED (list đã dùng can_view_task; dashboard get_dashboard_stats và mobile còn bỏ CC).
   - BUG-09 → LIKELY FIXED (cần test).
   - BUG-04..07 → CONFIRMED trên current source.
   - HARD-03: ghi rõ phần private cache đã giảm thiểu ở 4B4.
4. Đăng ký finding (status OPEN, nguồn = Claude independent review):
   - NEW-01 P2; NEW-02 P2 (gộp vào SEC-01); NEW-03 P2 ROLLOUT BLOCKER; NEW-04 P3; NEW-05 P3; NEW-06 P3.
   - NEW-07 P2, đổi tên: "switch-tenant ký ma=ADMIN giả danh ADMIN tenant, không ghi actor thật, ảnh hưởng mọi module (gồm personal)". Thuộc nhóm SEC-02.
   - NEW-08: KHÔNG cấp ID. Ghi trong SEC-02 dạng "chuỗi tấn công SEC-01 + SEC-02 + NEW-02".
   - NEW-09 (HARD-01 XSS) → P1 (stored XSS có thể chạy với quyền master khi master xem Task).
   - NEW-10 P2 (evidence SEC-07); NEW-11 P2; NEW-13 P3.
   - NEW-12 → cleanup task, không phải finding. NEW-14 → gộp vào HARD-04/05.
5. Kiểm tra READ-ONLY: cookie session có HttpOnly không (set_cookie trong services/auth_service.py). Ghi kết quả vào HARD-02.
6. Thêm mục "Git baseline": liệt kê các commit trên branch (git log --oneline).
   Từ nay delta batch đo bằng git diff HEAD.
   Thêm mục "Executor": từ DOC-1 trở đi là Claude Code; Codex không còn làm việc trong repo.
7. Thêm mục "Roadmap" theo CLAUDE.md:
   DOC-1 → SEC-01 → PWA-2+4B6 → DEPLOY GATE → AUTH-QUICK → XSS → SEC-02 → MOBILE → OPS.
8. Cập nhật CODEX_REVIEW_CHECKLIST_4B5.md theo acceptance thật trong audit_codex_v3.md.

## Quy tắc
- Mọi con số phải đối chiếu với runtime_results.json của run tương ứng.
- Không chạy runner. Không sửa code.

## Kết thúc
- git diff --check.
- Integrity hash protected files trước/sau.
- Ghi Change History.
- Ghi handoff docs/review/HANDOFF_DOC1_<YYYYMMDD_HHMM>.md: danh sách mục đã sửa (trước/sau), số finding đã đăng ký, kết quả HttpOnly, integrity.
- STOP.

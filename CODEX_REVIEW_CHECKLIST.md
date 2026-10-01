# CODEX REVIEW CHECKLIST — QLCV Batch 4B2

Checklist theo phạm vi và quyết định kiến trúc được USER phê duyệt. Dùng cho
review sau Batch 4B2; checkbox trống không phải kết luận FAIL hay PASS.
Reviewer ghi evidence (file/dòng, test name, run directory), kết quả và remaining
risk cho từng mục. Không coi exit code hoặc historical count là bằng chứng hiện tại.
Checklist không cấp quyền sửa code, chạy test, migration hoặc bắt đầu batch khác.

## 1. Scope code

- [ ] Production scope chỉ gồm `services/file_binding_service.py` (mới),
  `services/file_registry.py`, `services/drive_service.py`, `routes/documents.py`,
  `routes/tasks.py`, `services/task_service.py`, `config.py`.
- [ ] Test/docs scope: `tests/runtime_sandbox.py`, `tests/RUNTIME_SANDBOX.md`,
  `CODEX_AUDIT_FIX_LOG.md`; mọi helper thêm phải được giải thích/phê duyệt.
- [ ] Không sửa DocumentService, task_policy, models/schema, database/resolver,
  app.py, templates, static, deployment hoặc mobile.
- [ ] Phân biệt Batch 4B2 với thay đổi có sẵn; không nhận công mobile/VPS/user work.
- [ ] Diff từng production file và `git diff --check` có evidence review.

## 2. Registry schema/version

- [ ] SQLite sidecar có revised schema version rõ ràng; version hiện tại là v2.
- [ ] Incompatible v1/unknown/newer version hoặc thiếu constraint: fail closed,
  có lỗi version/migration rõ ràng; không reset/delete/recreate/discard metadata.
- [ ] Tối đa một ACTIVE và một reserved PENDING cho exact tenant/object/field slot.
- [ ] Storage locator unique theo trusted root + storage_name; generation hợp lệ.
- [ ] foreign_keys ON, busy timeout bounded, short transaction, BEGIN IMMEDIATE
  và SQLite constraints authoritative; không dựa vào process-local lock.
- [ ] Không ALTER/migrate business DB; test sidecar chỉ trong fresh sandbox.
- [ ] Import/config không tạo production registry; path nằm ngoài static/uploads
  và LOCAL_DOCS, có confinement validation. WAL chỉ khi verified local disk.

## 3. Upload WRITING -> UNBOUND

- [ ] Validate auth, tenant, extension/size trước khi tạo authority.
- [ ] Server allocate UUID locator, register WRITING trước exclusive physical write.
- [ ] Không overwrite existing bytes; collision retry/concurrency vẫn an toàn.
- [ ] Actual completed bytes xác định size/SHA-256; complete UNBOUND sau write thành công.
- [ ] Registry/write/completion lỗi: không trả successful upload, không có usable record.
- [ ] Giữ URL/name contract; opaque file_id nếu thêm chỉ là additive server identity.

## 4. Trusted tenant/uploader identity

- [ ] Tenant từ authenticated server context; actor từ session và tenant-local identity.
- [ ] Client company/MST, uploader/owner, role, file_id, storage path, size/hash,
  classification hoặc binding object không cấp authority.
- [ ] Không lookup/fallback tenant khác để grant binding.

## 5. UNBOUND policy

- [ ] Metadata/binding eligibility: same tenant + exact uploader + chưa expired.
- [ ] Expiry 24 giờ; ADMIN không implicit override.
- [ ] Expiry không tự xóa physical bytes; abandoned upload không tự có object binding.
- [ ] Không tuyên bố UNBOUND READ được bảo vệ khi download gateway chưa tồn tại.

## 6. PENDING -> business commit -> exact revalidation -> ACTIVE

- [ ] Object/action authorization thành công trước mọi registry mutation.
- [ ] Canonical local URL resolve đúng trusted registry entry, tenant và eligible state.
- [ ] Prepare PENDING exact object/field/generation trước business mutation.
- [ ] Business commit thành công; reload exact persisted object từ authenticated tenant.
- [ ] Object tồn tại và persisted field bằng exact expected canonical URL trước ACTIVE.
- [ ] Client Task ID/Document code/URL đơn thuần không chứng minh binding.

## 7. Failure rollback/compensation

- [ ] Test failure ở registry/physical/completion/PENDING/business commit/reload/activation.
- [ ] Failed business commit không tạo ACTIVE; rollback business transaction chưa commit.
- [ ] Revalidation/activation failure không kích hoạt replacement; old ACTIVE được giữ.
- [ ] Compensation chỉ revoke đúng still-PENDING intent, không revoke ACTIVE retry.
- [ ] Stale PENDING không cấp read authority; unavailable/corrupt registry fail closed.
- [ ] Không giả vờ business DB + sidecar atomic: post-commit failure có thể để URL
  business đã lưu nhưng chưa ACTIVE; API báo failure, ghi rõ reconciliation risk.
- [ ] Không tự rollback production hoặc xóa pre-existing physical bytes.

## 8. Replacement giữ old ACTIVE khi new còn PENDING

- [ ] Prepare B PENDING không revoke A ACTIVE trước business success.
- [ ] Commit FAIL và commit PASS/revalidation FAIL đều giữ A ACTIVE, B không ACTIVE.
- [ ] Kiểm tra state ở từng boundary, không chỉ kết quả cuối.

## 9. Atomic activation/revocation

- [ ] Sau commit + exact revalidation, transaction verify expected PENDING/generation.
- [ ] Activate replacement và supersede chỉ old exact-slot ACTIVE trong cùng transaction.
- [ ] Exactly intended ACTIVE generation; shared ACTIVE ở object/slot khác được giữ.
- [ ] Clear field chỉ revoke exact slot sau confirmed commit/reload; không xóa bytes.
- [ ] Không globally REVOKED physical file khi binding khác vẫn ACTIVE.

## 10. Concurrent replacement B/C

- [ ] Concurrent different replacement fail closed hoặc serialize an toàn.
- [ ] Không có >1 ACTIVE generation cho cùng exact slot; ACTIVE khớp persisted field.
- [ ] Kiểm thử threads và independent processes; không dùng in-memory lock làm authority.
- [ ] Busy/lock failure controlled; sidecar readable, không lost update/partial authority.

## 11. Idempotent retry

- [ ] Same exact reservation retry trả cùng binding an toàn.
- [ ] Repeated unchanged save/activation không tạo conflicting duplicate ACTIVE.
- [ ] Stale/revoked generation không được tái activate; retry không revoke shared binding.

## 12. Task file_giao_viec binding

- [ ] Reuse approved SEC-05 CREATE/EDIT: ADMIN/giver; receiver/CC/unrelated không EDIT.
- [ ] Non-ADMIN CREATE giver canonicalized từ actor; suggested/unused ID không bypass.
- [ ] Binding dùng exact successfully committed Task ID, không client ID đơn thuần.
- [ ] Valid creator/giver/ADMIN flow, replacement/clear/retry đều covered.

## 13. Task file_bao_cao binding

- [ ] Reuse SEC-05 REPORT: ADMIN/receiver; giver/CC/unrelated DENY.
- [ ] Report field slot riêng, không trở thành generic Task edit.
- [ ] Server reporter; body Task ID không override path Task ID hoặc binding target.
- [ ] Foreign/other-uploader UNBOUND/expired/unknown file không được report-bind.
- [ ] Report replacement/clear/commit failure có evidence.

## 14. Forward parent/child binding

- [ ] Reuse SEC-05 DELEGATE; parent tồn tại và được authorize trước mutation.
- [ ] Trusted inherited parent attachment tạo child binding riêng sau child commit/reload.
- [ ] Same tenant, không copy bytes; parent/child ACTIVE độc lập.
- [ ] Parent attachment unregistered/legacy giữ reference compatibility nếu cần,
  nhưng không tạo trusted child claim.
- [ ] Failed child commit không tạo ACTIVE child; forged giver không grant authority.

## 15. Document link_file binding

- [ ] Giữ current Document authorization, không redesign ACL/DocumentService.
- [ ] Create/update dùng exact tenant Document ID và distinct link_file slot.
- [ ] Exact persisted Document/link_file revalidation trước ACTIVE.
- [ ] Valid create/update/replace/clear, unauthorized/foreign denial và fault injection covered.
- [ ] Editable link_file/ma_tl không tự chứng minh physical ownership.

## 16. Cross-tenant denial

- [ ] A actor không bind B file/object; foreign receiver/CC không được grant quyền.
- [ ] Client company/MST không switch DB; same Task ID A/B chỉ authenticated tenant tác động.
- [ ] No cross-tenant shared binding/forward union, kể cả ADMIN.

## 17. Legacy UNKNOWN không auto-claim

- [ ] UNKNOWN DENY kể cả ADMIN cho đến verified mapping; không auto-claim từ URL,
  filename, timestamp, DB reference hoặc first matching object.
- [ ] NEW unregistered local reference bị reject; không nới validator để fixture giả PASS.
- [ ] Unchanged/inherited legacy compatibility không tạo registry ownership/ACTIVE claim.
- [ ] Không scan/import production legacy files hoặc ghi verified mapping trong 4B2.

## 18. External/local_docs compatibility

- [ ] Existing external URL/local_docs behavior giữ nguyên, không coi là local ownership.
- [ ] Absolute URL pretending local, traversal/encoding/slash/backslash/query aliases DENY.
- [ ] URL cũ không rewrite DB; legacy physical files không move/rename.

## 19. Denied-write zero mutation

- [ ] Mọi authorization/eligibility denial: A/B Task và Document rows unchanged.
- [ ] Registry unchanged: không tạo ACTIVE/PENDING authority.
- [ ] Existing attachment bytes/hash unchanged; provider mutation count unchanged/0.
- [ ] Phân biệt authorization denial với infrastructure failure sau durable business commit;
  không che post-commit compensation limitation bằng tuyên bố zero mutation sai.

## 20. Production integrity

- [ ] Pre/post SHA-256, size, mtime cho protected DB/data/uploads khớp.
- [ ] PRODUCTION DB MODIFIED = NO; PRODUCTION DATA MODIFIED = NO.
- [ ] PRODUCTION REGISTRY CREATED = NO; PRODUCTION UPLOAD CREATED = NO.
- [ ] Core fingerprints chỉ đổi approved files; current source khớp tested snapshot.
- [ ] Không production startup, provider request, seed/migration, package install,
  production cleanup, commit hoặc git reset/clean/restore.

## 21. SEC-05 530 regression

- [ ] Current fresh run: 530 PASS / 0 FAIL; approved action matrix không thay đổi.
- [ ] Client-ID/forged giver/actor/role/company, tenant, zero-mutation và suggested-code auth PASS.
- [ ] Positive attachment fixture dùng synthetic trusted upload/binding, không fictitious URL.
- [ ] Không skip assertion hoặc nới expected result; SEC-05 status dựa trên evidence.

## 22. SEC-03 84 regression

- [ ] Current fresh run: 84 PASS / 0 FAIL; anonymous/invalid upload401, legitimate upload PASS.
- [ ] Drive rename giữ anonymous401/authenticated403 fail-closed; no provider mutation.
- [ ] SEC-03 PARTIALLY FIXED; Drive rename BLOCKED, không mở lại.

## 23. BUG-10 collision 13 regression

- [ ] Current fresh run: 13 PASS / 0 FAIL; same filename/rapid/concurrent upload không overwrite.
- [ ] Forced collision retry/exhaustion, extension validation và traversal confinement PASS.
- [ ] Numeric validation không tự nhận đã sửa; BUG-10 PARTIALLY FIXED.

## 24. Core smoke + 11 routers

- [ ] Login/dashboard/tasks/logout current run PASS.
- [ ] All11 routers load: auth, tasks, master, companies, documents, personal, ai,
  processes, jds, org_chart, mobile.
- [ ] Fresh guarded runner; preflight, runtime_results.json và integrity.json đều reviewed.
- [ ] complete=true; report từng 4B2 subgroup, full PASS/FAIL và new regressions.

## 25. Mobile baseline

- [ ] Chỉ gọi `/mobile`500 và `/mobile/tasks`500 là BASELINE nếu current run reproduce.
- [ ] Failure mới phải ghi NEW REGRESSION, không gộp vào baseline.
- [ ] Không sửa mobile/PWA để làm batch này PASS.

## 26. SEC-04 vẫn OPEN sau 4B2

- [ ] Batch4B2 COMPLETE/FIXED chỉ mô tả approved upload/binding slice.
- [ ] SEC-04 = OPEN, không PARTIALLY FIXED/FIXED chỉ vì metadata/binding tồn tại.
- [ ] Ghi rõ public static bypass/private read/PWA/legacy verification chưa được bảo vệ.

## 27. Không gateway/static/PWA/legacy migration trong 4B2

- [ ] Không gateway/new read endpoint, app.py/static mount hoặc service-worker change.
- [ ] Không ownership inference, legacy verification/import, business SQL migration,
  physical move/rename/delete, Drive rename hoặc finding khác.
- [ ] Không tự bắt đầu 4B3; next slice chỉ là đề xuất, chờ USER.

## CRITICAL REJECTION CONDITIONS

Phát hiện bất kỳ điều kiện nào dưới đây => REJECT review, ghi evidence và dừng;
không tự sửa/nới test hoặc đánh dấu batch an toàn.

- [ ] Revoke old ACTIVE trước business commit hoặc trước exact revalidation thành công.
- [ ] Client URL tự trở thành trusted binding/ownership authority.
- [ ] Failed business commit tạo ACTIVE.
- [ ] Concurrent replacements tạo >1 ACTIVE cùng exact slot.
- [ ] Nới test/security expectation, skip assertion hoặc đổi fixture để che lỗi và PASS.
- [ ] Đánh dấu SEC-04 FIXED sau 4B2.

## REPLACEMENT INVARIANT

Exact slot = `(tenant_id, object_kind, object_id, field_slot)`.
PENDING không cấp read authority; physical blob có thể có vetted bindings khác
nhưng không cross-tenant. Những binding khác không bị revoke bởi replacement slot này.

```text
Initial:
    A = ACTIVE

Prepare replacement:
    A = ACTIVE
    B = PENDING

Business failure:
    A = ACTIVE
    B != ACTIVE

Commit PASS nhưng exact revalidation FAIL:
    A = ACTIVE
    B != ACTIVE

Commit + exact revalidation PASS:
    A = REVOKED/SUPERSEDED
    B = ACTIVE

Concurrent B/C:
    Cuối cùng tối đa 1 ACTIVE generation cho cùng exact slot.
    Nếu business commit + exact revalidation + activation thành công:
    ACTIVE generation phải là generation dự kiến và khớp persisted field.
```

## Review record

- Reviewer/date/time:
- Source snapshot/run directory:
- Targeted upload/binding/replacement/failure/concurrency/schema PASS/FAIL:
- Registry/SEC-05/SEC-03/BUG-10/Core/mobile results:
- Production integrity evidence:
- Critical rejection conditions found:
- Remaining risks / next recommended action:
- Review decision: APPROVE / REJECT / INCOMPLETE.

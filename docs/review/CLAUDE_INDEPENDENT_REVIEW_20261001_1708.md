# CLAUDE INDEPENDENT REVIEW — QLCV_web (second opinion cho công việc Codex)

Reviewer: Claude (independent security reviewer, chế độ chỉ kiểm chứng — không sửa source/test/log).
Báo cáo tự chứa evidence: mọi trích dẫn code có số dòng, mọi con số lấy trực tiếp từ artifact JSON.
Tên file upload production được thay bằng nhãn `<legacy-docx-1>`, `<legacy-docx-2>` (chỉ ghi hash, không ghi tên thật).

---

## 0. Metadata

| Mục | Giá trị |
|---|---|
| Thời gian review | 2026-10-01 16:5x → 17:1x (Asia/Ho_Chi_Minh) |
| Git HEAD | `961f23b2a5295b81ea94e4899933baf33c15855b` |
| Branch | `main` |
| Tracked-modified | 15 file (`git diff --stat`: 15 files, +336 / −306) |
| Untracked | 34 entry top-level trong `git status --porcelain` (46 khi `--untracked-files=all`) |
| Fresh run directory | `.test_runtime/run-7b9d17133d294f419996f96d9bdc1576/` (bắt đầu 16:59:15, kết thúc 17:08:05, exit code 0) |
| Run được log khai là mới nhất | `.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/` (Resumed 4B5) |
| CODEX_AUDIT_FIX_LOG.md | 2089 dòng, SHA-256 `30abd7b2fce9287e9b9f9e3c9849be64700c1710aa1c692518f269528da67398`, mtime 2026-10-01 13:45:40 |
| CODEX_REVIEW_CHECKLIST.md (4B2) | `31c16cc8d88421284f8cd930fe898b71b211e7c27eac9510db7d23cfec6836f7` |
| CODEX_REVIEW_CHECKLIST_4B3.md | `2307ec75c4f0037227db02a88b6c20c2e995590897e526b76e561672c20fd533` |
| CODEX_REVIEW_CHECKLIST_4B4.md | `d80c9cac47425012a5c19afc811e2ac6fbdb5a51da16b1b063c9b0a712cf6406` |
| CODEX_REVIEW_CHECKLIST_4B5.md | `473c5910ae7f772211768fca83616531236956f72b14676f16dfd383ecdbb9b7` |
| CODEX_REVIEW_CHECKLIST_4B5A.md | `7af36e6cd21253888613c5c0c8fb055e8b7f07ff2a30e0b1cf766553214c56da` |
| audit_codex_v1.md | `77f8f639…72654e9` (khớp hash v3 ghi lại) |
| audit_codex_v2.md | `4b7bcd58…f9bf4f2f1` (khớp hash v3 ghi lại) |
| audit_codex_v3.md | `142f00a8b95531b0ec4e351b4edb94c6884ac70ea4f86d4f2006e5564fdea34b` (khớp hash v4 ghi lại) |
| audit_codex_v4.md | `1b7816642511f8cc69db89e874d62bcd44dcfcf69376726e0d66008c0b7f5797` |
| Source đã đọc | services/file_registry.py (320 dòng), file_binding_service.py (114), file_access_service.py (181), legacy_provenance.py (105), legacy_discovery.py (phần liên quan), task_policy.py (67), task_service.py (260), drive_service.py (154), auth_service.py (phần SEC-01), employee_service.py (phần SEC-01); routes/tasks.py (288), routes/documents.py (239), routes/companies.py, routes/master.py, routes/auth.py, routes/mobile.py (phần BUG-01); app.py (179); static/sw.js (103); config.py (59); tests/runtime_sandbox.py (2194, đọc có chọn lọc); tests/RUNTIME_SANDBOX.md |

Ghi chú quan trọng về git: `git diff` chỉ phản ánh 15 file tracked. Toàn bộ module mới của SEC-04/SEC-05
(`services/file_registry.py`, `file_binding_service.py`, `file_access_service.py`, `legacy_provenance.py`,
`legacy_discovery.py`, `task_policy.py`, `routes/mobile.py`, `static/sw.js`, `tests/`) đều **untracked**, nên
`git diff` KHÔNG cho thấy đầy đủ thay đổi. Reviewer đã dùng `source_manifest.json` của từng run để xác định delta
theo batch (xem §5, §7). Hai entry untracked `cleanup-verification-20261001-165036/` và `verify_cleanup_candidates.py`
có mtime 16:50–16:51, không thuộc Codex và không thuộc review này.

---

## 1. Summary JSON

```json
{
  "review_decision": "APPROVE",
  "batches": {
    "3D": "APPROVE",
    "4B1": "APPROVE",
    "4B2": "APPROVE",
    "4B3": "APPROVE",
    "4B4": "APPROVE",
    "4B5A": "APPROVE",
    "4B5": "APPROVE"
  },
  "critical_rejection_found": false,
  "fresh_run": {
    "complete": true,
    "pass": 2396,
    "fail": 2,
    "groups": {
      "PWA": "314/314",
      "gateway": "531/531",
      "4B2": "338/338",
      "registry": "77/77",
      "SEC05": "530/530",
      "SEC03": "84/84",
      "collision": "13/13",
      "provenance_4B5A": "234/234",
      "tooling_4B5": "225/225"
    }
  },
  "claimed_latest": {
    "run_dir": ".test_runtime/run-44c3751cf1424f059f00b4305853ce0c",
    "pass": 2396,
    "fail": 2
  },
  "new_regressions": [],
  "production_integrity_unchanged": true,
  "log_inconsistencies_count": 16,
  "test_integrity_issues_count": 5,
  "new_findings": [
    {"id": "NEW-01", "severity": "P2", "title": "Stale PENDING binding khóa vĩnh viễn mọi thao tác sửa Task/Document trên slot đó"},
    {"id": "NEW-02", "severity": "P2", "title": "change_password tự tạo lại tài khoản ADMIN thiếu mà không kiểm tra mật khẩu cũ"},
    {"id": "NEW-03", "severity": "P2", "title": "Service worker root-scope chuyển mọi request động (navigation/POST) qua fetch(request,{cache:'no-store'}) chưa được kiểm chứng trên browser thật"},
    {"id": "NEW-04", "severity": "P3", "title": "Lỗi sau business commit trả thông báo 'Không có quyền' dù dữ liệu đã được lưu"},
    {"id": "NEW-05", "severity": "P3", "title": "Endpoint không xác thực lộ thông tin: /api/auth/lookup-user-tenant (email→MST), /api/documents/next-code"},
    {"id": "NEW-06", "severity": "P3", "title": "Harness integrity không bao phủ qlcv_khach_hang.db và private_metadata/"}
  ]
}
```

Giải thích `review_decision = APPROVE`: không phát hiện critical rejection condition nào; fresh run tái lập chính xác
con số đã khai (2396/2, cùng 2 FAIL mobile); production integrity không đổi. APPROVE ở đây là cho **chất lượng code và
evidence trong phạm vi từng batch**, KHÔNG phải chấp thuận production rollout (real browser, Nginx thật, chính sách
legacy production chưa được kiểm chứng). Log trung tâm có 16 chỗ stale/mâu thuẫn cần làm mới trước khi dùng làm handoff.

---

## 2. Executive summary

1. Fresh guarded run `run-7b9d1713…`: complete=true, **2396 PASS / 2 FAIL**, khớp tuyệt đối với run khai báo `run-44c3751c…`; source_manifest hai run giống hệt.
2. Hai FAIL duy nhất là `/mobile` và `/mobile/tasks` trả 500 (expected 200) — được ghi FAIL thật, không bị ẩn; nguyên nhân xác nhận trong source (`routes/mobile.py:73-79` dùng `Task.trang_thai`, `Task.id` không tồn tại).
3. Replacement invariant 4B2 được kiểm chứng **trong code**: PENDING commit trước business commit; business commit + reload + exact revalidation + activate/supersede nằm trong cùng một `BEGIN IMMEDIATE` của sidecar; old ACTIVE chỉ bị revoke trong `activate_binding`.
4. Không phát hiện test bị skip, expectation bị nới, hay test bị xóa giữa các run (đối chiếu tên test + expected vô hướng qua 15 cặp run).
5. Production integrity: 10 file được bảo vệ + `qlcv_khach_hang.db` có SHA-256/size/mtime_ns giống hệt trước/sau; `private_metadata/` vẫn không tồn tại.
6. Log trung tâm có 16 mục stale/mâu thuẫn (header, §1, §2, §3, §6, §8, §9, §11, §12, §13) — chủ yếu vì chỉ thêm section cuối mà không cập nhật phần đầu.
7. Phát hiện mới: 3 × P2 (stale PENDING khóa slot; change_password tạo lại ADMIN; rủi ro SW trên browser thật), 3 × P3.
8. SEC-01: đồng ý BLOCKED/OPEN; có phương án hẹp hơn (chặn quản lý tài khoản reserved ở default tenant + sửa biểu thức `is_nsx_master_admin`), nhưng vẫn cần USER duyệt vì đổi authorization.
9. Đồng ý SEC-04 vẫn OPEN; SEC-05 FIXED trong phạm vi Task đã duyệt.
10. Không bắt đầu batch nào; không sửa file nào ngoài báo cáo này.

---

## 3. Batch decisions

| Batch | Decision | Lý do 1 dòng | Evidence chính |
|---|---|---|---|
| 3D | APPROVE | Chỉ sửa harness; source_manifest 3C→3D không đổi; SEC05 530/0 tái lập | `run-601a577a…` 677/2; manifest diff 3C→3D = `[]`; fresh SEC05 530/530 |
| 4B1 | APPROVE | Registry foundation fail-closed; về sau được thay bởi v2/v3 nhưng 77 assertions vẫn PASS | `run-c00b7009…` 754/2, REGISTRY 77; fresh REGISTRY 77/77 |
| 4B2 | APPROVE | Thứ tự PENDING→commit→revalidate→activate đúng trong code; không có critical condition; có NEW-01 (P2, availability) | §4; `run-a81a2e79…` 1092/2; fresh B4B2 338/338 |
| 4B3 | APPROVE | Gateway kiểm tra registry + live object + ACL + size/hash trước khi trả bytes; Nginx thật/symlink thật chưa kiểm chứng (đã khai) | `file_access_service.py:154-179`; `run-9dc4c7d9…` 1623/2; fresh gateway 531/531 |
| 4B4 | APPROVE (phạm vi mô phỏng) | Logic SW đúng theo source + Node VM; real browser NOT RUN → không đủ cho rollout (NEW-03) | `static/sw.js:74-103`; `run-7b3e6a1e…` 1937/2; fresh PWA 314/314 |
| 4B5A | APPROVE | Provenance v3 có CHECK constraint SQL + kiểm tra ngữ nghĩa; 234/0; attempt-1 bị loại đúng quy trình | `file_registry.py:137-143,76-88`; `run-56914c09…` 2171/2; fresh 234/234 |
| 4B5 | APPROVE (tooling/synthetic) | Discovery read-only + apply chỉ trong sandbox; log trung tâm quá sơ sài (3 attempt chỉ ghi trong audit v3) | `legacy_discovery.py:340-350`; `run-44c3751c…` 2396/2; fresh 225/225 |

---

## 4. Critical rejection conditions & Replacement invariant

### 4.1 Critical rejection conditions (checklist 4B2)

| Điều kiện | Kết quả | Evidence |
|---|---|---|
| Revoke old ACTIVE trước business commit hoặc trước exact revalidation thành công | NOT FOUND | Old ACTIVE chỉ bị revoke ở `file_registry.py:248-249` (trong `activate_binding`) và `file_binding_service.py:97-99` (nhánh clear) — cả hai đều chạy SAU `mutate()` + reload + so sánh field (`file_binding_service.py:88-93`). Test: `B4B2 REPLACE preparing B preserves A`, `B4B2 FAILURE commit old ACTIVE`, `B4B2 FAILURE revalidation old ACTIVE`, `B4B2 FAILURE activation old ACTIVE`, `B4B2 FAILURE clear old ACTIVE preserved` — tất cả PASS trong fresh run |
| Client URL tự trở thành trusted binding/ownership authority | NOT FOUND | URL chỉ là locator; phải có registry record cùng tenant, provenance hợp lệ, state hợp lệ, uploader khớp hoặc own_slot/shared (`file_binding_service.py:50-74`); URL mới chưa đăng ký bị từ chối (`:54-56`). Test `B4B2 BIND … unregistered`, `Document unregistered` PASS |
| Failed business commit tạo ACTIVE | NOT FOUND | `mutate()` lỗi → exception trước `activate_binding` → rollback sidecar + `revoke_pending` (`:88-90, :105-111`). Test `B4B2 FAILURE commit replacement never ACTIVE` PASS (actual `[]`, expected `[]`) |
| Concurrent replacements tạo >1 ACTIVE cùng exact slot | NOT FOUND | Unique partial index `binding_slot_active` (`file_registry.py:152`) + `binding_slot_pending` (`:153`) + `_validate` bắt buộc index tồn tại (`:66-74`). Test `B4B2 CONCURRENCY replacement exactly one ACTIVE` = 1, `B4B2 CONCURRENCY PROCESS one final ACTIVE generation` PASS (2 process độc lập) |
| Nới test/security expectation, skip assertion, đổi fixture để che lỗi | NOT FOUND | Đối chiếu tên test + expected vô hướng giữa 15 cặp run (§7): không test nào bị xóa; expected vô hướng chỉ đổi ở schema version (1→2→3) và giá trị động (UUID/URL upload). Fixture SEC05 đổi từ URL giả sang upload thật (siết chặt, không nới) |
| Đánh dấu SEC-04 FIXED sau 4B2 | NOT FOUND | Log §3 dòng 92: SEC-04 `OPEN`; mọi section sau đều ghi OPEN |

### 4.2 Trích code nguyên văn

**a. Prepare PENDING — `services/file_registry.py:209-230`**

```python
209    def create_pending_binding(self, file_id, tenant_id, object_kind, object_id, field_slot, generation=1, *, replacement=False):
210        tenant_id, object_id, field_slot = map(_text, (tenant_id, object_id, field_slot))
211        if object_kind not in ('TASK', 'DOCUMENT', 'PERSONAL') or isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
212            raise RegistryError("Invalid binding")
213        with self._connection(mutation=True) as conn:
214            file = conn.execute('SELECT * FROM files WHERE file_id=? AND tenant_id=?', (file_id, tenant_id)).fetchone()
215            if not file or not self.valid_provenance(dict(file)) or file['classification'] == 'UNKNOWN' or file['state'] not in ('UNBOUND','BOUND') or self.expired_unbound(dict(file)):
216                raise RegistryError("File cannot be bound")
217            old = conn.execute("SELECT * FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=? AND state IN ('PENDING','ACTIVE') ORDER BY CASE state WHEN 'PENDING' THEN 0 ELSE 1 END", (tenant_id, object_kind, object_id, field_slot)).fetchone()
218            if old:
219                if old['file_id'] == file_id and (replacement or old['generation'] == generation):
220                    return old['binding_id']
221                if old['state']=='PENDING' or not replacement:
222                    raise RegistryError("Binding conflict")
223            if replacement:
224                last=conn.execute('SELECT COALESCE(MAX(generation),0) FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=?',(tenant_id,object_kind,object_id,field_slot)).fetchone()[0]
225                generation=last+1
226            binding = str(uuid.uuid4())
227            now = _now()
228            conn.execute('INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?,?,?)',
229                         (binding,file_id,tenant_id,object_kind,object_id,field_slot,generation,'PENDING',now,now))
230            return binding
```

Nhận xét: ĐÚNG thứ tự. PENDING được INSERT và COMMIT trong transaction riêng (`_connection(mutation=True)` → `BEGIN IMMEDIATE` … `commit`) **trước** khi gọi business callback. Old ACTIVE không bị chạm. Lưu ý dòng 217/221: nếu slot đang có một PENDING cũ của file khác thì từ chối — đây là nguồn gốc NEW-01.

**b. Business commit + reload + exact revalidation — `services/file_binding_service.py:76-100`**

```python
 76        pending=None
 77        try:
 78            if record:
 79                pending=self.registry.create_pending_binding(record['file_id'],*slot,replacement=True)
 80                receipt=self.registry.get_binding(pending,self.tenant)
 81            # Even clear/external/legacy mutations serialize against registry slots
 82            # when sidecar exists. No sidecar creation for legacy or external links.
 83            if self.registry.path.exists():
 84                with self.registry._connection(mutation=True) as conn:
 85                    live=self.registry.slot_bindings(*slot,connection=conn)
 86                    if any(b['state']=='PENDING' and b['binding_id']!=pending for b in live):
 87                        raise RegistryError('Another replacement is reserved')
 88                    result=mutate()
 89                    if not result.get('success'):
 90                        raise RegistryError('Business mutation failed')
 91                    persisted=self.reload(model,object_id)
 92                    if persisted is None or (getattr(persisted,field) or '')!=url:
 93                        raise RegistryError('Post-commit binding revalidation failed')
 94                    if pending:
 95                        self.registry.activate_binding(pending,self.tenant,expected_generation=receipt['generation'],connection=conn)
 96                    else:
 97                        for binding in live:
 98                            if binding['state']=='ACTIVE':
 99                                conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE binding_id=?",(_now(),binding['binding_id']))
100                    return result
```

`reload` (`:42-44`): `self.db.expire_all()` rồi `select(...).execution_options(populate_existing=True)` → đọc lại từ DB, không dùng object cache.

Nhận xét: ĐÚNG thứ tự. Trong cùng một `BEGIN IMMEDIATE` của sidecar (dòng 84): kiểm tra không có PENDING cạnh tranh → business commit (`mutate()` gọi `db.commit()`) → reload thật → so sánh **chính xác** field đã lưu với URL đã được xác thực → mới activate. Business DB và sidecar là hai SQLite riêng: commit business (dòng 88) không atomic với commit sidecar (khi thoát `with`, dòng 100) — log đã khai đúng giới hạn này.

**c. Activate + supersede — `services/file_registry.py:232-251` (transaction mở ở `:103-107`)**

```python
103            if mutation:
104                conn.execute('BEGIN IMMEDIATE')
105            yield conn
106            if mutation:
107                conn.commit()
...
232    def activate_binding(self, binding_id, tenant_id, *, expected_generation=None, connection=None):
233        if connection is None:
234            with self._connection(mutation=True) as conn:
235                return self.activate_binding(binding_id,tenant_id,expected_generation=expected_generation,connection=conn)
236        conn=connection
237        binding = conn.execute('SELECT * FROM bindings WHERE binding_id=? AND tenant_id=?', (binding_id,tenant_id)).fetchone()
238        if not binding or binding['state'] not in ('PENDING','ACTIVE') or (expected_generation is not None and binding['generation']!=expected_generation):
239            raise RegistryError("Invalid binding transition")
240        file = conn.execute('SELECT * FROM files WHERE file_id=? AND tenant_id=?', (binding['file_id'],tenant_id)).fetchone()
241        if not file or not self.valid_provenance(dict(file)) or file['classification']=='UNKNOWN' or file['state'] not in ('UNBOUND','BOUND') or self.expired_unbound(dict(file)):
242            raise RegistryError("File cannot activate")
243        if binding['state']=='ACTIVE':
244            return
245        old=conn.execute("SELECT * FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=? AND state='ACTIVE'",(tenant_id,binding['object_kind'],binding['object_id'],binding['field_slot'])).fetchone()
246        if old and old['generation']>=binding['generation']:
247            raise RegistryError("Stale binding generation")
248        if old:
249            conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE binding_id=?",(_now(),old['binding_id']))
250        conn.execute("UPDATE bindings SET state='ACTIVE',updated_at=? WHERE binding_id=?", (_now(),binding_id))
251        conn.execute("UPDATE files SET state='BOUND',version=version+1 WHERE file_id=?", (file['file_id'],))
```

Nhận xét: ĐÚNG. Gọi với `connection=conn` từ (b) nên revoke old (249) + activate new (250) + BOUND (251) nằm trong CÙNG `BEGIN IMMEDIATE` và commit một lần. Kiểm tra generation (238, 246) ngăn kích hoạt binding cũ/stale. Re-check provenance/state/expiry ngay trong transaction (241).

**d. Compensation khi lỗi — `services/file_binding_service.py:105-114` và `services/file_registry.py:302-305`**

```python
105        except Exception as exc:
106            self.db.rollback()
107            if pending:
108                try:
109                    self.registry.revoke_pending(pending,self.tenant)
110                except RegistryError:
111                    pass  # Stale PENDING is not authority; reconciliation required.
112            if isinstance(exc,RegistryError):
113                raise
114            raise RegistryError('Business binding operation failed') from exc
...
302    def revoke_pending(self, binding_id, tenant_id):
303        # Compensation never revokes an ACTIVE retry or someone else's slot.
304        with self._connection(mutation=True) as conn:
305            conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE binding_id=? AND tenant_id=? AND state='PENDING'",(_now(),binding_id,tenant_id))
```

Nhận xét: ĐÚNG về an toàn: chỉ revoke đúng binding còn `PENDING` (điều kiện `state='PENDING'`), không bao giờ revoke ACTIVE. Khi exception xảy ra bên trong `with` của (b), context manager rollback toàn bộ sidecar transaction (`file_registry.py:111-113`), nên old ACTIVE còn nguyên. Hạn chế: nếu `revoke_pending` lỗi (busy 300 ms, crash), PENDING bị bỏ lại vĩnh viễn và **khóa slot** (NEW-01). `self.db.rollback()` (106) vô tác dụng nếu business đã commit — đúng như log khai "business URL có thể đã lưu nhưng không ACTIVE".

**e. Kiểm tra trong gateway trước khi trả bytes — `services/file_access_service.py:141-179`**

```python
143        raw=request.scope.get('raw_path',b'').decode('ascii')
144        canonical='/static/uploads/'+storage_name
145        if not storage_basename(storage_name) or raw!=quote(canonical,safe='/'):
146            return denied()
147        session=AuthService.get_session(request)
148        if not session:
149            return denied(401)
150        actor=task_policy.actor_from_session(db,session)
151        tenant=session.get('company_mst')
152        if actor is None or not isinstance(tenant,str) or not tenant:
153            return denied(401)
154        registry=FileRegistry()
155        row,bindings=registry.access_snapshot(tenant,Config.UPLOAD_STORAGE_ROOT_ID,storage_name)
156        if not row or not registry.valid_provenance(row) or row['classification'] not in ('PRIVATE','VERIFIED_LEGACY') or row['state'] not in ('UNBOUND','BOUND'):
157            return denied()
158        if row['state']=='UNBOUND':
159            if (row['provenance_type']!='VERIFIED_UPLOADER' or row['classification']!='PRIVATE' or row['uploader_id']!=actor.ma
160                    or not row['expires_at'] or registry.expired_unbound(row)):
161                return denied()
162        else:
163            allowed=False
164            for binding in bindings:
165                if binding['tenant_id']!=tenant:
166                    continue
167                if binding['object_kind']=='TASK' and binding['field_slot'] in ('file_giao_viec','file_bao_cao'):
168                    obj=task_policy.load_task(db,binding['object_id'])
169                    allowed=bool(obj and getattr(obj,binding['field_slot'])==canonical and task_policy.can_view_task(actor,obj))
170                elif binding['object_kind']=='DOCUMENT' and binding['field_slot']=='link_file':
171                    from routes.documents import readable_documents_query
172                    obj=readable_documents_query(db,session).filter(Document.ma_tl==binding['object_id']).first()
173                    allowed=bool(obj and obj.link_file==canonical)
174                if allowed:
175                    break
176            if not allowed:
177                return denied()
178        content,modified=physical_bytes(row)
179        return file_response(request,row,content,modified)
```

Nhận xét: ĐÚNG thứ tự: canonical path → session → actor tenant-local → registry (read-only snapshot, chỉ ACTIVE binding) → UNKNOWN/WRITING/REVOKED deny → UNBOUND chỉ uploader + chưa hết hạn → BOUND cần binding ACTIVE + object sống + field hiện tại khớp chính xác + ACL hiện tại → cuối cùng mới đọc file (`physical_bytes`, `:62-84`, kiểm tra lstat/reparse, opened-handle realpath, size, SHA-256). Range/ETag/304 xử lý trong `file_response` chỉ sau đó. Vì gateway luôn kiểm tra field sống, trường hợp "business đã commit nhưng chưa ACTIVE" chỉ gây mất khả dụng, không gây lộ dữ liệu.

### 4.3 Replacement invariant — đối chiếu từng trạng thái

| Trạng thái invariant | Code | Test (fresh run, đều PASS) |
|---|---|---|
| Initial A ACTIVE | — | `B4B2 BIND file BOUND` |
| Prepare: A ACTIVE, B PENDING | (a) dòng 217-229 không chạm ACTIVE | `B4B2 REPLACE preparing B preserves A`, `B4B2 REPLACE reserved B PENDING` |
| Business failure: A ACTIVE, B ≠ ACTIVE | (b) 88-90 → (d) | `B4B2 FAILURE commit old ACTIVE`, `B4B2 FAILURE commit replacement never ACTIVE` |
| Commit PASS, revalidation FAIL: A ACTIVE, B ≠ ACTIVE | (b) 91-93 → rollback sidecar | `B4B2 FAILURE revalidation old ACTIVE`, `B4B2 FAILURE revalidation replacement never ACTIVE`, `B4B2 FAILURE postcommit business remains committed` |
| Commit + revalidation PASS: A REVOKED, B ACTIVE | (c) 249-250 | `B4B2 REPLACE B ACTIVE`, `B4B2 REPLACE A exact slot revoked`, `B4B2 REPLACE A child preserved` |
| Concurrent B/C: ≤1 ACTIVE, khớp field | unique index `:152-153`; (b) 86 | `B4B2 CONCURRENCY replacement exactly one ACTIVE`, `… ACTIVE matches persisted URL`, `… PROCESS one final ACTIVE generation` |

### 4.4 Giới hạn non-atomic business DB ↔ sidecar

- API có báo failure: route Task bắt `RegistryError` → `db.rollback()` → `_denied()` (`routes/tasks.py:203-205, 233-235, 266-268`); Document trả `{'success':False,'message':'Không thể xác thực/lưu liên kết tệp.'}` (`routes/documents.py:85-87`). Test `B4B2 FAILURE revalidation response denied` (success=False) PASS.
- Reconciliation risk được log nêu đúng (log dòng 1566-1575): "Fault after business commit may leave new business URL persisted but NO new ACTIVE binding; old ACTIVE remains… reconciliation/custodian tooling not implemented."
- Thiếu sót trong cách log mô tả: (1) thông báo trả về cho Task là "Không có quyền hoặc dữ liệu không hợp lệ." dù dữ liệu đã lưu (NEW-04); (2) stale PENDING không chỉ "unusable" mà còn khóa slot (NEW-01).

---

## 5. Log inconsistencies

| # | Mục trong log | Nội dung đang ghi | Giá trị đúng theo artifact | Artifact chứng minh |
|---|---|---|---|---|
| 1 | Header dòng 3 | `Updated: 2026-10-01 10:51 +07:00` | File có nội dung tới 13:45 (section Resumed 4B5 và SEC-01) | mtime log 13:45:40; audit_codex_v3 tạo 12:07:56, v4 13:45:16 |
| 2 | Header dòng 5-7 | `Latest completed current-source run: Batch4B5A run-56914…, 234/0 …; full2171/2` | Latest completed: Resumed 4B5 `run-44c3751c…`, 2396 PASS / 2 FAIL, targeted 225/0 | `run-44c3751c…/runtime_results.json`: complete=true, 2398 results, 2396 pass |
| 3 | Header dòng 7 | `full discovery/review mapping remains unimplemented` | Discovery/review tooling đã implement (`services/legacy_discovery.py`), 225/0 | fresh + claimed run: nhóm `B4B5` = 225 |
| 4 | §1 dòng 49-53 | `Batch4B4 … SEC04 OPEN; 4B5 verified legacy resolution NOT STARTED` | 4B5A COMPLETE, 4B5 tooling COMPLETE; SEC-04 vẫn OPEN | như #2, #3 |
| 5 | §2 bảng | Hàng cuối là Batch4B4 (`4B5 not started`); không có hàng 4B5A, 4B5, SEC-01 | Cần thêm 4B5A (234/0, 2171/2), 4B5 (225/0, 2396/2), SEC-01 BLOCKED | `run-56914c09…`, `run-44c3751c…`, `.test_runtime/audit-sec01-blocked/integrity.json` |
| 6 | §3 hàng SEC-04 | `Current PWA314/0, gateway531/0; full1937/2 …` / `Verified legacy/UNKNOWN resolution remains4B5, not started` | Current full 2396/2; 4B5A 234/0; 4B5 225/0; production UNKNOWN = 2 file, activated = 0 | `run-44c3751c…`, `production_legacy_inventory.json` |
| 7 | §3 hàng SEC-01 | Mô tả gốc; không nhắc root cause/BLOCKED | Root cause chi tiết + BLOCKED (audit v4) | audit_codex_v4.md §7 |
| 8 | §6 Files Modified | Chỉ có Phase A, Batch 1, 2A, 2B.0, 2B.1, 4B2, 4B3, 4B4 | Thiếu 3B (routes/tasks.py, task_service.py, NEW task_policy.py), 3D (tests), 4B1 (NEW file_registry.py, config.py), 4B5A (file_registry, file_binding_service, file_access_service, NEW legacy_provenance), 4B5 (NEW legacy_discovery, legacy_provenance) | source_manifest diff: 3D→4B1 `['config.py','services\\file_registry.py']`; 4B4→4B5A `[file_access_service, file_binding_service, file_registry, legacy_provenance]`; 4B5A→4B5 `[legacy_discovery, legacy_provenance]` |
| 9 | §8 dòng 170-172 | `Latest completed run: Batch4B4 … run-7b3e6a1e… 1937 PASS / 2 FAIL` | Latest: `run-44c3751c…` 2396/2 | như #2 |
| 10 | §9 dòng 279 | `Latest Batch4B2 fresh run: all10 protected …` | Lần kiểm tra integrity gần nhất do Codex là SEC-01 audit (`audit-sec01-blocked/integrity.json`) và 4B5 run | các integrity.json tương ứng |
| 11 | §9 dòng 293 | `Current Batch4B4 completed runtime integrity report: run-7b3e6a1e…` | Current: `run-44c3751c…/integrity.json` | như trên |
| 12 | §11 dòng 344-347 | `No … legacy onboarding work has occurred` | Legacy provenance (4B5A) + discovery/review tooling (4B5) đã thực hiện (synthetic) | audit v2, v3 |
| 13 | §12 dòng 351-354 | `Current Batch4B4 is COMPLETE … Batch4B5 … NOT STARTED` | Next action thực tế: USER quyết định MASTER boundary (SEC-01) và chính sách 2 file UNKNOWN (4B5) | log dòng 2076, 2089 |
| 14 | §13 Change History | Bảng dừng ở 4B4; các entry 4B5-stop/4B5A/4B5/SEC-01 nằm sau đoạn "For each future…", dùng heading cấp `#` (dòng 1943) phá cấu trúc | Cần thêm 4 hàng vào bảng §13 | log dòng 1937-1943 |
| 15 | Section Resumed 4B5 (dòng 2067-2076) | Chỉ 10 dòng; không liệt kê 3 attempt run | Có 3 attempt: `run-93284f08…` (incomplete, 1901 results), `run-d5f8dec9…` (incomplete, 1976), `run-4bad803e…` (complete 2393/2, B4B5 222) — chỉ được ghi trong audit v3 §13 | runtime_results.json của 3 run (đã đọc) |
| 16 | Section 4B5A dòng 2026-2029 | Attempt-1 bị loại vì "provenance validation was additionally applied to binding mutation and assertions were expanded" | Source diff attempt-1→final chỉ là `services\file_registry.py` (validation nằm trong `create_pending_binding/activate_binding` của registry, không phải `file_binding_service.py`). Ngoài ra 4 test `PWA_4B3_INTEGRATION LEGACY approved …` được **đổi nhãn** thành `PROVENANCE_PWA_INTEGRATION` (PWA_4B3_INTEGRATION 56→52, PROVENANCE_PWA_INTEGRATION 2→7) — log không nêu | so sánh `run-7c6418a4…` và `run-56914c09…` |

Kiểm tra mọi run directory được log trích dẫn (tồn tại + số liệu khớp):

| Run | Log khai | Artifact thực tế | Khớp? |
|---|---|---|---|
| run-d995521808… (Batch 1) | 52 checks, 49 PASS, 3 FAIL | 52 / 49 / 3 (anonymous upload 200, 2 mobile) | ✓ |
| run-e387d8e5… (2A) | 136 / 134 | 136 / 134 / 2 mobile | ✓ |
| run-46b82e21… (2B.1) | 149 / 147 | 149 / 147 / 2 mobile | ✓ |
| run-66c003f4… (3C) | runtime_results.json absent | absent (chỉ integrity/preflight/source_manifest) | ✓ |
| run-601a577a… (3D) | 677 / 2, SEC05 530 | complete, 679 / 677 / 2, SEC05 530 | ✓ |
| run-9cfa2737… (4B1 lần 1) | registry 72, 749/2 | 751 / 749 / 2, REGISTRY 72 | ✓ |
| run-c00b7009… (4B1) | registry 77, 754/2 | 756 / 754 / 2, REGISTRY 77 | ✓ |
| run-35379589… (4B2 attempt) | dừng ở JSON serialization | complete=false, 809 results, 0 FAIL | ✓ |
| run-7dc71548… (4B2 attempt) | 1079/2 | 1081 / 1079 / 2 | ✓ |
| run-4c01d965… (4B2 attempt) | dừng ở fixture | complete=false, 1028 | ✓ |
| run-a81a2e79… (4B2) | 1092/2, 4B2 338 | 1094 / 1092 / 2, B4B2 338 | ✓ |
| run-e48fba78… (4B3 attempt) | CSS/JS 404 + 2 mobile | 1576 / 1572 / 4 (2 GATEWAY_STATIC_BYPASS public asset 404 + 2 mobile) | ✓ |
| run-c692f871… (4B3 attempt) | gateway 482, 1574/2 | GATEWAY 482, 1576 / 1574 / 2 | ✓ |
| run-9dc4c7d9… (4B3) | 1623/2, gateway 531 | 1625 / 1623 / 2, GATEWAY 531 | ✓ |
| run-4acf8eac… / run-36dacce0… / run-dc034ef6… (4B4 standalone) | 239 / 240 / 244 | pwa_results 239/239, 240/240, 244/244 | ✓ |
| run-cd820336… (4B4 attempt) | 310 targeted, 1933/2 | PWA 310, 1935 / 1933 / 2 | ✓ |
| run-7b3e6a1e… (4B4) | 1937/2, PWA 314 | 1939 / 1937 / 2, PWA 314 (Node 278 + live 36) | ✓ |
| run-7c6418a4… (4B5A attempt) | 2153/2 | 2155 / 2153 / 2 | ✓ |
| run-56914c09… (4B5A) | 2171/2, 234/0 | 2173 / 2171 / 2; 16 nhóm cộng = 234 | ✓ |
| run-44c3751c… (4B5) | 2396/2, 225/0 | 2398 / 2396 / 2, B4B5 225 | ✓ |

Tất cả run directory được trích dẫn đều tồn tại và số liệu khớp. Mâu thuẫn chỉ nằm ở các section tóm tắt không được cập nhật.

---

## 6. Checklist results

Quy ước: PASS = có evidence code và/hoặc test fresh; FAIL = có bằng chứng sai; INCOMPLETE = chưa/không thể kiểm chứng.
"fresh" = `run-7b9d1713…/runtime_results.json`.

### 6.1 CODEX_REVIEW_CHECKLIST.md (Batch 4B2)

| Mục | Kết quả | Evidence |
|---|---|---|
| 1. Scope code chỉ 7 production file | PASS | source_manifest 4B1→4B2: `config.py, routes/documents.py, routes/tasks.py, services/drive_service.py, services/file_binding_service.py, services/file_registry.py, services/task_service.py` |
| 1. Không sửa DocumentService/task_policy/models/app/templates/static | PASS | Các file đó không có trong diff manifest 4B1→4B2 |
| 1. Phân biệt 4B2 với thay đổi có sẵn | PASS | Log dòng 1608-1611 nêu tracked diff là cumulative |
| 2. Schema version rõ ràng ("hiện tại là v2") | PASS (lịch sử) / stale | Tại 4B2 là v2; hiện `file_registry.py:29` `VERSION = 3` (4B5A) |
| 2. Version không tương thích fail closed, không reset | PASS | `file_registry.py:59-74`; test `B4B2 SCHEMA v1 explicit migration error`, `B4B2 SCHEMA incompatible bytes preserved` |
| 2. ≤1 ACTIVE + ≤1 PENDING mỗi slot | PASS | `file_registry.py:152-153` |
| 2. Locator unique; generation hợp lệ | PASS | `UNIQUE(storage_root_id,storage_name)` `:144`; `CHECK(generation > 0)` `:148` |
| 2. foreign_keys, busy timeout, BEGIN IMMEDIATE | PASS | `:99-104` |
| 2. Không ALTER business DB | PASS | Không có ALTER trong file_registry/binding; sidecar riêng |
| 2. Import không tạo registry; path ngoài static/LOCAL_DOCS | PASS | `config.py:51-55`; `file_registry.py:40-57`; test `REGISTRY lazy import no sidecar` |
| 3. Validate auth/tenant/extension trước authority | PASS | `routes/documents.py:215-220`; `drive_service.py:76-86` |
| 3. WRITING trước exclusive write | PASS | `drive_service.py:100-102` (`register_writing` rồi `open(filepath,"xb")`) |
| 3. Không overwrite; collision retry | PASS | `drive_service.py:92-110`; BUG10 13/13 fresh |
| 3. Size/SHA-256 từ bytes thật; UNBOUND sau write | PASS | `drive_service.py:112-131` (fsync rồi `complete_unbound`) |
| 3. Lỗi → không trả success, không record usable | PASS | `drive_service.py:134-141` (mark_revoked); test `B4B2 FAILURE physical failure no usable metadata` |
| 3. Giữ URL/name contract; file_id additive | PASS | `routes/documents.py:223` |
| 4. Tenant từ session; client không cấp authority | PASS | `routes/documents.py:220`, `task_policy.py:16-22` |
| 4. Không fallback tenant khác | PASS | `file_binding_service.py:58` (`record['tenant_id']!=self.tenant` → deny) |
| 5. UNBOUND: cùng tenant + đúng uploader + chưa hết hạn; ADMIN không override | PASS | `file_binding_service.py:58,68-69`; gateway `:158-161` |
| 5. Expiry 24h, không xóa bytes | PASS | `file_registry.py:189`; test `REGISTRY expiry 24 hours` |
| 6. Authorization trước registry mutation | PASS | routes/tasks.py:180-199 trước `save_task_data`; documents.py:59-61 |
| 6. PENDING trước business; reload; exact match trước ACTIVE | PASS | §4.2 (a)(b) |
| 7. Fault injection mọi boundary | PASS | 33 test `B4B2 FAILURE …` PASS fresh |
| 7. Compensation chỉ revoke still-PENDING | PASS | `file_registry.py:305` |
| 7. Stale PENDING không cấp read authority | PASS | gateway chỉ đọc `state='ACTIVE'` (`file_registry.py:281-283`) |
| 7. Không giả atomic; API báo failure; nêu reconciliation risk | PASS (có ghi chú) | §4.4; thông báo lỗi gây hiểu nhầm (NEW-04) |
| 8. Replacement giữ A ACTIVE khi B PENDING | PASS | §4.3 |
| 9. Activate + supersede cùng transaction | PASS | §4.2 (c) |
| 9. Clear chỉ revoke slot sau commit/reload | PASS | `file_binding_service.py:96-99`; test `B4B2 REPLACE clear exact slot`, `B4B2 FAILURE clear old ACTIVE preserved` |
| 10. Concurrent B/C thread + process | PASS | `B4B2 CONCURRENCY …` 12/12 |
| 11. Idempotent retry | PASS | `file_registry.py:219-220`; `B4B2 CONCURRENCY exact reservation retry`, `… exact retry metadata unchanged` |
| 12. Task file_giao_viec dùng SEC-05 CREATE/EDIT | PASS | `routes/tasks.py:180-185`, `task_service.py:169-170` |
| 13. file_bao_cao slot riêng, REPORT | PASS | `task_service.py:202-203`; `routes/tasks.py:187` chặn `file_bao_cao` trong generic edit |
| 14. Forward: binding child riêng sau commit; legacy không tạo claim | PASS | `task_service.py:253-255`, `file_binding_service.py:63-67`; test `B4B2 BIND legacy child no trusted binding` |
| 15. Document link_file binding, revalidation | PASS | `routes/documents.py:72-87`; test `B4B2 FAILURE Document revalidation denied` |
| 16. Cross-tenant denial | PASS | `file_binding_service.py:58`; test `report foreign tenant` |
| 17. UNKNOWN không auto-claim; URL mới chưa đăng ký bị từ chối | PASS | `file_binding_service.py:54-59` |
| 18. External/local_docs giữ nguyên; alias absolute bị từ chối | PASS | `file_binding_service.py:28-36` |
| 19. Denied-write zero mutation | PASS | `tests/runtime_sandbox.py:619-641` (task_write so sánh DB, files, registry, provider) |
| 20. Production integrity | PASS | §9 |
| 21. SEC-05 530/0, fixture dùng upload thật | PASS | fresh SEC05 530/530; `tests/runtime_sandbox.py:658-659` dùng `local_upload(...)` |
| 22. SEC-03 84/0 | PASS | fresh 84/84 |
| 23. BUG-10 13/0 | PASS | fresh 13/13 |
| 24. Core smoke + 11 routers | PASS | preflight routers 11/11; 50 smoke check (gồm 2 mobile FAIL) |
| 25. Mobile baseline ghi đúng | PASS | §7.4 |
| 26. SEC-04 OPEN | PASS | log §3 |
| 27. Không gateway/static/PWA trong 4B2 | PASS | manifest 4B1→4B2 không có app.py/sw.js |

### 6.2 CODEX_REVIEW_CHECKLIST_4B3.md

| Mục | Kết quả | Evidence |
|---|---|---|
| Route/static mount ordering | PASS | `app.py:63-65` route `/static/uploads/{storage_name:path}` khai báo trước mount `/static` `app.py:83-88` |
| /static/uploads direct bypass | PASS | fresh GATEWAY_AUTH 12/12, GATEWAY_FAIL_CLOSED 38/38 |
| Parent /static bypass | PASS | `app.py:70-81` (`any(p.casefold()=='uploads' …)`, resolved-root check); GATEWAY_STATIC_BYPASS 42/42 |
| Nginx source bypass audit | PASS (source) | `nginx_vps_default.conf`, `vps_default.conf` chỉ `proxy_pass http://127.0.0.1:8081`; không có `alias`/`root` uploads |
| Actual production Nginx | INCOMPLETE | Không có quyền truy cập máy chủ; `vps_default.conf` còn `location /qlcv/ { proxy_pass http://127.0.0.1:8081/; }` (strip prefix) chưa được kiểm thử với gateway raw-path check `file_access_service.py:145` |
| Signed-session auth / tampered session | PASS | GATEWAY_AUTH; stdout fresh run có "Tampered signed cookie detected!" từ test |
| Session expiration/revocation | INCOMPLETE | SEC-02 OPEN; `auth_service.py:240-249` không kiểm tra hạn/thu hồi |
| Canonical tenant/actor | PASS | `file_access_service.py:150-153`; GATEWAY_TENANT 24/24 |
| Registry bắt buộc; UNKNOWN deny kể cả ADMIN | PASS | `:155-157`; GATEWAY_UNBOUND 30/30 |
| UNBOUND uploader-only, expiry | PASS | `:158-161` |
| ACTIVE binding chưa đủ; live object + field + ACL | PASS | `:164-177`; GATEWAY_LIVE_REVALIDATION 32/32 |
| Task READ ACL / Document READ | PASS | `task_policy.can_view_task`; `readable_documents_query` (`routes/documents.py:104-139`) dùng chung với library |
| Multiple-binding union; foreign binding | PASS | `:164-175` (`continue` khi tenant khác) |
| Traversal/basename/Windows/UNC | PASS | `storage_basename` `:29-33`; GATEWAY_PATH 16/16 |
| Realpath / opened-handle | PASS | `:62-84` |
| Genuine symlink/junction | INCOMPLETE | Đã khai NOT FULLY TESTABLE (không có quyền symlink Windows) |
| Size/SHA-256 integrity | PASS | `:77-83`; GATEWAY_INTEGRITY 24/24 |
| GET/HEAD/Range/Conditional sau auth | PASS | `file_response` `:87-138` chỉ được gọi ở `:179`; GATEWAY_HTTP 46/46 |
| Existence disclosure / no redirect | PASS | `denied()` `:24-26` JSON đồng nhất |
| Inline/download filename/type | PASS | `:92-98` |
| Cache headers private,no-store | PASS | `HEADERS` `:20-21` |
| SW Cache API | — (thuộc 4B4) | xem 6.3 |
| Registry unavailable/corrupt fail closed; readonly open | PASS | `file_registry.py:264-295` (`mode=ro`, `query_only`) |
| Public CSS/JS | PASS | GATEWAY_STATIC_BYPASS; lịch sử: attempt `run-e48fba78…` có 2 FAIL public asset 404, đã sửa trong app.py, không đổi expected (§7.5) |
| Zero mutation | PASS | GATEWAY_ZERO_MUTATION 186/186 |
| Regression 4B2/registry/SEC05/SEC03/BUG10/Core/routers | PASS | fresh: 338/77/530/84/13; routers 11/11 |
| Mobile baseline | PASS | 2 FAIL nguyên văn §8 |
| Production integrity; approved source scope | PASS | §9; manifest 4B2→4B3 = `app.py, routes/documents.py, file_access_service.py, file_registry.py` |
| SEC-04 OPEN | PASS | log §3 |

### 6.3 CODEX_REVIEW_CHECKLIST_4B4.md

| Mục | Kết quả | Evidence |
|---|---|---|
| SW architecture audited; private namespace | PASS | `static/sw.js:5-18` (`isPrivateUpload` decode tối đa 3 lần, chuẩn hóa `\`, `//`, lowercase) |
| Private classification trước cache lookup | PASS | `sw.js:80-83` nhánh private/dynamic trả về trước nhánh public |
| Private network-only; no match/put/add | PASS | `sw.js:81` `event.respondWith(fetch(request, { cache: 'no-store' }))`; PWA_NETWORK_ONLY 77/77, PWA_NO_PRIVATE_WRITE 47/47 |
| No private offline fallback | PASS | Không có catch cho nhánh private → reject; PWA_OFFLINE_PRIVATE 22/22 |
| Old cache purge, chỉ app-owned | PASS | `sw.js:46-72`, regex `^qlcv-mobile-v[0-9]+$`; PWA_OLD_CACHE_PURGE 19/19 |
| Cache version v2 | PASS | `sw.js:1` |
| Public cache preserved / cross-origin | PASS | `sw.js:20-30, 77`; PWA_PUBLIC_CACHE 8/8, PWA_CROSS_ORIGIN 4/4 |
| Methods/Range/Conditional | PASS | PWA_METHODS 23/23 |
| Anonymous/unauthorized/UNKNOWN/unregistered/tenant switch/logout | PASS | PWA_NETWORK_ONLY + PWA_4B3_INTEGRATION 52/52 (replay response gateway thật từ sandbox) |
| Authenticated HTML precache removed | PASS | `sw.js:3` chỉ `['/static/css/mobile.css', '/manifest.json']` |
| Server no-store | PASS | `file_access_service.py:20-21` |
| Regression 4B3/4B2/registry/SEC05/SEC03/BUG10/Core/routers | PASS | fresh tương ứng |
| Zero mutation; production integrity | PASS | PWA_ZERO_MUTATION 40/40; §9 |
| Real-browser test | INCOMPLETE | `pwa_evidence = {"kind": "Node VM actual SW / synthetic CacheStorage and network", "real_browser": "NOT RUN"}`; xem NEW-03 |
| Production client activation | INCOMPLETE | Không có deployment |
| SEC-04 OPEN | PASS | |
| "4B5 NOT STARTED" | PASS (lịch sử) / stale | Đúng tại 08:07; nay 4B5A/4B5 đã làm |

### 6.4 CODEX_REVIEW_CHECKLIST_4B5A.md (30 mục)

| Mục | Kết quả | Evidence |
|---|---|---|
| Uploader evidence audit | PASS (source) | Không có trường provenance lịch sử trong models (đồng ý với Codex) |
| Uploader never fabricated; legacy uploader NULL | PASS | `legacy_provenance.py:89-92` INSERT với `uploader_id=None`, reviewer ở cột riêng |
| Normal uploader bắt buộc | PASS | `file_registry.py:139` CHECK `uploader_id IS NOT NULL AND length(trim(uploader_id))>0`; `register_writing` `:166` `_text(uploader_id)`; NORMAL_UPLOADER_REQUIRED 4/4 |
| Legacy provenance explicit (v3, BOUND/REVOKED) | PASS | `file_registry.py:137-143` |
| Client không chọn được legacy | PASS | `register_writing` luôn ghi `'VERIFIED_UPLOADER'` (`:183`) và chỉ cho `PRIVATE/UNKNOWN` (`:171`); PROVENANCE_ATTACKS 9/9 |
| Legacy creation authority isolated | PASS (giới hạn đã khai) | `legacy_provenance.py:53-54` yêu cầu `type(reviewed) is _ReviewedMapping`; không route HTTP nào import (grep) |
| No uploader fallback; ACTIVE binding required | PASS | gateway `:158-161` UNBOUND đòi `VERIFIED_UPLOADER`; LEGACY_NO_UPLOADER_FALLBACK 10/10, LEGACY_BINDING_REQUIRED 8/8 |
| Task/Document live ACL | PASS | LEGACY_TASK_ACL 16/16, LEGACY_DOCUMENT_ACL 10/10 |
| UNKNOWN deny, ADMIN không bypass | PASS | LEGACY_UNKNOWN_DENY 9/9 |
| Foreign tenant denied | PASS | LEGACY_TENANT_ISOLATION 7/7 |
| Malformed provenance denied | PASS | `valid_provenance` `:76-88`; PROVENANCE_MALFORMED_DENY 12/12 |
| Backward compat v2 read-only | PASS | `access_snapshot` `:278, 285-287`; mutation trên v2 bị `_validate` từ chối `:61-62`; PROVENANCE_BACKWARD_COMPAT 12/12 |
| Atomicity | PASS | `legacy_provenance.py:79-104` một `BEGIN IMMEDIATE`, revalidate trước và sau; PROVENANCE_ATOMICITY 5/5 |
| Hash/size/path | PASS | `legacy_provenance.py:77,104` `physical_bytes`; PROVENANCE_PATH_INTEGRITY 10/10 |
| PWA private preserved | PASS (mô phỏng) | PROVENANCE_PWA_INTEGRATION 7/7 |
| Regression 4B4/4B3/4B2/registry/SEC05/SEC03/BUG10/Core/routers | PASS | fresh |
| Mobile baseline | PASS | §8 |
| Production integrity; no production activation | PASS | §9; `private_metadata/` không tồn tại |

Ghi chú: `legacy_provenance.py` đã bị sửa tiếp ở 4B5 (manifest 4B5A→4B5 đổi `legacy_provenance.py`), nên evidence 4B5A của `run-56914c09…` là cho phiên bản cũ; phiên bản hiện tại được bao phủ bởi `run-44c3751c…` và fresh run (234/234).

### 6.5 CODEX_REVIEW_CHECKLIST_4B5.md (checklist trạng thái BLOCKED lúc 10:27)

| Mục | Kết quả hiện tại | Evidence |
|---|---|---|
| Reference ≠ ownership | PASS | B4B5 LEGACY_CLASSIFICATION 8/8 |
| Uploader not fabricated | PASS | B4B5 LEGACY_PROVENANCE_INTEGRATION 5/5 |
| UNKNOWN default deny | PASS (fresh) | B4B5 LEGACY_UNKNOWN_DENY 33/33 |
| Normalization/path; external exclusion | PASS (fresh) | LEGACY_NORMALIZATION 23/23, LEGACY_EXTERNAL_REFERENCE 1/1 |
| Orphan/missing physical | PASS (fresh) | LEGACY_ORPHAN 2/2, LEGACY_MISSING_PHYSICAL 2/2 |
| Cross-tenant/multi-reference | PASS (fresh) | LEGACY_CROSS_TENANT 3/3, LEGACY_MULTI_BINDING 11/11 |
| UNAPPROVED default; explicit approval | PASS (fresh) | LEGACY_APPROVAL_REQUIRED 3/3, LEGACY_CUSTODIAN_BINDING 7/7 |
| Apply-time revalidation/stale | PASS (fresh) | LEGACY_STALE_REVIEW 6/6, LEGACY_REVALIDATION 1/1 |
| Atomic apply | PASS (fresh) | LEGACY_ATOMIC_APPLY 3/3 |
| Regressions / Core / mobile | PASS | fresh |
| Production integrity | PASS | §9 |
| SEC-04 conservative | PASS | OPEN |
| Production custodian review / final policy | INCOMPLETE | Production approvals = 0; chưa có quyết định USER (2 file UNKNOWN) |

Ghi chú: checklist 4B5 trong repo vẫn ở trạng thái "BLOCKED, 10 NOT RUN" và không được cập nhật sau khi 4B5 resume; acceptance thật nằm trong audit_codex_v3 §10 (46 PASS, 3 NOT RUN). Đây là mâu thuẫn tài liệu, không phải lỗi code.

---

## 7. Test integrity findings

Phương pháp: (1) đọc helper `record/rejected/task_write`; (2) grep `skip|except Exception|pass$|baseline|xfail`; (3) đối chiếu **tên test** và **expected vô hướng** giữa các cặp run 3D→4B1→4B2→4B3→4B4→4B5A→4B5→fresh và các attempt; (4) tìm record có `pass=true` nhưng `actual != expected` (kết quả: 0 trong run-56914c09, run-44c3751c).

`record` so sánh chặt bằng `==` — `tests/runtime_sandbox.py:284-286`:

```python
284    def record(name, actual, expected):
285        assert not violations, 'STOP: sandbox guard triggered'
286        results.append({'test': name, 'actual': actual, 'expected': expected, 'pass': actual == expected})
```

Không có cơ chế baseline-fail list; FAIL mobile được ghi như mọi FAIL khác.

Kết quả đối chiếu tên test (removed = test có ở run trước nhưng mất ở run sau):

| Cặp run | Removed | Added | Expected vô hướng thay đổi (ngoài giá trị động UUID/URL) |
|---|---|---|---|
| 3D → 4B1 | 0 | 77 | không |
| 4B1 → 4B2 | 1* | 339 | `REGISTRY schema version` 1→2 |
| 4B2 → 4B3 | 1* | 532 | không |
| 4B3 attempt `e48fba78` → final | 1* | 50 | không |
| 4B3 → 4B4 | 1* | 315 | không |
| 4B4 attempt `cd820336` → final | 1* | 5 | không |
| 4B4 → 4B5A | 1* | 235 | `REGISTRY schema version` 2→3, `B4B2 SCHEMA current version` 2→3 |
| 4B5A attempt `7c6418a4` → final | 5 (1* + 4 đổi nhãn) | 23 | không |
| 4B5 attempt `4bad803e` → final | 1* | 4 | không |
| 4B5 claimed → fresh | 1* | 1* | không |

`*` = test `REGISTRY FAILCLOSED invalid/public path <run-id>` có run-id trong tên nên luôn "đổi tên" mỗi run — artifact đặt tên, không phải mất test.

### 7.1 Schema assertion 2→3 — KẾT LUẬN: hợp lệ, nhưng assertion yếu (P3)

`tests/runtime_sandbox.py:308` và `:1119`:

```python
308    record('REGISTRY schema version', reg.VERSION, 3)
1119        record('B4B2 SCHEMA current version',FileRegistry.VERSION,3)
```

- Thay đổi 2→3 là chính đáng: schema thật đổi (thêm 4 cột provenance + CHECK, `file_registry.py:137-143`). v2 vẫn được kiểm tra riêng ở `:1591` (`PRAGMA user_version=2` → PROVENANCE_BACKWARD_COMPAT).
- Điểm yếu: hai assertion so sánh **hằng số trong class** với literal, không đọc `PRAGMA user_version` của DB thật, nên gần như tautology. Bù lại, mọi `_connection()` đều chạy `_validate` bắt buộc `user_version == 3` (`file_registry.py:60-62`), nên DB sai version sẽ làm các test khác FAIL. Mức độ: P3 (chất lượng test), không che lỗi.

### 7.2 Harness repair 3D — KẾT LUẬN: chỉ sửa harness, không đụng production

- source_manifest `run-66c003f4…` (3C) so với `run-601a577a…` (3D): **không khác** (diff = `[]`).
- Sửa đổi: suggested-code lấy đúng lúc (`tests/runtime_sandbox.py:693-701`), xử lý row thiếu an toàn (`:680-682` `row.get(...) if row else None`), ghi kết quả tăng dần (`:287-292`).

```python
693            if label == 'suggested':
694                # Acquire only when this case is ready: prior creates consume codes.
695                suggested = client.get('/api/tasks/suggested-code?prefix=A_USER')
696                record('SEC05 suggested authenticated contract', suggested.status_code, 200)
697                identifier = suggested.json()
```

- Expected của 530 test SEC05 giữa 3D và 4B1/4B2: không đổi về permission; chỉ 5 test `… REPORT attachment` / `… inherited attachment` đổi giá trị expected từ URL giả (`/static/uploads/new-report.txt`) sang URL upload thật — do 4B2 bắt buộc file đã đăng ký. Đây là **siết chặt** fixture (đúng như checklist 4B2 mục 21 yêu cầu), không nới.

### 7.3 Assertion mở rộng ở 4B5A attempt-1 — KẾT LUẬN: quy trình đúng; một chi tiết không được khai

- Attempt `run-7c6418a4…`: 2155 checks (2153/2). Final `run-56914c09…`: 2173 (2171/2). Source khác nhau đúng 1 file: `services\file_registry.py` → attempt-1 không thể là acceptance evidence, Codex đã loại đúng.
- Không test nào bị xóa; không expected nào bị nới. Thay đổi đếm: PROVENANCE_ZERO_MUTATION 94→103, LEGACY_TASK_ACL 13→16, PROVENANCE_ATOMICITY 3→5, PROVENANCE_ATTACKS 8→9, LEGACY_TENANT_ISOLATION 6→7, LEGACY_NO_UPLOADER_FALLBACK 9→10 (tất cả tăng).
- Không được khai: 4 test `PWA_4B3_INTEGRATION LEGACY approved {actual gateway status, no Cache API, server no-store, exact actual gateway body}` được đổi nhãn sang `PROVENANCE_PWA_INTEGRATION` (logic phân nhóm `tests/runtime_sandbox.py:2063`). Vì vậy PWA_4B3_INTEGRATION giảm 56→52. Không mất coverage, nhưng log không nêu. Mức độ: P3 (tài liệu).

### 7.4 Cách xử lý mobile 500 — KẾT LUẬN: trung thực, FAIL thật không bị ẩn

`tests/runtime_sandbox.py:1798-1799`:

```python
1798        record('mobile dashboard baseline', client.get('/mobile').status_code, 200)
1799        record('mobile tasks baseline', client.get('/mobile/tasks').status_code, 200)
```

Expected = 200, actual = 500 → `pass=false` trong mọi run từ Batch 1 tới fresh run. Không có danh sách "expected failure". Nguyên nhân xác nhận trong source `routes/mobile.py:73-79`:

```python
73        query = query.filter(Task.trang_thai.ilike("%đang%"))
...
79    tasks = query.order_by(Task.id.desc()).all()
```

Model `Task` không có cột `trang_thai` hay `id` (khóa chính là `id_phan_cong`, trạng thái là `tinh_trang`, `models/models.py:33,41`). BUG-01 CONFIRMED.

### 7.5 Windows static guard defect ở 4B3 — KẾT LUẬN: lỗi thật được phát hiện bởi test và sửa ở production, không nới test

Attempt `run-e48fba78…`: FAIL `GATEWAY_STATIC_BYPASS public asset /static/css/mobile.css` (actual 404) và `… public representative js` (404). Sau sửa (`app.py:71-76`), các test này PASS với expected không đổi (đối chiếu e48fba78→9dc4c7d9: không expected vô hướng nào đổi).

```python
71        parts=path.replace('\\','/').split('/')
74        raw=scope.get('raw_path',b'')
75        if '%' in path or b'\\' in raw or any(p.casefold()=='uploads' for p in parts):
76            return denied()
```

### 7.6 Các vấn đề test integrity khác (5 vấn đề, tổng hợp)

| # | Vị trí | Vấn đề | Mức |
|---|---|---|---|
| T1 | `runtime_sandbox.py:308,1119` | Schema assertion so hằng số class (7.1) | P3 |
| T2 | `source_manifest.json` (mọi run) | Manifest chỉ gồm 34 file Core (`app.py`, `config.py`, `database\*`, `models\*`, `routes\*`, `services\*`, `static/sw.js`); **không** gồm `tests/runtime_sandbox.py` hay `templates/`. "Source manifest unchanged" không chứng minh harness không đổi giữa các run | P3 |
| T3 | `runtime_sandbox.py:19-32` `inventory()` | Không bao phủ `qlcv_khach_hang.db` và `private_metadata/` (xem NEW-06) | P3 |
| T4 | Log 4B5A | Đổi nhãn 4 test không được khai (7.3) | P3 |
| T5 | `runtime_sandbox.py:1099-1103` | `replacement at least one succeeds` (`any(outcomes)`) yếu; `stale PENDING no authority` chỉ kiểm tra trạng thái sau race, **không có test** cho hệ quả stale PENDING còn sót khi compensation lỗi (NEW-01) | P3 |

```python
1099        record('B4B2 CONCURRENCY replacement at least one succeeds',any(outcomes),True)
1100        record('B4B2 CONCURRENCY replacement exactly one ACTIVE',len([r for r in live if r['state']=='ACTIVE']),1)
1103        record('B4B2 CONCURRENCY stale PENDING no authority',all(r['state']=='ACTIVE' for r in live),True)
```

Nới guard của harness ở 4B5 (cho phép `mode=ro&immutable=1`): `tests/runtime_sandbox.py:96-104` vẫn ép path qua `check()` (phải nằm trong `.test_runtime/run-*`) và chỉ chấp nhận đúng 2 query string. Có ghi trong audit v3 §13. Đánh giá: chấp nhận được, không phải nới an toàn.

```python
 96    def sqlite_path(database):
 97        if isinstance(database,str) and database.startswith('file:'):
 ...
101            if parsed.netloc or parsed.query not in ('mode=ro','mode=ro&immutable=1') or parsed.fragment:
102                block('Unsafe SQLite URI denied')
103            return check(url2pathname(parsed.path))
104        return check(database)
```

Fixture URL giả thay vì synthetic trusted upload: KHÔNG phát hiện ở positive case. `seed_task` (`:605-611`) đặt `file_giao_viec='/static/uploads/synthetic-task.txt'` (chưa đăng ký) nhưng đó là dữ liệu legacy có sẵn; mọi thao tác ghi file mới trong SEC05 matrix dùng `local_upload(...)` thật (`:658-659`).

---

## 8. Fresh run so với claimed

Lệnh: `.\venv\Scripts\python.exe -B tests/runtime_sandbox.py` (chạy đúng 1 lần, 16:59:15 → 17:08:05, exit 0).
stdout cuối: `Runtime completed; baseline failures: 2` / `PRODUCTION DB/DATA MODIFIED = NO`.
source_manifest fresh == source_manifest `run-44c3751c…` (so sánh dict: `True`) → hai run cùng source.

| Nhóm | Claimed (`run-44c3751c…`) | Fresh (`run-7b9d1713…`) | Chênh lệch |
|---|---|---|---|
| Tổng | 2398 checks, 2396 PASS / 2 FAIL | 2398 checks, 2396 PASS / 2 FAIL | 0 |
| complete | true | true | — |
| PWA (PWA_*) | 314/0 | 314/314 | 0 |
| Gateway (GATEWAY_*) | 531/0 | 531/531 | 0 |
| 4B2 (B4B2) | 338/0 | 338/338 | 0 |
| Registry (REGISTRY) | 77/0 | 77/77 | 0 |
| SEC05 | 530/0 | 530/530 | 0 |
| SEC03 | 84/0 | 84/84 | 0 |
| Collision (BUG10) | 13/0 | 13/13 | 0 |
| Provenance 4B5A (LEGACY_*/PROVENANCE_*/NORMAL_UPLOADER_REQUIRED) | 234/0 | 234/234 | 0 |
| Tooling 4B5 (B4B5) | 225/0 | 225/225 | 0 |
| Core smoke + mobile (còn lại) | 50/52 | 50/52 | 0 |

FAIL nguyên văn từ `run-7b9d17133d294f419996f96d9bdc1576/runtime_results.json`:

```json
[{"test": "mobile dashboard baseline", "actual": 500, "expected": 200, "pass": false},
 {"test": "mobile tasks baseline", "actual": 500, "expected": 200, "pass": false}]
```

Preflight (`preflight.json`): `status = PASS`; routers 11/11 = auth, tasks, master, companies, documents, personal, ai, processes, jds, org_chart, mobile (đều `true`); 8 guard probe (3× production DB blocked, traversal blocked, 3× direct DB/write/network blocked, SQLite ATTACH blocked).
`unexpected_guard_violations = []`; `drive_mutation_calls = 0`; `pwa_evidence.real_browser = "NOT RUN"`.

NEW REGRESSION: **không có**. Tên test fresh vs claimed: removed 1 / added 1 — chỉ là test có run-id trong tên; expected vô hướng chỉ khác ở 2 giá trị động (digest/snapshot synthetic).

---

## 9. Production integrity

Tính độc lập bằng Python (`hashlib.sha256` trên toàn bộ bytes, `os.stat`) trước khi chạy runner (16:5x) và sau khi runner kết thúc (17:08). Nội dung DB không được in.
Phạm vi = 10 file harness bảo vệ + `qlcv_khach_hang.db` (bổ sung) + kiểm tra `private_metadata/`.

| File | SHA-256 trước | SHA-256 sau | Size trước/sau | mtime_ns trước/sau | Khớp? |
|---|---|---|---|---|---|
| `qlcv.db` | 4f602ab4d5e43a3fc241c99f00e54dcfe77f6c90c7fba36f7a48f422caf116f0 | giống | 294912 / 294912 | 1785945160700406700 / giống | ✓ |
| `database/master_system.db` | a2dece227c2183343cf40730303bbfb46ceb66e73e2ac8810e1f24bf9b5b7017 | giống | 45056 / 45056 | 1786443070639241500 / giống | ✓ |
| `database/tenants/0109998888.db` | e944207eabe66b8a89d4d320cd3aedc7d13ae7e46900a8d70f7a0eca48ecd70a | giống | 237568 / 237568 | 1785915790326134000 / giống | ✓ |
| `database/tenants/0317598974.db` | b2a78aef6a303b73fd5bcda41347eb954b7e1679d51d18cdaa08baddb5806290 | giống | 237568 / 237568 | 1786443070617877000 / giống | ✓ |
| `static/uploads/.gitkeep` | 40b2a8898364b9eb2815698b194bd08bd5662b3190567e76f16e649ac7396ca2 | giống | 36 / 36 | 1788485269718932000 / giống | ✓ |
| `static/uploads/<legacy-docx-1>` | 337fb94e117447915a504caa658299d7965ddc67f40b436519574b65c8e183d7 | giống | 9825 / 9825 | 1785942593675055700 / giống | ✓ |
| `static/uploads/<legacy-docx-2>` | ac084d041877e5f02cae9e8e22c50dd26a611a4fd5c5f819d0bc2f29cdfcdd55 | giống | 13640 / 13640 | 1783735315570962900 / giống | ✓ |
| `.env` | be761aa10faa4fd5f4a2892e634d6e68d7af812be0da8c55fd4a48200a63ce2a | giống | 553 / 553 | 1783737107176066900 / giống | ✓ |
| `companies.json` | 575221b04b98c3919adfd0a8897d011cab61f88a0ee2648a025e6c82b83f4801 | giống | 272 / 272 | 1783910738904216300 / giống | ✓ |
| `seed.xlsx` | 0db3828c017b77e2917512aff085e88c2b8e7734118aeebb876fb925d7117b5e | giống | 30169 / 30169 | 1784293090898293300 / giống | ✓ |
| `qlcv_khach_hang.db` (ngoài phạm vi harness) | ae35a474273a719550439f72db822d7fd04c30518f17ceda2d5790383bdb2d79 | giống | 102400 / 102400 | 1784276002807002700 / giống | ✓ |
| `private_metadata/` | không tồn tại | không tồn tại | — | — | ✓ |

- Fingerprint trước của reviewer khớp với `run-44c3751c…/integrity.json` (cùng SHA-256/size/mtime_ns cho cả 10 file) → production không đổi kể từ lần chạy của Codex.
- `run-7b9d1713…/integrity.json`: `before == after` cho 10 entry, `production_data_modified: false`.
- Ghi chú: một số snapshot "independent" của Codex (ví dụ `independent_integrity.json`, `audit-sec01-blocked/integrity.json`) có mtime_ns lệch ở chữ số hàng trăm ns (…700406**8**00 thay vì …700406**7**00) — do công cụ độ phân giải 100 ns; mỗi snapshot nhất quán nội bộ, không phải thay đổi file.
- Reviewer không mở DB nào (kể cả read-only); chỉ đọc bytes để hash.

---

## 10. Finding status

| ID | Status theo log | Ý kiến reviewer | Lý do + evidence |
|---|---|---|---|
| SEC-01 | OPEN (BLOCKED) | ĐỒNG Ý | `auth_service.py:123` `is_nsx_master_admin = (company_mst in ["0312345678","default"]) and (user.ma_nv in ["ADMIN","SUPERADMIN","ROOT"] or user.quyen == "ADMIN" and user.ma_nv == "ADMIN")` — chỉ cần mã NV reserved; `employee_service.py:54-97` cho tạo mã tùy ý, `:100-128` cho đổi mật khẩu/quyền ADMIN; route `routes/master.py:121-138` cho ADMIN/CEO |
| SEC-02 | OPEN | ĐỒNG Ý | `auth_service.py:240-249` chỉ kiểm tra chữ ký; cookie `max_age=86400` (`:225-233`) chỉ là hạn phía browser, server không kiểm tra hạn/thu hồi |
| SEC-03 | PARTIALLY FIXED | ĐỒNG Ý | `routes/documents.py:198-205` bắt buộc session; rename luôn 403 (`:208-239`); SEC03 84/84 fresh |
| SEC-04 | OPEN | ĐỒNG Ý | Gateway + SW đã có, nhưng: 2 file UNKNOWN production chưa có chính sách; Nginx thật/browser thật chưa kiểm chứng; `/local_docs` (`app.py:93-95`) vẫn là StaticFiles public nếu cấu hình |
| SEC-05 | FIXED (phạm vi Task) | ĐỒNG Ý (có điều kiện) | `task_policy.py` + routes/tasks.py; 530/530 fresh. Phụ thuộc SEC-02 (role lấy từ cookie `task_policy.py:22`) — log đã nêu |
| SEC-06 | OPEN | ĐỒNG Ý (không kiểm chứng thêm) | Không có thay đổi resolver; reviewer không audit lại |
| SEC-07 | OPEN | ĐỒNG Ý | audit v4 §6 mô tả prefix/first-match; reviewer không kiểm chứng runtime |
| HARD-01 | OPEN | ĐỒNG Ý (không kiểm chứng) | Không audit lại template |
| HARD-02 | OPEN | ĐỒNG Ý | `app.py:38-44` `allow_origins=["*"], allow_credentials=True`; cookie không `secure` (`auth_service.py:225-233`) |
| HARD-03 | OPEN | ĐỒNG Ý một phần | Phần private cache đã được 4B4 xử lý trong SW; phần manifest icons/logout purge vẫn mở. Log §3 chưa cập nhật phần đã giảm thiểu |
| HARD-04 | OPEN | ĐỒNG Ý | Nginx template chỉ `listen 80`, không TLS |
| HARD-05 | OPEN | ĐỒNG Ý | `employee_service.py` mật khẩu mặc định `"123456"`; `config.py:25-31` in SECRET_KEY sinh ngẫu nhiên ra stdout |
| BUG-01 | OPEN | ĐỒNG Ý | `routes/mobile.py:73-79`; fresh 2 FAIL |
| BUG-02 | OPEN | ĐỒNG Ý (không kiểm chứng) | — |
| BUG-03 | OPEN | ĐỒNG Ý | `routes/tasks.py:214` `@router.get("/api/tasks/{task_id}")` khai báo trước `:282` `@router.get("/api/tasks/get-temp-id")` → route động bắt trước |
| BUG-04..07, BUG-09 | OPEN | ĐỒNG Ý (không kiểm chứng) | Không thuộc phạm vi batch đã review |
| BUG-08 | OPEN | KHÔNG ĐỒNG Ý (đã thay đổi) | Log: "Task list ignores CC". Source hiện tại `task_service.py:9-11` lọc list bằng `can_view_task` (bao gồm CC, `task_policy.py:33-36`); test `SEC05 … LIST` cho CC PASS. Phần Task list đã được SEC-05 sửa; phần dashboard (`auth_service.get_dashboard_stats` chỉ lọc giver/receiver) vẫn lệch → nên đổi thành PARTIALLY FIXED |
| BUG-10 | PARTIALLY FIXED | ĐỒNG Ý | Collision fixed (13/13); `task_service.py:119-122` `int(float(...))` không giới hạn/không bắt `TypeError`/`OverflowError` |
| CLEAN-01 | OPEN | ĐỒNG Ý | — |

### Finding mới

| ID đề xuất | Severity | Mô tả | Evidence |
|---|---|---|---|
| NEW-01 | P2 | Stale PENDING khóa slot vĩnh viễn. Nếu compensation `revoke_pending` lỗi (busy 300 ms) hoặc process chết giữa lúc tạo PENDING và hoàn tất, PENDING còn lại. Mọi lần lưu sau trên cùng Task/Document (kể cả chỉ sửa tiêu đề, xóa file, đổi sang link ngoài) đều bị từ chối, trừ khi gửi lại đúng file của PENDING đó. Không có expiry PENDING, không có công cụ reconciliation. Log chỉ nói PENDING "unusable", không nói khóa slot | trích dưới |
| NEW-02 | P2 | `change_password` tạo lại tài khoản `ADMIN` khi không tồn tại, với mật khẩu mới do người gọi chọn, không kiểm tra mật khẩu cũ. Điều kiện: session có `ma="ADMIN"` trong tenant không có employee ADMIN (ví dụ session do `switch-tenant` tạo — `routes/companies.py:313-320` luôn ký `"ma": "ADMIN"`; hoặc session cũ còn hiệu lực do SEC-02). Ở default tenant, tài khoản này trở thành MASTER (SEC-01). Không có trong log/audit v4 | trích dưới |
| NEW-03 | P2 | SW đăng ký ở root scope; mọi request same-origin không phải public asset (mọi navigation trang, POST API) đi qua `event.respondWith(fetch(request, { cache: 'no-store' }))`. Tạo lại Request có `mode: 'navigate'` với init không rỗng, redirect `manual` của navigation, body POST — chỉ được mô phỏng bằng Node VM. Nếu một engine xử lý khác, **toàn bộ ứng dụng** (cả desktop, vì cùng origin) có thể lỗi cho client đã từng mở `/mobile`. Cần real-browser smoke trước rollout | `static/sw.js:74-83`; `pwa_evidence.real_browser = "NOT RUN"` |
| NEW-04 | P3 | Lỗi sau business commit (revalidation/activation/sidecar commit) trả `"Không có quyền hoặc dữ liệu không hợp lệ."` dù thay đổi đã được lưu → client không phân biệt được "bị từ chối" với "đã lưu nhưng file không truy cập được" | `routes/tasks.py:16-18, 203-205`; test `B4B2 FAILURE postcommit business remains committed` (actual = URL mới) cùng `B4B2 FAILURE revalidation response denied` (success=False) |
| NEW-05 | P3 | Endpoint không xác thực: `/api/auth/lookup-user-tenant?username=<email>` trả MST + tên công ty → dò email ↔ tenant; `/api/documents/next-code` không kiểm tra session | `routes/auth.py:75-98`; `routes/documents.py:98-102` |
| NEW-06 | P3 | `inventory()` của harness không gồm `qlcv_khach_hang.db` và `private_metadata/`; "10 protected unchanged" không chứng minh 2 vị trí này. (Reviewer đã kiểm tra bổ sung: không đổi / không tồn tại) | `tests/runtime_sandbox.py:19-23` |

NEW-01 — `services/file_registry.py:217-222` và `services/file_binding_service.py:85-87`:

```python
217            old = conn.execute("SELECT * FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=? AND state IN ('PENDING','ACTIVE') ORDER BY CASE state WHEN 'PENDING' THEN 0 ELSE 1 END", ...).fetchone()
218            if old:
219                if old['file_id'] == file_id and (replacement or old['generation'] == generation):
220                    return old['binding_id']
221                if old['state']=='PENDING' or not replacement:
222                    raise RegistryError("Binding conflict")
...
 85                    live=self.registry.slot_bindings(*slot,connection=conn)
 86                    if any(b['state']=='PENDING' and b['binding_id']!=pending for b in live):
 87                        raise RegistryError('Another replacement is reserved')
```

Kịch bản: Task T có A ACTIVE; lần lưu thay bằng B tạo PENDING(B); business commit lỗi; `revoke_pending` lỗi busy → PENDING(B) còn. Lần sau: lưu lại với A (url không đổi) → dòng 217 lấy PENDING(B) trước → khác file → dòng 222 raise. Lưu với link ngoài/rỗng → `pending=None` → dòng 86 raise. `save_task_data` luôn đi qua `FileBindingService.run` (`task_service.py:169-170`), nên Task T không sửa được nữa. Route trả `_denied()`.

NEW-02 — `services/auth_service.py:156-168` (gọi từ `routes/auth.py:181-184` với `session["ma"]`):

```python
156        if not user:
157            if ma_nv_clean == "ADMIN":
158                user = Employee(
159                    ma_nv="ADMIN",
160                    ten_nv="Quản trị hệ thống",
161                    mat_khau=hash_password(new_pass_clean),
162                    quyen="ADMIN",
...
166                db.add(user)
167                db.commit()
168                return {"success": True, "message": "✅ Đổi mật khẩu thành công!"}
```

---

## 11. Nhận xét đề xuất SEC-01 (audit_codex_v4.md)

**Phạm vi Codex đề xuất:** dừng (BLOCKED) vì sửa đúng cần một "MASTER credential-management boundary" — thay đổi authorization của tenant ADMIN/CEO đối với Employee; có thể cần MASTER credential store riêng. File cần duyệt: `routes/master.py`, `services/employee_service.py`, phối hợp `services/auth_service.py`, `routes/auth.py`, `routes/companies.py`.

**Đánh giá:**
- Root cause chính xác (đã kiểm chứng `auth_service.py:123`, `employee_service.py:54-128`, `routes/master.py:121-138`, `routes/companies.py:22-44, 299-322`).
- Quyết định dừng là hợp lý vì quy tắc STOP của prompt: bất kỳ bản sửa an toàn nào cũng phải từ chối một thao tác mà tenant ADMIN/CEO hiện được phép.
- Đề xuất hơi **rộng** khi gợi ý scoped session + có thể MASTER credential store mới; và **thiếu** đường NEW-02 (`change_password` tự tạo ADMIN) và việc CEO có thể nâng quyền bất kỳ ai lên ADMIN qua `update_employee` (`quyen` lấy từ payload).

**Phương án hẹp hơn (đề xuất, chưa triển khai):**
1. `services/auth_service.py:123`: chỉ cấp master khi `company_mst` là default **và** `user.ma_nv == "ADMIN"` **và** `user.quyen == "ADMIN"`; bỏ `SUPERADMIN`/`ROOT` (hoặc dùng allowlist cấu hình qua env).
2. `services/employee_service.py` (`add_employee`, `update_employee`): khi tenant là default và `ma_nv` thuộc tập reserved, từ chối trừ khi caller có `is_master_admin` thật; đồng thời không cho caller không-master gán `quyen="ADMIN"` cho reserved ID. Cần truyền `session` (hoặc cờ master) từ `routes/master.py:121-138`.
3. `services/auth_service.py:156-168`: bỏ nhánh tự tạo ADMIN (hoặc chỉ cho phép khi tenant không có employee nào và caller là master).
4. Không đụng session format, không tạo store mới, không migration. Phần scoped session để lại cho SEC-02.

Giới hạn của phương án hẹp: master vẫn dựa trên một Employee trong `qlcv.db`; ai có quyền ghi DB/được master tạo thì vẫn là master. Nhưng đóng được cả path A (tạo ID reserved) và path B (reset mật khẩu ADMIN bởi tenant manager) mà audit v4 mô tả.

**File sẽ phải sửa (phương án hẹp):** `services/auth_service.py`, `services/employee_service.py`, `routes/master.py`; test: `tests/runtime_sandbox.py` (+ `tests/RUNTIME_SANDBOX.md`). `routes/companies.py` và `routes/auth.py` không bắt buộc.

---

## 12. Câu hỏi cần USER quyết định

1. **SEC-01 — ranh giới quản lý tài khoản MASTER.**
   - A: Phương án hẹp (§11): chỉ master mới tạo/sửa reserved ID ở default tenant; bỏ ROOT/SUPERADMIN; bỏ tự tạo ADMIN. Hệ quả: tenant ADMIN/CEO của default tenant mất quyền reset mật khẩu ADMIN; 3 file nguồn thay đổi.
   - B: MASTER credential store riêng (bảng/file mới trong master DB) + scoped session. Hệ quả: an toàn hơn về lâu dài, nhưng cần schema/bootstrap/migration và ảnh hưởng SEC-02.
   - Khuyến nghị: **A** ngay, B đưa vào lộ trình SEC-02.
2. **Chính sách 2 file UNKNOWN production (`<legacy-docx-1>`, `<legacy-docx-2>`).**
   - A: Giữ deny vĩnh viễn; người dùng upload lại qua flow mới. Hệ quả: link cũ trong 2 Task/Document hỏng, không cần custodian.
   - B: Chạy quy trình custodian review (cần khóa ký, bằng chứng độc lập, apply production — chưa có entry point production). Hệ quả: thêm công cụ + rủi ro vận hành.
   - Khuyến nghị: **A** (chỉ 2 file; chi phí B không tương xứng).
3. **Xử lý NEW-01 (stale PENDING).**
   - A: Cho PENDING hết hạn theo thời gian (ví dụ > N phút thì coi như REVOKED khi gặp trong `create_pending_binding`/`run`). Hệ quả: thay đổi nhỏ trong registry, cần test mới.
   - B: Công cụ reconciliation offline cho admin. Hệ quả: không đổi logic online, nhưng cần thao tác thủ công khi xảy ra.
   - Khuyến nghị: **A**, kèm test fault-injection cho `revoke_pending` lỗi.
4. **Điều kiện trước rollout 4B3/4B4.**
   - A: Bắt buộc real-browser smoke (Chrome/Edge/Safari iOS) cho navigation, POST, đăng xuất, offline, và kiểm tra Nginx thật (`/static/uploads`, `/qlcv/` prefix) trước khi deploy.
   - B: Deploy rồi theo dõi. Hệ quả: nếu SW lỗi, client đã cài SW bị hỏng toàn app tới khi có SW mới.
   - Khuyến nghị: **A**.
5. **Làm mới log trung tâm.**
   - A: Cho Codex cập nhật header/§1/§2/§3/§6/§8/§9/§11/§12/§13 theo bảng §5 (chỉ tài liệu).
   - B: Đóng băng log, dùng audit_codex_vN làm nguồn chính. Hệ quả: người đọc log sẽ thấy số liệu 4B4 là "latest".
   - Khuyến nghị: **A**.
6. **BUG-08 status.** A: đổi thành PARTIALLY FIXED (list đã đúng, dashboard chưa). B: giữ OPEN. Khuyến nghị: **A**.

---

## 13. Giới hạn của review này

- Không chạy browser thật, không có Playwright/Selenium; mọi kết luận PWA dựa trên source + Node VM của Codex.
- Không truy cập máy chủ/Nginx production; chỉ đọc template trong repo.
- Không mở bất kỳ DB nào (kể cả read-only) → không kiểm chứng độc lập số liệu production inventory (21 reference, 2 UNKNOWN) của audit v3; chỉ kiểm chứng rằng 2 file upload tồn tại và không đổi.
- Không chạy lại các attempt run; số liệu các run lịch sử lấy từ artifact JSON có sẵn (không thể chứng minh artifact không bị sửa sau khi tạo, nhưng mtime thư mục khớp dòng thời gian log).
- `tests/runtime_sandbox.py` (2194 dòng) được đọc có chọn lọc (helper, guard, SEC05 matrix, 4B2 failure/concurrency, schema, mobile), không đọc toàn bộ phần Node VM/4B5.
- `services/legacy_discovery.py` chỉ đọc các phần guard (`readonly_database`, `apply_synthetic`), không audit toàn bộ thuật toán phân loại.
- SEC-06, SEC-07, HARD-01, BUG-02/04/05/06/07/09 không được audit lại; "ĐỒNG Ý" ở các mục này nghĩa là không có bằng chứng ngược lại.
- Cross-DB reconciliation: chỉ kiểm chứng bằng đọc code và test fault-injection có sẵn; không có thử nghiệm crash thật (kill process giữa hai commit).
- Session (SEC-02) và tenant path (SEC-06/07): không có test runtime trong harness; không thể kết luận phạm vi khai thác.
- Runner chỉ được phép chạy 1 lần; không có lần chạy thứ hai để kiểm tra tính ổn định (flakiness) của các test concurrency.

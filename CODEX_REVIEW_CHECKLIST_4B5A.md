# Batch 4B5A — Legacy Provenance Model

Evidence date: 2026-10-01. Batch acceptance PASS; USER review pending.
Fresh run: `.test_runtime/run-56914c095017492d97da57114b97fc2f/`.
Evidence: runtime_results.json, integrity.json, preflight.json, source_manifest.json,
pwa_results.json. Checklist is an evidence map, not a substitute for those artifacts.

| Acceptance item | Status | Evidence |
|---|---|---|
| Actual uploader evidence audit performed | PASS | Current models, upload service/routes and source search: NEW upload captures signed-session uploader; no immutable historical upload proof in legacy fields/AuditLog. External archives not investigated. |
| Uploader never fabricated | PASS | PROVENANCE_MODEL: legacy uploader NULL; reviewer separate. |
| Normal uploader remains mandatory | PASS | NORMAL_UPLOADER_REQUIRED 4/0; normal NULL/empty/whitespace rejected; actual upload succeeds. |
| Legacy provenance explicit | PASS | Schema v3 constrained LEGACY_VERIFIED_MAPPING, BOUND/REVOKED only; PROVENANCE_MODEL 5/0. |
| Normal/client API cannot select legacy provenance | PASS | PROVENANCE_ATTACKS 9/0; flags/classification/JSON/form cannot create legacy identity. Existing upload actor canonicalization preserved. |
| Legacy creation authority isolated | PASS | LEGACY_CREATION_AUTHORITY 7/0; no HTTP route/import; offline digest-bound explicit permit only. Arbitrary privileged Python/SQLite writer is inside trusted administrative boundary, not isolated by this API. |
| Legacy has no uploader fallback | PASS | LEGACY_NO_UPLOADER_FALLBACK 10/0; UNBOUND/fake-uploader/no-binding denied. |
| Legacy requires valid ACTIVE binding | PASS | LEGACY_BINDING_REQUIRED 8/0; no ACTIVE/unsupported binding denied including ADMIN. |
| Task live ACL preserved | PASS | LEGACY_TASK_ACL 16/0 plus unchanged GATEWAY_TASK/LIVE_REVALIDATION; deleted object/relationship loss denied. SEC05 policy untouched. |
| Document live ACL preserved | PASS | LEGACY_DOCUMENT_ACL 10/0; general/department ACL and deleted object; unchanged Document predicate. |
| UNKNOWN remains denied | PASS | LEGACY_UNKNOWN_DENY 9/0 plus gateway regression. |
| ADMIN cannot bypass UNKNOWN | PASS | LEGACY_UNKNOWN_DENY ADMIN case and gateway UNKNOWN case. |
| Foreign tenant denied | PASS | LEGACY_TENANT_ISOLATION 7/0; foreign binding rejected; same employee code does not cross tenant. |
| Malformed provenance denied | PASS | PROVENANCE_MALFORMED_DENY 12/0, corrupted enum/case/missing representation. |
| Backward compatibility deterministic | PASS | PROVENANCE_BACKWARD_COMPAT 12/0: valid v2 PRIVATE/UNKNOWN read as VERIFIED_UPLOADER; normal uploader/admin semantics unchanged; v2 bytes unchanged. Mutations require separately approved explicit upgrade; no migration helper or silent upgrade. |
| Atomicity safe | PASS | PROVENANCE_ATOMICITY 5/0 plus zero-mutation checks: stale callback/post-insert callback/second-slot conflict rollback identity and bindings. SQLite BEGIN IMMEDIATE/constraints authoritative. |
| Hash/size/path protections preserved | PASS | PROVENANCE_PATH_INTEGRITY 10/0 plus unchanged gateway integrity/path suite. |
| PWA private behavior preserved | PASS | PROVENANCE_PWA_INTEGRATION 7/0: actual legacy gateway response replay, no Cache API, offline failure. Node VM synthetic cache lifecycle; real browser NOT RUN. |
| 4B4 regression | PASS | PWA 314/0. |
| 4B3 regression | PASS | GATEWAY 531/0. |
| 4B2 regression | PASS | B4B2 338/0. |
| Registry regression | PASS | REGISTRY 77/0, schema expectations intentionally v3. |
| SEC-05 regression | PASS | SEC05 530/0. |
| SEC-03 regression | PASS | SEC03 84/0; Drive rename remains BLOCKED. |
| BUG-10 collision regression | PASS | BUG10 13/0; numeric validation untouched. |
| Core smoke | PASS | Current login/dashboard/tasks/logout actor smoke. |
| 11 routers | PASS | preflight/router inventory 11/11. |
| Mobile baseline unchanged | PASS (baseline match only) | /mobile and /mobile/tasks each HTTP500; the two actual FAILs retained, not relabeled as passing functionality. |
| Production integrity | PASS | Before/after SHA-256/size/mtime_ns unchanged; preflight PASS; guard violations [], provider calls0; source manifest current. |
| No production legacy activation | PASS | Production registry absent; no production discovery/apply/migration/file writes. All activation synthetic. |

Summary: 30 acceptance items PASS with evidence limitations stated; 0 FAIL,
0 NOT RUN, 0 NOT FULLY TESTABLE for these applicable items. REAL BROWSER = NOT RUN,
production clients and actual Nginx = NOT VERIFIED, outside this model batch.
SEC-04 OPEN. Original representation blocker resolved; full 4B5 workflow not resumed.
Future tooling must authenticate custodian and verify independent evidence + full
reference/conflict inventory before issuing a permit. An editable URL is never proof.

Attempt history: first run run-7c6418a4981a46179c23fb5c5c96e21f recorded2153/2,
but source-manifest guard rejected it after in-scope provenance mutation checks and
additional security assertions were added. It is diagnostic, not final acceptance.
Final fresh run2171/2 on unchanged source; no expected security rule weakened.

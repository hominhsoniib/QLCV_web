# CODEX REVIEW CHECKLIST — Batch 4B3 / SEC-04

Updated: 2026-10-01 06:37 +07:00 (Asia/Ho_Chi_Minh).
Historical CODEX_REVIEW_CHECKLIST.md is the Batch 4B2 checklist and remains unchanged.
This file maps acceptance criteria to actual evidence; checklist text alone is not proof.
USER review remains pending. No deployment acceptance is claimed.

## Review evidence record

- Scope: approved Batch 4B3 FORCE EXECUTION, online private gateway/static exclusion only.
- Reviewer: Codex, execution validation; USER final review pending.
- Final fresh run: `.test_runtime/run-9dc4c7d902ef4445a5f90e9f836874ef/` (R below).
- Artifacts: R/runtime_results.json, integrity.json, preflight.json, source_manifest.json,
  gateway_environment.json. Reports were read, not inferred from exit code.
- Runtime: complete=true; targeted531 PASS/0 FAIL; full1623 PASS/2 FAIL.
- Only FAIL: /mobile500 and /mobile/tasks500 expected200, historical baseline reproduced.
- NEW REGRESSIONS: NONE in final run; provider mutation count0; guard violations empty.
- Production DB/data/registry/upload modified or created: NO/NO/NO/NO.
- Protected inventory10 SHA-256/size/mtime_ns unchanged; current Core hashes match tested manifest.
- Source delta: app.py, services/file_registry.py, new services/file_access_service.py,
  routes/documents.py (shared existing READ predicate only). Tests/docs/log/checklist updated.
- Config/Task policy/Task write flows/Drive/coordinator/mobile/PWA/deployment/schema unchanged.
- Existing uncommitted Phase A/mobile/VPS/4B1/4B2/SEC05/user changes retained.
- AST5 files PASS; git diff --check PASS. Full cumulative diff reviewed with historical attribution.
- Acceptance result: PASS for applicable executable checks; genuine Windows link creation
  NOT FULLY TESTABLE, actual production Nginx NOT VERIFIED. These are explicit limitations.
- Central log updated with attempts, fresh evidence and remaining risk. SEC-04 OPEN.

## Acceptance checklist with evidence

Evidence categories are exact test-name prefixes in R/runtime_results.json.
PASS below requires fresh runtime evidence except explicitly labeled source-only inspection.

| Criterion | Result | Evidence / limitation |
| --- | --- | --- |
| Route/static mount ordering | PASS | GATEWAY_STATIC_BYPASS canonical gateway marker/bytes; private route before public mount in app.py |
| /static/uploads direct public bypass | PASS | AUTH/UNBOUND/FAIL_CLOSED deny anonymous, unknown, unregistered physical files |
| Parent /static bypass | PASS | STATIC_BYPASS HTTP alias matrix + direct parent get_response uploads denial; resolved-root exclusion |
| Nginx source bypass audit | PASS | SOURCE ONLY: both Nginx templates proxy8081; deploy/run/chay source has no uploads alias/root |
| Actual production Nginx | NOT RUN | NOT VERIFIED; no live production access/reload/deploy |
| Signed-session authentication | PASS | GATEWAY_AUTH canonical known and missing anonymous401; valid actor bytes200 |
| Invalid/tampered session | PASS | GATEWAY_AUTH invalid signatures deny401, no bytes/private metadata |
| Session expiration/revocation | NOT RUN | Existing untimed mechanism SEC02; not implemented or claimed by4B3 |
| Canonical tenant/actor authority | PASS | GATEWAY_TENANT same employee code across A/B; forged query/header tenant/role/actor deny |
| Registry lookup required | PASS | GATEWAY_FAIL_CLOSED absent entry and missing registry deny; no initialize/fallback |
| UNKNOWN denied including ADMIN | PASS | GATEWAY_UNBOUND uploader/admin UNKNOWN404 |
| Unregistered physical file denied | PASS | GATEWAY_FAIL_CLOSED existing synthetic legacy bytes404; no inferred claim |
| UNBOUND uploader-only | PASS | GATEWAY_UNBOUND exact uploader200; same-tenant ADMIN/other, foreign actor deny |
| UNBOUND expiry/state/classification | PASS | UNBOUND expired/WRITING/REVOKED/UNKNOWN deny; PRIVATE required |
| ACTIVE binding alone insufficient | PASS | TASK PENDING/revoked and LIVE_REVALIDATION missing live object deny |
| Live business object revalidation | PASS | LIVE_REVALIDATION deleted Task/Document deny despite registry binding |
| Persisted field exact match | PASS | LIVE_REVALIDATION changed assignment/report/Document link denies old file |
| Task READ ACL integration | PASS | GATEWAY_TASK giver/receiver/CC/ADMIN/unrelated; source calls task_policy.can_view_task unchanged |
| Current Task relationship required | PASS | LIVE_REVALIDATION actor loses relationship then denied |
| Document READ authorization | PASS | GATEWAY_DOCUMENT ADMIN/CEO, own/general departments, manager own/direct subordinate; library predicate alignment |
| Current Document permission required | PASS | LIVE_REVALIDATION department permission lost denies |
| Multiple-binding union | PASS | TASK denied-parent/allowed-child, parent-only, both and neither; separate live bindings |
| Foreign binding cannot grant authority | PASS | TENANT denies foreign Task/Document/session; readonly snapshot filters binding tenant |
| Supported binding kinds/slots only | PASS | TASK assignment/report/child and DOCUMENT link_file; missing/revoked/PENDING denial; source allowlist, no new Personal/AI kinds |
| Traversal/canonical basename | PASS | GATEWAY_PATH and STATIC_BYPASS ../, nesting, encoding/double encoding, separators, empty/dot invalid basenames |
| Windows drive/UNC/control rejection | PASS | GATEWAY_PATH + STATIC_BYPASS Windows/mixed slash/UNC/NUL cases |
| Realpath confinement | PASS | GATEWAY_PATH opened-handle outside root denial; regular-file/root checks executed on valid reads |
| Genuine symlink/junction/reparse creation | NOT FULLY TESTABLE | R/gateway_environment.json: Windows symlink privilege unavailable; junction not created; no genuine link PASS claimed |
| Opened-handle escape defense | PASS | GATEWAY_PATH injected final-handle outside-root result denies; production Windows handle validation + reparse guard |
| Physical size integrity | PASS | GATEWAY_INTEGRITY size mismatch/missing/directory deny |
| Physical SHA-256 integrity | PASS | GATEWAY_INTEGRITY same-size hash mismatch deny; immutable verified bytes returned |
| GET authorization | PASS | GATEWAY_HTTP full bytes only after ACL/hash |
| HEAD authorization | PASS | HTTP authorized metadata; anonymous/unauthorized no private headers; INTEGRITY tampered HEAD denies |
| Range authorization | PASS | HTTP authorized206/exact bytes; invalid416 only after auth; anonymous/unauthorized Range denied |
| Conditional authorization | PASS | HTTP authorized ETag/date304; unauthorized denied; INTEGRITY hash mismatch conditional denied |
| Existence disclosure | PASS | Per-request uniform401/404 JSON/HEAD empty; no private ETag/Last-Modified/range/redirect on denial |
| No dashboard redirect for private errors | PASS | AUTH/FAIL_CLOSED HTTP follow_redirects=False + no Location/sensitive payload |
| Inline/download filename/type | PASS | HTTP inline/download and sanitized Content-Disposition; source presentation-only filename/extension-derived conservative MIME |
| Private-safe cache headers | PASS | Every private gread checks private,no-store; source Pragma/Expires/nosniff |
| Service-worker Cache API protection | NOT RUN | Explicitly4B4; no-store alone does not stop cache.put; static/sw.js unchanged |
| Registry unavailable/corrupt fail-closed | PASS | FAIL_CLOSED missing/corrupt/version/schema/busy/read error deny; no public fallback |
| Readonly registry open | PASS | ZERO_MUTATION fingerprints; mode=ro/query_only coherent snapshot, no initialization |
| Public CSS/JS/static assets | PASS | STATIC_BYPASS mobile.css/representative JS/manifest/sw200; public image/favicon checks conditional on present files |
| Zero-mutation authorized reads | PASS | GATEWAY_ZERO_MUTATION DB/registry/upload fingerprints + provider count checks |
| Zero-mutation denied reads | PASS | GATEWAY_ZERO_MUTATION applies to each denial and static alias; no authority mutation |
| Batch4B2 regression | PASS | Current338/0 including upload/binding/replacement/compensation/process races |
| Registry foundation regression | PASS | Current77/0 including concurrency/fail-closed/version checks |
| SEC05 regression | PASS | Current530/0; Task authorization expectations unchanged |
| SEC03 regression | PASS | Current84/0; authenticated upload and fail-closed Drive rename preserved |
| BUG10 collision regression | PASS | Current13/0; numeric validation remains outside scope |
| Core smoke | PASS | Current login/dashboard/tasks/logout checks all PASS |
| Core routers | PASS | R/preflight + runtime: auth/tasks/master/companies/documents/personal/ai/processes/jds/org_chart/mobile11/11 |
| Mobile historical baseline | PASS | Current run exactly two historical HTTP500s; bugs remain, not claimed fixed |
| Production integrity | PASS | R/integrity before==after; across-batch protected fingerprint comparison unchanged; production registry absent |
| Approved source scope | PASS | Selected source delta only four approved production files; no schema/static/deploy/Task semantics changes |
| No legacy onboarding/claim | PASS | Unregistered/UNKNOWN denial, no production scan/mapping/URL rewrite/file move |
| SEC04 remains OPEN | PASS | Central finding OPEN;4B4 Cache API and4B5 verified legacy resolution remain |

## Targeted evidence counts

| Category | PASS | FAIL |
| --- | ---: | ---: |
| GATEWAY_AUTH | 12 | 0 |
| GATEWAY_UNBOUND | 30 | 0 |
| GATEWAY_TASK | 50 | 0 |
| GATEWAY_DOCUMENT | 31 | 0 |
| GATEWAY_TENANT | 24 | 0 |
| GATEWAY_PATH | 16 | 0 |
| GATEWAY_STATIC_BYPASS | 42 | 0 |
| GATEWAY_HTTP | 46 | 0 |
| GATEWAY_INTEGRITY | 24 | 0 |
| GATEWAY_LIVE_REVALIDATION | 32 | 0 |
| GATEWAY_FAIL_CLOSED | 38 | 0 |
| GATEWAY_ZERO_MUTATION | 186 | 0 |
| TOTAL | 531 | 0 |

## Repair history / limits

- Initial run-e48fba78587d415b80f47d64f40577ab: public CSS/JS404 defect in
  Windows separator guard; two mobile baseline failures also present.
- app.py repair distinguishes raw client alias from framework-normalized separators.
  No expected security result weakened or assertion skipped.
- Fresh run-c692f8711a85458fa11c4aace4114c57: targeted482/0, full1574/2.
- Added stronger report/Document/general/parent-only/HEAD/hash-conditional coverage
  and narrow readonly error/connection hardening; final fresh R targeted531/0,
  full1623/2. No final new regression.
- No production startup, registry/upload write, provider request, package install,
  deployment, migration, commit or destructive Git command.
- Genuine OS links/actual production Nginx remain unverified as recorded above.
- Existing session architecture risks and memory/IO cost of full per-request hashing
  remain operational considerations; gateway uses verified bytes to avoid reopen races.
- Stop after USER review handoff. Do not start4B4/PWA or4B5/legacy automatically.

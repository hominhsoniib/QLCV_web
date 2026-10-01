# CODEX AUDIT & FIX STATUS — QLCV

Updated: 2026-10-01 10:51 +07:00 (Asia/Ho_Chi_Minh).

Latest completed current-source run: Batch4B5A run-56914c095017492d97da57114b97fc2f,
234/0 provenance targeted; full2171/2 historical mobile failures. Original4B5
representation blocker resolved; full discovery/review mapping remains unimplemented.
SEC04 OPEN. Prior 'not started' and older full-run counts below describe earlier phases.

This is a reviewer handoff, not a terminal transcript. Earlier work is recorded
retrospectively; its exact completion timestamps were not captured. Source-based
findings are distinguished from runtime evidence. No secrets, session values or
production user records are included.

Status vocabulary: OPEN, IN PROGRESS, PARTIALLY FIXED, FIXED, BLOCKED, DEFERRED.
COMPLETE and PASS/FAIL below describe phase/test outcomes, not finding statuses.

## 1. Current Project Scope

QLCV only: authentication/session, dashboard, tasks, personal management,
departments, employees, companies/multi-tenant, documents/local files/Google
Drive, QLCV AI, processes, Job Descriptions, organization chart, mobile/PWA,
startup/database and deployment.

CRM and QuoteFlow are disabled from the shared QLCV entry points. Their source,
databases, uploads, exports, backups and configuration remain preserved.

Batch 3B Task authorization code and tests were written after user policy approval.
Batch 3D repaired only the harness/reporting and completed fresh guarded validation:
SEC-05 530/530 PASS. No production code changes in Batch 3D; stop after reporting.
Batch 4A final private-file architecture audit completed; only this log updated.
USER approved sidecar/UNKNOWN/UNBOUND/shared/cache/legacy architecture; Batch 4B1
metadata foundation implemented/tested only, not activated in production flow.
Production sidecar NOT created. No private gateway, identity/session fix, business schema change,
migration, data cleanup or commit is authorized by this log. Drive rename remains
disabled; further batches require a separate user instruction.

Batch 4B2 resumed after explicit USER approval of the coordinator and sidecar
replacement/version revision. Upload + trusted business binding integration is
COMPLETE/FIXED for its approved scope; fresh targeted 338/0 and full 1092/2.
The two failures are reproduced historical mobile 500s. SEC-04 remains OPEN:
public static serving, private read gateway, PWA and legacy verification are not fixed.

Batch 4B3 subsequently implemented the authenticated read gateway and excluded
uploads from the parent public static mount. Fresh final validation: 531 targeted
PASS/0 FAIL; full 1623 PASS/2 reproduced historical mobile FAIL. SEC-04 remains
OPEN: service-worker Cache API and verified legacy resolution are not implemented.

Batch4B4 subsequently implemented narrowly scoped service-worker private-cache
exclusion and app-owned old-cache invalidation. Actual SW Node event/cache
simulation plus synthetic gateway replay:314/0; fresh full1937/2 historical mobile
FAIL. Real browser NOT RUN; production-client rollout NOT VERIFIED. SEC04 OPEN;
4B5 verified legacy resolution NOT STARTED.

## 2. Completed Phases

Batch4B5A legacy provenance foundation: COMPLETE/FIXED deliverable,234/0 targeted,
2171/2 full, production integrity clean. Registryv3 only, no business migration or
production activation. Original4B5 audit stays historical BLOCKED;4B5 workflow may
resume only after USER review. SEC04 OPEN. See dated4B5A section for exact evidence.

| Work | Status | Outcome and evidence | Limit |
| --- | --- | --- | --- |
| Phase A | FIXED | COMPLETE: CRM router/background startup/desktop and mobile UI disabled; QuoteFlow launch/provisioning removed from shared scripts; dedicated QuoteFlow Nginx template block removed. Static checks PASS. | Production runtime/services were not launched or changed. Source/data retained; Phase B not performed. |
| Core audit | FIXED | Requested read-only audit completed; 27 Core Python AST parses, 28 Core Jinja parses and diff check PASS. | Findings themselves remain open unless noted below; audit did not run production app. |
| Batch 1 | FIXED | Runtime sandbox PASS; synthetic actors/data; all 11 Core routers loaded. Sandbox safe for security fixes = YES through guarded runner. | Trusted application-code test guard, not an OS boundary against malicious native code. |
| Batch 2A / SEC-03 | PARTIALLY FIXED | Anonymous upload 200 before fix → 401 after fix. Authenticated uploads work. Anonymous rename 401; authenticated rename fails closed 403. | No trusted Drive ownership metadata; authorized rename remains BLOCKED. |
| Batch 2B.0 design audit | FIXED | Design deliverable completed after resumption; outcome is audit completion only. Flow/ownership/legacy/static/cache analysis and implementation test plan recorded below. | SEC-04 remains OPEN; no production implementation or new runtime test. |
| Batch 2B.1 upload identity foundation | FIXED | Local collision scope completed: UUID filenames, exclusive create, bounded collision retry; 13 targeted checks PASS. | BUG-10 PARTIALLY FIXED: numeric validation unchanged. SEC-04 OPEN; no registry/gateway/static/cache changes. |
| Batch 3A SEC-05 design audit | FIXED | Audit deliverable completed: endpoint/actor inventory, source-confirmed ID bypass, policy decisions, proposed architecture and regression matrix below. | SEC-05 OPEN. Source evidence only; no new runtime tests or production code changes. |
| Batch 3B SEC-05 implementation | PARTIALLY FIXED | Approved matrix implemented in Task routes/service/new centralized policy; dedicated sandbox tests added. Diff reviewed. | Sandbox NOT RUN for Batch 3B before user's stop/review instruction. No runtime acceptance or regression PASS claimed. SEC-05 PARTIALLY FIXED. |
| Batch 3C SEC-05 runtime validation | PARTIALLY FIXED | Guarded runner executed once on current snapshot; isolation/import and 11 routers PASS, production integrity PASS. | Validation FAIL/incomplete: IndexError in CREATE suggested-ID test; runtime_results.json not written. No code/test changes or rerun. SEC-05 remains PARTIALLY FIXED. |
| Batch 3D harness repair + SEC-05 validation | FIXED | Fresh run complete: SEC-05 530 PASS / 0 FAIL; total 677 PASS / 2 known mobile FAIL; SEC-03 84 and collision 13 PASS. | Production code unchanged; DB/data integrity PASS. SEC-05 FIXED only for approved Task scope; other security findings remain. |
| Batch 4A SEC-04 final architecture audit | FIXED | COMPLETE design deliverable: current-source evidence, recommended sidecar/gateway/lifecycle/cache architecture, implementation slices and required user decisions below. | SEC-04 OPEN; only documentation updated. No registry, app/runtime, schema, file move or source change. |
| Batch 4B1 SEC-04 metadata foundation | FIXED | COMPLETE: lazy SQLite sidecar v1, metadata primitives and fail-closed tests; 77 targeted PASS including 14 concurrency/13 fail-closed. Fresh total 754 PASS / 2 known mobile FAIL. | SEC-04 OPEN; no upload/business/static/cache integration and no production registry created. |
| Batch 4B2 upload/binding integration | FIXED | COMPLETE after USER scope approval: new authenticated upload registration, Task/report/Document/forward binding, replacement/clear and sidecar v2. Fresh targeted 338/0; foundation77, SEC05 530, SEC03 84, collision13 PASS; total1092/2. | SEC04 OPEN. No gateway/static/cache/legacy activation; no production registry/upload created. Separate business/sidecar commits require fail-closed compensation/reconciliation. |
| Batch 4B3 private gateway/static exclusion | FIXED | COMPLETE within approved scope: exact upload route before parent mount, independent parent exclusion, readonly registry/live object/ACL/size/hash checks; targeted531/0; full1623/2; all prior security regressions PASS. | SEC04 OPEN. Actual production Nginx NOT VERIFIED; real Windows symlink/junction creation NOT FULLY TESTABLE. PWA Cache API/legacy onboarding/session fixes not performed. |
| Batch4B4 PWA private cache protection | FIXED | COMPLETE within approved scope: SWv2 private/dynamic network-only, old QLCV private entries purged, vetted public entries preserved; targeted314/0, fresh full1937/2; gateway531/prior security groups PASS. | Evidence is Node VM actual SW + synthetic CacheStorage/network + actual synthetic gateway replay, not a real browser/production client test. SEC04 OPEN;4B5 not started. |

## 3. Security Findings

CONFIRMED means demonstrated from source unless runtime tests are explicitly
listed. HIGH identifies a source-supported risk whose exploit/extent needs
runtime validation. No unfixed finding is treated as resolved by a general smoke
test.

| ID | Severity | Description | Status | Files Changed | Tests | Remaining Risk |
| --- | --- | --- | --- | --- | --- | --- |
| SEC-01 | P0 | CONFIRMED: reserved employee IDs in default tenant can grant master identity; employee creation does not reserve these IDs. | OPEN | None for this finding | Dedicated escalation test NOT RUN | Cross-company administration escalation is conditional on default-tenant employee-management privilege. |
| SEC-02 | P0 | CONFIRMED: untimed signed session; no server-side expiry/revocation or current user/role/company revalidation. | OPEN | None | Replay/revocation tests NOT RUN | Browser logout smoke PASS does not prove copied-session revocation. |
| SEC-03 | P0 | CONFIRMED: upload/Drive mutation endpoints previously lacked auth and ownership checks. | PARTIALLY FIXED | routes/documents.py; tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md | 84 SEC-03 regression checks PASS; anonymous upload now 401, legitimate uploads succeed; denied rename makes zero Drive mutations | Authorized Drive mutation BLOCKED by missing trusted ownership mapping; session weaknesses remain. |
| SEC-04 | P0 | Historical public upload exposure;4B3 online gateway/parent exclusion and4B4 SW private-cache protection implemented. | OPEN | 4B1/4B2/4B3 foundation;4B4 static/sw.js and tests/docs/checklist/log only | Current PWA314/0, gateway531/0; full1937/2 historical mobile;4B2 338,registry77,SEC05 530,SEC03 84,collision13 PASS | Verified legacy/UNKNOWN resolution remains4B5, not started. Real browser/production clients and actual Nginx not verified. Existing session/tenant findings remain separate. |
| SEC-05 | P0 | Approved action-specific Task policy, server CREATE identity, existing-object-first mutation and exact tenant-local target validation implemented in Batch 3B, validated in Batch 3D. | FIXED | Batch 3B: routes/tasks.py; services/task_service.py; new services/task_policy.py. Batch 3D: tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; this log | Current guarded run: 530 SEC-05 PASS / 0 FAIL; matrix, bypass, tenant, zero-mutation and suggested-code auth PASS | Session/tenant resolver risks SEC-01/02/06/07 remain; dashboard/AI/mobile query drift and public files SEC-04 remain outside this fix. |
| SEC-06 | P0 | HIGH: tenant path construction lacks confinement validation. | OPEN | None | Production resolver exploit NOT RUN; sandbox traversal guard PASS is test isolation only | Risk through master operations; sandbox guard does not fix production resolver. |
| SEC-07 | P0 | HIGH: prefix email lookup/fallback and global index updates without tenant ownership validation. | OPEN | None | Dedicated ambiguous-identity/index tests NOT RUN | Wrong routing/mapping possible; password bypass not demonstrated. |
| HARD-01 | P2 | HIGH: unescaped HTML sinks in Task/metadata/mobile and unsanitized AI Markdown HTML. | OPEN | None | Browser XSS test NOT RUN | Exploitability varies by input privilege/sink. |
| HARD-02 | P2 | HIGH: broad credentialed CORS, no CSRF guard found, cookie lacks Secure flag. | OPEN | None | Browser origin/CSRF tests NOT RUN | SameSite=Lax mitigates some cases; blanket cross-site exploit not claimed. |
| HARD-03 | P2 | HIGH: PWA authenticated/static cache and fallback policy; missing manifest icons confirmed. | OPEN | None | Browser offline/shared-device tests NOT RUN | Private cached content may survive logout; offline API may receive HTML. |
| HARD-04 | P2 | HIGH: deployment template root service/public HTTP backend, TLS not established by template; port/readiness inconsistency. | OPEN | None for this finding | Live deployment test NOT RUN | Actual production proxy/TLS topology not verified. |
| HARD-05 | P2 | CONFIRMED: fixed default user password; missing signing configuration creates per-process key and logs it. | OPEN | None | Credential/multiworker tests NOT RUN | Default accounts and inconsistent worker sessions remain concerns. |

## 4. Runtime Bugs

| ID | Severity / confidence | Description | Status | Validation / next test |
| --- | --- | --- | --- | --- |
| BUG-01 | P1 / CONFIRMED | Mobile uses nonexistent Task fields. | OPEN | Sandbox /mobile and /mobile/tasks both 500 with Task data. |
| BUG-02 | P1 / CONFIRMED from source | Mobile AI payload/response mismatch, wrong logout method, JS strip() call. | OPEN | Browser contract/logout/search tests NOT RUN. |
| BUG-03 | P1 / CONFIRMED from source | Dynamic Task route precedes get-temp-id route. | OPEN | Dedicated route-flow test NOT RUN. |
| BUG-04 | P1 / CONFIRMED from source | MST rename failure does not prevent master/index update; cache/session lifecycle inconsistent. | OPEN | Lock/failure/multiworker test required in sandbox. |
| BUG-05 | P1 / CONFIRMED from source | Startup DATABASE_URL and default request resolver can point to different DBs. | OPEN | Custom DB configuration test required. |
| BUG-06 | P1 / CONFIRMED from source | Multi-stage tenant/index/Process commits can leave partial data. | OPEN | Failure injection/reconciliation tests required. |
| BUG-07 | P1 / HIGH | Startup sync ordering and concurrent code allocation/multiworker startup. | OPEN | Old/new schema and concurrency tests required. |
| BUG-08 | P1 / CONFIRMED from source | Task list ignores CC and differs from role-based detail visibility. | OPEN | List/detail/dashboard matrix required. |
| BUG-09 | P1 / CONFIRMED from source | JD view fallback is absent in export. | OPEN | JD variants/export tests required. |
| BUG-10 | P1 / CONFIRMED | Local filename collision/overwrite fixed by UUID plus exclusive create; numeric payload validation remains incomplete. | PARTIALLY FIXED | Batch 2B.1: 13 collision/concurrency/filename checks PASS, including forced existing-ID retry/exhaustion; numeric null/overflow/bounds not fixed. |
| CLEAN-01 | P3 / CONFIRMED from source | Scattered policies/error contracts; expiry check targets a field absent from master model. | OPEN | Contract/policy review; no cleanup performed. |

## 5. Mobile/PWA Bugs

- /mobile = 500 and /mobile/tasks = 500 remain baseline failures, not Batch 2A
  regressions (BUG-01).
- Mobile AI/logout/search mismatches and session/template field differences
  remain source findings; no browser fix/test performed (BUG-02).
- Missing manifest icons and cache/fallback/logout concerns remain open
  (HARD-03). Private file cache implications must be considered in SEC-04 design.
- Batch 2A did not modify mobile files. Preserve existing uncommitted mobile/PWA
  changes. No CRM mobile functionality is to be restored.

## 6. Files Modified By Codex

| Phase/batch | Files | Attribution |
| --- | --- | --- |
| Phase A | app.py; routes/mobile.py; templates/layout.html; templates/mobile/layout.html; templates/mobile/dashboard.html; templates/help_guide.html; chay_app.bat; run_vps.bat; deploy_vps.sh; nginx_vps_default.conf | Only CRM/QuoteFlow disabling hunks; several files already contained user changes. |
| Batch 1 | tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; .test_runtime/.gitignore | New harness/documentation/ignore rule; generated sandbox snapshots/data/reports remain ignored. |
| Batch 2A | routes/documents.py; tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md | Auth and fail-closed guards plus regression tests/documentation. document_service.py and drive_service.py unchanged. |
| Documentation initialization | CODEX_AUDIT_FIX_LOG.md | New retrospective reviewer handoff only. |
| Batch 2B.0 completion | CODEX_AUDIT_FIX_LOG.md | Completed private-file design, evidence, blockers, scope and test plan only. |
| Batch 2B.1 | services/drive_service.py; tests/runtime_sandbox.py; CODEX_AUDIT_FIX_LOG.md | Only local filename allocation, targeted regression tests and this handoff. routes/documents.py unchanged from Batch 2A. |
| Batch 4B2 | NEW services/file_binding_service.py; services/file_registry.py; services/drive_service.py; routes/documents.py; routes/tasks.py; services/task_service.py; config.py; tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; this log | Only approved upload/binding and sidecar v2 integration. config adds storage root identifier; prior port/path changes are not 4B2. Existing Task policy/mobile/VPS/Phase A work retained. |
| Batch 4B3 | NEW services/file_access_service.py; app.py; services/file_registry.py; routes/documents.py; tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; CODEX_REVIEW_CHECKLIST_4B3.md; this log | Gateway, parent exclusion, readonly snapshot and exact existing Document predicate extraction only. No config/Task policy/Task flow/drive/PWA/deployment/schema changes. Historical 4B2 checklist unchanged. |
| Batch4B4 | static/sw.js; tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; NEW CODEX_REVIEW_CHECKLIST_4B4.md; this log | Only SW cache policy/lifecycle plus embedded test-only Node VM and synthetic gateway replay. No production Python, manifest, templates, registry/gateway semantics or deployment edits. Historical checklists preserved. |

Do not attribute pre-existing config.py, main_launcher.py, vps_default.conf,
deployment documentation, mobile/PWA additions or other user work to Codex.
No file deletion, production data modification or commit was performed.

## 7. Test Infrastructure

Runner (existing project venv; no package installation):

```powershell
.\venv\Scripts\python.exe -B tests/runtime_sandbox.py
```

- Fresh .test_runtime/run-* Core snapshot each run; tests do not import the live
  checkout app. No production database/upload/seed/env/credential copies.
- Synthetic Company A/B actors: ADMIN, MANAGER, USER; separate default-tenant
  synthetic ADMIN exercises existing master login behavior.
- Fail-closed engine/SQLite/path/write guards, SQLite ATTACH denial, network and
  subprocess blocking; narrowly scoped Windows asyncio socketpair exception.
- Provider stubs; Batch 2A recording Drive stub detects denied mutations.
- Before startup: resolver/engine/source/router assertions and eight denial
  probes. Integrity checks use hash, size and mtime; changes stop testing without
  automatic rollback.
- Existing bugs are recorded as baseline failures, so process exit 0 alone does
  not mean every business test passed. Read runtime_results.json.

## 8. Latest Test Results

**Latest completed run: Batch4B4, reviewed 2026-10-01 08:07 +07:00**:
`.test_runtime/run-7b3e6a1e3b29440fb38ff3a24dfc2c5d/`.
Complete=true: **1937 PASS / 2 FAIL**, 1939 checks; PWA **314/0**, gateway531/0.
4B2 338/0; registry77/0; SEC05 530/0; SEC03 84/0; collision13/0.
Only failures: `/mobile`500 and `/mobile/tasks`500 expected200, reproduced
historical baseline. No new regression. Core smoke/11routers PASS; provider0;
guard violations empty; preflight PASS; integrity unchanged; source manifest
including static/sw.js matches current tested snapshot. Production registry/upload
created NO. Deterministic SW/cache runtime PASS; real browser NOT RUN.

**Historical completed run: Batch 4B3, reviewed 2026-10-01 06:37 +07:00**:
`.test_runtime/run-9dc4c7d902ef4445a5f90e9f836874ef/`.
Complete=true: **1623 PASS / 2 FAIL**, 1625 checks; gateway **531/0**.
4B2 338/0; registry77/0; SEC05 530/0; SEC03 84/0; collision13/0.
Only failures: `/mobile` and `/mobile/tasks` HTTP500 expected200, reproduced
historical baseline. No new regression. Core smoke/11 routers PASS, provider
mutation count0, guard violations empty. Preflight PASS, protected production
DB/data hashes/size/mtime unchanged, source_manifest matches current Core snapshot.
Production registry/upload created NO. See Batch4B3 evidence section below.

**Historical completed run: Batch 4B2, 2026-10-01 05:34 +07:00**:
`.test_runtime/run-a81a2e790b8045a4ba8bf00ee958c0f3/`.
`runtime_results.json` complete=true: **1092 PASS / 2 FAIL**, 1094 checks.
Targeted4B2 **338/0**: UPLOAD36, BIND239, REPLACE13, FAILURE33,
CONCURRENCY12 (including five independent-process replacement checks), SCHEMA5.
Regression: REGISTRY77/0; SEC05 530/0; SEC03 84/0; BUG10 collision13/0.
Login/dashboard/tasks/logout PASS; all11 Core routers true; Drive mutation count0.
Only FAIL: mobile dashboard `/mobile`=500 and mobile tasks `/mobile/tasks`=500,
expected200, exactly the historical baseline. No new observed regression.
Preflight PASS; integrity.json before==after for all10 protected files including
SHA-256/size/mtime. Current Core Python snapshot hashes match source_manifest.json.
Production registry/upload created NO. No external provider request.

**Historical completed run: Batch 4B1, 2026-09-30 22:33 +07:00**:
`.test_runtime/run-c00b7009fb654fb9ae233e7670be6da5/`.
Complete report: **754 PASS / 2 FAIL**, 756 total. Registry foundation **77/0**,
concurrency subset **14/0**, fail-closed subset **13/0** (subsets overlap).
SEC-05 **530/0**, SEC-03 **84/0**, BUG-10 collision **13/0**. Login/dashboard/tasks/
logout and 11 routers PASS. Only two current mobile500 baseline failures.
Preflight/integrity/source snapshot PASS, guard violations empty, provider calls0.
An earlier run with thread-only registry tests passed 72/0 and total749/2 at
run-9cfa27371b504e00bdc17c473177dc0f. Fresh rerun added actual two-process tests;
no production behavior fix or expectation change between those runs.

**Historical completed run: Batch 3D, 2026-09-30 21:17 +07:00**:
`.test_runtime/run-601a577af1c54f719542bfde7f8da525/`.
`runtime_results.json` complete=true: **677 PASS / 2 FAIL (679 total)**.
SEC-05: **530 PASS / 0 FAIL**. SEC-03: **84 PASS / 0 FAIL**.
BUG-10 collision: **13 PASS / 0 FAIL**. Only failures: mobile dashboard and mobile
tasks, actual HTTP 500 vs expected 200; same two historical baseline cases,
confirmed in current run. No new regression. Preflight PASS / 11 routers, no guard
violations, Drive mutation count=0. Integrity before/after equal, source unchanged.
These are current-run counts; earlier sections below preserve historical attempts.

**Latest attempt: Batch 3C, 2026-09-30 21:07 +07:00**. Exact directory:
`.test_runtime/run-66c003f48123430e8bb962332aeb457f/`.
Runner executed once; exit 1, IndexError at tests/runtime_sandbox.py:492.
`runtime_results.json` is absent because the worker writes it only at normal end.
Total sandbox and SEC-05 targeted PASS/FAIL counts are **UNAVAILABLE**, not zero
and not the historical 147/149. Full matrix/bypass/tenant/zero-mutation acceptance
is **NOT PROVEN**. Detailed failure and evidence are recorded below.
`preflight.json` PASS with all 11 Core routers. `integrity.json` before/after equal,
production_data_modified=false; source_manifest.json matches current Core source.
AST parse of all four requested files PASS; git diff --check PASS. Import of Core
and new Task policy completed inside the isolated worker, not production.

The Batch 3B NOT RUN statement below is historical for that implementation batch;
Batch 3C is a new attempted run, not a successful completion.

Batch 3B: **NOT RUN**. No guarded runner invocation occurred before the user
requested review/documentation only and prohibited further execution/changes.
The following Batch 2B.1 results remain historical; they do not validate the
current Batch 3B source snapshot. SEC-05 matrix/bypass/zero-mutation assertions
have been added to the harness but have not executed.

Historical completed runtime run: Batch 2B.1,
`.test_runtime/run-46b82e21daba4fa588e4ce4f07201b2a/`.

| Check | Outcome |
| --- | --- |
| Overall | 149 checks: 147 PASS, 2 FAIL (known mobile baseline) |
| BUG-10 collision foundation | 13 targeted checks PASS: same-name uploads, 16 rapid uploads, 8 synchronized concurrent uploads, byte preservation, UUID path shape, forced ID collision retry, exhausted retries without overwrite, traversal confinement, validated extension preservation and blocked extension case-insensitivity |
| SEC-03 regression | 84 checks PASS |
| Anonymous local upload | Before 200; after 401; no upload file created |
| Valid authenticated local upload | ADMIN/MANAGER/USER allowed; saved content checked |
| Invalid session | Upload/rename 401 |
| Drive rename | Anonymous 401; authenticated/cross-tenant/ADMIN requests 403 |
| Drive provider mutation | 0 calls; no real provider request |
| Authorized Drive ALLOW | BLOCKED; cannot prove ownership with current metadata |
| Login/dashboard/tasks/logout | PASS |
| Core router inventory | All 11 loaded |
| Unexpected isolation violations | 0 |
| Static validation / diff check | Python AST PASS; git diff --check PASS |

Earlier Batch 1 run: 52 checks, 49 PASS, 3 baseline FAIL (anonymous upload plus two
mobile pages). The anonymous upload failure was resolved in Batch 2A; mobile
failures remain. Batch 2A: 136 checks, 134 PASS, two mobile FAIL; its evidence is
preserved. Batch 2B.0 ran no new runtime test. Batch 2B.1 reran the guarded sandbox
after the filename fix; all 84 SEC-03 checks and Core smoke tests still PASS.

Batch 2B.1 physical identity is uuid4().hex plus the validated extension, independent
of client basename and timestamp. open(..., "xb") atomically refuses existing
paths; up to eight generated candidates are tried, then upload fails without
overwriting. URL prefix, original UI filename, size limit and extension checks
remain unchanged. No legacy filename or DB URL is modified. No new ownership
claim can be inferred merely from a UUID filename.

## 9. Production Integrity

Latest Batch4B2 fresh run: all10 protected DB/data/upload fingerprints equal
before/after (SHA-256, size, mtime_ns). Independent pre-resume/post-run snapshot
also matches. PRODUCTION DB MODIFIED=NO; PRODUCTION DATA MODIFIED=NO;
PRODUCTION REGISTRY CREATED=NO; PRODUCTION UPLOAD CREATED=NO.
Selected Core fingerprints changed only config.py, documents/tasks routes,
drive/file_registry/task services and NEW file_binding_service.py, all explicitly
approved. Untouched Core/source snapshots match; no business SQL migration/seed,
production startup, provider request, physical legacy move/delete or cleanup.

- Phase A protected data existence/metadata checks passed; no data operations.
- Batch 1: PRODUCTION DB MODIFIED = NO; PRODUCTION DATA MODIFIED = NO.
- Batch 2A: PRODUCTION DB MODIFIED = NO; PRODUCTION DATA MODIFIED = NO.
- Batch 2B.1: PRODUCTION DB MODIFIED = NO; PRODUCTION DATA MODIFIED = NO;
  guarded runtime integrity report compared SHA-256, size and mtime unchanged.
- Current Batch4B4 completed runtime integrity report:
  `.test_runtime/run-7b3e6a1e3b29440fb38ff3a24dfc2c5d/integrity.json`.
  All10 protected production fingerprints unchanged; registry/upload createdNO;
  current source manifest including SW matches final tested snapshot.
- Historical Batch2B.1 runtime integrity report:
  `.test_runtime/run-46b82e21daba4fa588e4ce4f07201b2a/integrity.json`.
- Database inspection during the unfinished design audit was read-only, with
  read-only immutable SQLite connections and no application startup. No database
  values or real filenames are reproduced here.
- Resumed Batch 2B.0: 10 protected-file fingerprints (hash/size/mtime) unchanged;
  60 selected Core source/asset fingerprints unchanged. Production DB/data
  modified = NO / NO. Only this documentation file is updated.
- Batch 3A: source-only audit, no application import/startup or DB queries;
  protected-file and selected Core fingerprints checked before/after. Production
  DB/data modified = NO / NO. Only this documentation file is updated.
  Comparison PASS: hash, size and mtime identical; selected Core source/asset
  comparison PASS. Git diff --check PASS; tracked diff remains the preexisting
  13 files, 98 insertions / 143 deletions. Central log is already untracked.
- Batch 3B review: protected-file SHA-256/size/mtime snapshot before edits and
  after edits matches. PRODUCTION DB MODIFIED = NO; PRODUCTION DATA MODIFIED = NO.
  No app startup, sandbox runtime, DB query, migration, seed or provider action
  occurred in this batch. This is an edit/review integrity check, not a runtime
  acceptance report.
- Batch 3C: independent pre/post snapshot and new runner integrity report agree:
  all 10 protected files unchanged (SHA-256, size, mtime). PRODUCTION DB MODIFIED
  = NO; PRODUCTION DATA MODIFIED = NO. Core snapshot hashes unchanged. Synthetic
  A-tenant DB inspected read-only after failure; production DB not queried.
- Batch 3D: all 10 protected files unchanged by independent SHA-256/size/mtime
  comparison and fresh runner integrity report. PRODUCTION DB MODIFIED=NO;
  PRODUCTION DATA MODIFIED=NO. Selected Core source/asset fingerprints unchanged;
  fresh source_manifest matches current production code. No production app/seed,
  migration, DB query, provider action or source change used.

No production app startup, migration, seed, tenant delete/MST change, upload
cleanup or external provider request was used to validate the fixes.

## 10. Blocked Items

| Item | Status | Reason / required decision |
| --- | --- | --- |
| Authorized Drive rename and its ALLOW test | BLOCKED | No trusted Drive file-to-tenant/owner mapping. Editable URLs and client IDs are insufficient. No schema/migration authorized; keep all three rename endpoints disabled. |
| Guaranteed private legacy-file ownership | BLOCKED | Current URL fields establish references, not trustworthy physical-file ownership. Legacy ambiguity requires an explicit trusted mapping/deny policy before claiming cross-tenant isolation. |
| Real-browser/production-client private-cache verification | DEFERRED |4B4 actual SW Node simulation and gateway replay PASS. Real browser NOT RUN, deployed clients/update NOT VERIFIED; policy applies after new worker activation, not copied-session revocation or arbitrary third-party/browser-memory/download cleanup. |

## 11. Open Findings

SEC-01, SEC-02, SEC-04, SEC-06, SEC-07; HARD-01 through HARD-05;
BUG-01 through BUG-09; CLEAN-01 remain OPEN. SEC-03 and BUG-10 remain PARTIALLY
FIXED. SEC-05 is FIXED after Batch 3D approved-policy runtime acceptance.
BUG-10 collision scope is fixed; numeric validation is still open.

No Identity/Session batch, mobile fixes, Phase B CRM/QuoteFlow cleanup or legacy
onboarding work has occurred. Batch4B3 protects online FastAPI upload reads;
Batch4B4 protects application-managed private Cache API use. SEC04 remains OPEN
for verified legacy resolution; real-browser/production rollout not verified.

## 12. Next Recommended Batch

Current Batch4B4 is COMPLETE for its source/simulated-runtime scope. Request USER
review of its diff/checklist/evidence first, including real-browser validation
limitations. Batch4B5 requires separate authorization for verified custodian-
reviewed legacy mapping; it is NOT STARTED. No production rollout performed.
SEC04 remains OPEN.

Historical recommendation after Batch4B1: approved architecture supersedes prior approval
requests for sidecar, UNKNOWN deny-all, uploader-only24h UNBOUND, vetted same-tenant
parent/child union bindings, future network-only cache/purge, exact URL and
custodian-reviewed tool-assisted legacy verification. Recommend separately
authorized 4B2 upload/binding integration with PENDING -> business commit -> exact
revalidation -> ACTIVE. Do not activate gateway/cache or start4B2 automatically.
Historical recommendations below are retained as context, not current blockers
already resolved by USER approval.

Batch 3A design is complete; user approved the action matrix in Batch 3B.
Batch 3D corrected the harness-only failure and completed fresh SEC-05 acceptance:
SEC-05 FIXED. Recommend separately authorized SEC-04 ownership/gateway scope
planning using the now-tested Task READ capability; current batch does not create
registry/gateway, change static/cache policy, or start another finding.
Historical design ambiguities below are superseded by the approved matrix where
specified. Batch 2B.0 design and
Batch 2B.1 collision prerequisite are complete. Before
authorizing further implementation, decide trusted
legacy ownership mapping, UNKNOWN-file denial, proposed non-SQL metadata storage
and narrow service-worker cache scope. Recommended implementation is Option C
plus Option A's private file gateway, with no DB rewrite or physical file move.
Full Task ACL safety still depends partly on SEC-05; no Task policy rewrite is
authorized here.

Do not start Batch 2B implementation or reopen Drive rename automatically.

### Batch 2B.0 evidence and file flow

Shared flow: authenticated /api/drive/upload-local -> DriveService.upload_local_file
-> Config.UPLOAD_DIR (default static/uploads) -> server-generated filename
  (timestamp-based at design time; UUID after Batch 2B.1)
-> root-relative /static/uploads/... URL plus original name returned to browser
-> a later Task/Document save stores the client-submitted URL string. Upload
itself stores no tenant/uploader registry. Size/extension checks stay unchanged.

| Type | Persisted relationship / active consumer | Authorization capability / limitation |
| --- | --- | --- |
| Task attachment | tasks.file_giao_viec; id_phan_cong is Task key. tasks/index.html uses upload res.url in data-url, save payload link; TaskService stores it and returns link. | Existing detail read check permits ADMIN/assigner/receiver/CC; tenant comes from signed session DB selection. No trusted physical-file tenant/uploader ownership. |
| Report attachment | tasks.file_bao_cao; report.html sends linkBaoCao; TaskService.update_bao_cao stores latest nonempty link; detail API returns file_bao_cao. | Same Task relationship/read policy. Current report page does not render the returned existing file_bao_cao field. No per-report file entity/history/uploader metadata. |
| Forward attachment | forward.html uploads and submits payload link. TaskService.save_forward ignores that link and copies parent.file_giao_viec into child.file_giao_viec. | Child Task permissions may differ. New uploaded forward file may remain unbound; no reliable independent delegation-file relationship. Record behavior only; do not fix during SEC-04 design. |
| Document library | documents.link_file keyed by ma_tl; documents/index.html stores res.url through linkFile and renders direct href. repository.html receives previewUrl, fetches DOCX or sets iframe.src. | ADMIN/CEO all tenant documents; others general/own department; MANAGER includes direct subordinate departments. Document ACL is available, but edited URL does not establish physical ownership. |
| Personal attachment | personal_tasks.file_dinh_kem with task id/user_id; raw model serialization exposes field. PersonalService supports writes but is not called by active routes; active create/update omit this field and UI has no attachment flow found. | Row ownership exists via user_id/session. Physical-file/uploader ownership remains UNKNOWN. Treat any existing reference as legacy, not a verified new upload. |
| AI / mobile | No dedicated attachment upload/read/preview pipeline found in active AI/mobile source. Mobile links to desktop Task pages; PWA service worker can cache static files. | No separate mobile/AI file ACL to reuse. Desktop gateway rules apply when accessed through those pages; cache behavior is a separate blocker. |

Evidence anchors: models/models.py:48,49,59,86; services/drive_service.py:66-104;
services/task_service.py:156,174,217,272; templates/tasks/forward.html:350;
templates/tasks/index.html:586-598; routes/documents.py:85-169;
templates/documents/repository.html:241-268; routes/personal.py:120-173;
static/sw.js:34-54.

Task/Document/Personal rows have object IDs and an implicit tenant DB context;
only Personal has explicit user ownership. No attachment model has a separate
file ID, trusted uploader, upload timestamp or persisted original filename.
Document.ngay_cap_nhat is record update date, not upload provenance; Task schedule
dates are not upload timestamps. Returned original filename is UI-only metadata.

Normal physical rename/delete/download endpoints for local attachments were not
found. Drive rename is disabled. Upload oversize cleanup removes its partial
file; Document/Personal delete removes the row, not the physical attachment.
Process/JD exports stream generated content separately; they are not uploads.

### Legacy classification and compatibility

- Read-only aggregate inspection confirmed existing Task and Document fields
  contain full root-relative /static/uploads/... URLs. No bare filename or
  absolute-host upload URL appeared in the inspected fields. This describes the
  inspected databases, not all historical backups or external deployments.
- Core template/JS consumers use returned/stored URLs; no hard-coded uploads
  prefix construction was found in the reviewed active consumers. The upload
  service constructs the prefix. External and local_docs links also exist as
  supported source formats; do not convert/proxy them as local upload files.
- Task openCurrentLink currently prepends https:// to a root-relative link;
  that is an existing relative-link consumer issue, not a URL migration solution.
- PUBLIC: established CSS/JS/images/manifest/PWA assets outside uploads.
  No legitimate public-upload asset use was established. Upload files are
  private candidates; existing unverified files/references are UNKNOWN/LEGACY
  and must fail closed. Extension, filename, single-tenant reference or current
  public hosting cannot determine privacy/ownership.
- Losing/changing a DB reference can orphan a file. Duplicate/shared references,
  deleted objects, overwritten names and new unsaved/forward uploads need a
  conservative policy; do not grant access by searching only the requester's DB.
  A user can insert a known other-tenant URL into their own Task.

### Static exposure root cause

app.py:59 mounts uploads publicly; app.py:62/66 mounts the entire static tree.
Removing only the first mount leaves a parent-static path to uploads. Existing
mounts precede included API routers, so a late registered legacy route will not
override the upload mount. StaticFiles limits filesystem containment but does
not authenticate users or apply tenant ACLs (local framework source inspected).

Future protection must cover GET/HEAD, normalized/encoded aliases, Windows path
case/separators and realpath/junction/symlink resolution. Keep public assets,
manifest and service worker working. Nginx templates proxy requests today; check
actual deployment for a direct static alias before claiming end-to-end coverage.
Optional public local_docs exposure is a separate unresolved surface.

### Options comparison

| Option | Security | Compatibility | DB migration / file migration | Multi-tenant suitability | Rollback / complexity / risk |
| --- | --- | --- | --- | --- | --- |
| A: files stay, authenticated gateway | Strong only with trusted ownership, ACLs and parent-static exclusion | API response adapters can rewrite local URLs without changing DB, but old bookmarks need compatibility | NO / NO | Good with server-owned registry; DB URL match alone insufficient | Moderate-high complexity; controlled rollback. Removing new gateway without restoring an insecure public path is preferable. |
| B: private storage outside static | Strong filesystem boundary, still needs ownership/ACL | Requires logical aliases for stored old URLs | DB rewrite avoidable / YES physical moves | Good; can physically separate tenants | Highest move/backup/rollback risk; not recommended for immediate batch. |
| C: protect legacy uploads URL | Same security as gateway if all bypasses are excluded | Best: old URLs remain exactly usable for authorized verified files | NO / NO | Good with trusted mapping and scoped ACL | Moderate-high routing/cache/metadata complexity. Preserve files and mapping during rollback; never silently restore public serving. |

### Recommended design (not implemented)

Use C with A's shared authorization gateway. GET/HEAD legacy /static/uploads/...
and optional /api/files/{opaque_id} resolve to one service. Register legacy
handling before mounts, and explicitly exclude uploads from parent StaticFiles,
including canonical aliases. Retain /static for public assets.

Before file bytes, 304 or ranges: authenticate -> canonical path confinement ->
trusted server-owned file mapping -> session tenant equality -> existing object
presence and read authorization -> file response. No client company/owner hint
or arbitrary URL grants ownership. API/file errors must not become the global
HTML-404 dashboard redirect. Use 401 anonymous; 404 for missing/foreign/UNKNOWN
objects without existence disclosure; 403 where safe for same-tenant denial.

Existing SQL schema cannot supply authoritative physical ownership. A proposed
non-public, server-managed metadata registry can avoid DB schema migration:
opaque file ID, tenant, uploader, storage locator, original filename, upload time,
classification and vetted object bindings. This is NEW persistent state requiring
approval, durable atomic writes, multiworker locking/recovery and backup policy;
it must not be a publicly writable manifest or a cache rebuilt from arbitrary URLs.
The registry format/location is not created in this audit.

For legacy files, verified mappings need explicit trusted evidence/review. Unknown
or conflicting ownership stays denied even to tenant ADMIN; do not assign ownership
by filename or an editable reference. Shared files need vetted sharing rules, not
an automatic ACL union across tenants. New uploads need trusted provenance and
binding validation; unbound files should remain uploader-only or denied under an
approved policy. Collision-safe creation was a prerequisite at design time and
has now been implemented/tested in Batch 2B.1. Trusted ownership mapping is still
absent; collision safety alone does not resolve SEC-04.

Trade-off: no SQL migration/file move is feasible, but guaranteed access to every
legacy file is not feasible with existing evidence. Bytes/URLs are preserved;
UNKNOWN files become temporarily unavailable until ownership is verified.

SEC-04 CAN BE FIXED BEFORE SEC-05 = PARTIALLY. Anonymous/static bypass protection
and authoritative tenant checks can precede SEC-05; read predicates can be used
only after a real Task/Document exists and has a vetted binding. Do not use the
helper's missing-Task-returns-True behavior. Broad Task write permissions can
still alter recipients/visibility, so full business ACL safety depends on SEC-05.
This audit does not change that policy or session architecture.

### Exact proposed implementation scope and test plan

No files in this list are modified by this audit. Future minimal/conditional scope:

- app.py: authenticated legacy handler ordering and parent-static exclusion;
  keep assets/manifest/sw functioning. No global error-handler redesign.
- New routes/files.py and services/file_access_service.py (proposed names):
  canonical resolution, vetted mapping and read policy, inline/download response.
- routes/documents.py and services/drive_service.py: future upload provenance
  registration; preserve SEC-03 auth and blocked Drive operations. No folder moves.
- routes/tasks.py and document save handlers: narrowly validate/publish local
  file bindings only if approved; do not rewrite general Task authorization.
- templates/tasks/index.html: relative local link handling if explicitly included;
  Document preview/links need no rewrite with C. Changing report/forward behavior
  is excluded unless separately approved.
- static/sw.js: private-response exclusion and old private-cache invalidation are
  required for logout/offline guarantee. This narrow PWA scope must be authorized;
  not modified here. No mobile business/UI fix.
- tests/runtime_sandbox.py, tests/RUNTIME_SANDBOX.md and this log: future regression
  fixtures, contract documentation and result recording.
- Optional test-only/configuration helper for private metadata location; do not
  modify production env or requirements. Deployment aliases reviewed separately.

Tests before marking SEC-04 fixed (synthetic sandbox only):

1. Anonymous GET/HEAD private file: 401, no bytes or HTML redirect.
2. Same-tenant authorized vetted Task/Document/personal file: ALLOW; unauthorized
   same-tenant: DENY. Verify uploader-only unsaved flow under chosen policy.
3. Cross-tenant: DENY even if requester puts victim URL in own Task/Document;
   deny guessed IDs, forged company parameters, ambiguous/missing mappings.
4. Missing object/file: 404; missing Task cannot authorize via existing helper.
5. Dot-dot, encoded/double encoded traversal, separators, case aliases, drive/UNC
   paths and symlink/junction escape: DENY; public static path cannot bypass gateway.
6. Old stored URL: exact URL works only for verified authorized file; UNKNOWN,
   foreign or orphan reference is denied without changing DB/file. Shared bindings
   and references removed/deleted/replaced follow explicit chosen policy.
7. DOCX fetch, PDF/image iframe, inline/download, Range/HEAD and conditional 304:
   authenticate each request; no bytes leaked by a cache validator.
8. Public CSS/JS/images, manifest, service worker and PWA assets remain available.
9. Browser/PWA: no private cache writes; invalidate prior private cache entries;
   logout then online/offline access through app: DENY, including back navigation.
   No-store alone is insufficient against explicit Cache API storage. Previously
   downloaded/copied bytes outside the app cannot be recalled by server changes.
10. New-upload provenance/binding atomicity, filename collision and multiworker
    registry safety; denied requests must not mutate objects/files/provider state.
11. Existing Batch 1/2A smoke/SEC-03 tests preserved; mobile 500 baseline unchanged;
    production DB/data hash/size/mtime unchanged.

DB migration required: NO for C plus an approved non-SQL registry; optional future
SQL attachment registry is a separate schema decision. File migration required:
NO for recommended C/A; YES only if B chosen. Legacy metadata verification is
still required and is not a DB rewrite or evidence-free ownership assignment.

Implementation blockers: trusted mapping/legacy UNKNOWN policy; durable registry
approval; Task ACL dependency SEC-05; PWA cache scope;
existing session/tenant issues remain open (SEC-01/02/06/07). No claim that this
design resolves those findings or Drive ownership.

### Batch 3A SEC-05: source evidence and action inventory

Audit recorded and final integrity verified 2026-09-30 20:45 +07:00. Production source unchanged. Evidence
confidence CONFIRMED from source; no new runtime/exploit test. Files reviewed:
routes/tasks.py, services/task_service.py, models/models.py, Task index/report/
remind/forward/overdue/report_center templates, database resolver and existing
authentication tenant selection. Startup Excel seeding is not a user Task action.
PersonalTask is a different model and is excluded from this Task policy change.

All Task APIs use get_db's authenticated-session company_mst tenant, except the
session-only temporary-ID bridge. Actor is session ma/role. No Task endpoint
reads client company/MST/database path to choose its DB. Session identity and
resolver weaknesses are separate dependencies, not fixed by this audit.

| Action / method / route | Service and check | ID / client-controlled fields / effect |
| --- | --- | --- |
| LIST GET /api/tasks | get_index_init_data; session required | No Task ID. Only ma == ADMIN lists all; otherwise giver/receiver only. role unused; CC omitted. |
| VIEW GET /api/tasks/{task_id} | get_task_by_id; session + broad helper | Path ID; returns Task details, journals and attachment references. Missing object returns success:false, currently HTTP 200. |
| CREATE/EDIT/ASSIGN POST /api/tasks | save_task_data; session; route new-vs-existing based on ID shape | idPhanCong, maCV, tenCV, nguoiGiao, nguoiNhan, dates, tienDo, status, link, phoiHop, nhatKyBaoCao, noiDungNhacNho. Missing ID/TU DONG forces non-ADMIN giver to session ma; nonempty ID uses broad helper. Service decides CREATE by actual absence. Existing edits can replace giver/receiver/CC/attachment and nonempty journals. |
| REPORT POST /api/tasks/{task_id}/report | update_bao_cao; session + same helper | Path ID overrides client id. Client progress/status/giaiTrinh/linkBaoCao; append journal, increment count, change status/progress and report attachment. |
| DIRECT POST /api/tasks/{task_id}/remind | update_nhac_nho; session + same helper | Path ID; client message. Append SEP CHI DAO and increment count. No saved authenticated director identity. |
| DELEGATE POST /api/tasks/forward | save_forward; session + same helper on parent | Client idPhanCongGoc, nguoiNhanUyQuyen, nguoiGiao, tenCV, ngayKT, phoiHopMoi, txtNote. Child ID server generated from parent and suggested code; child giver client-controlled, default parent receiver. Parent status changed; parent's attachment inherited; submitted link ignored. |
| CHANGE STATUS / PROGRESS | Generic save and report above | No dedicated endpoint; must not allow generic save to bypass action-specific field policy. |
| UPDATE REPORT | No separate report object or edit endpoint | Append via report; generic save can replace whole nonempty nhatKyBaoCao. Permission to rewrite history is not established. |
| ATTACH FILE | POST /api/drive/upload-local then save/report binding | SEC-03 session check permits upload, without Task ID/action check; binding Task link or report link currently uses broad helper. Forward inherits parent link. No ownership proof from submitted URL. |
| VIEW/DOWNLOAD ATTACHMENT | Direct stored URL; not a Task download API | /static/uploads bypasses Task auth (SEC-04). Drive provider rights are not Task authorization. |
| Suggested code GET /api/tasks/suggested-code | get_suggested_ma_cv; no session check | Client prefix drives code lookup in default/session tenant. Not a reservation; anonymous can query code state. Future auth restriction belongs to Task API scope if approved; concurrency allocation BUG-07 separate. |
| POST /api/tasks/set-temp-id; GET /api/tasks/get-temp-id | Session only; no Task object authorization | Client id saved as navigation hint; never an authorization capability. Dynamic GET route shadows get-temp-id (existing BUG-03, not fixed here). |
| HTML /tasks, /tasks/overdue, /tasks/report-center, /tasks/report, /tasks/remind, /tasks/forward | Session only for shells; APIs load data | report/remind/forward take query id or cookie temp_task_id; shell access is not permission to mutate selected object. |
| DELETE | No business Task DELETE endpoint/service/UI action found | Do not add deletion or infer deletion permission. PersonalTask DELETE is unrelated. |

### Current authorization flow

Request -> get_db dependency resolves signed-session company_mst (or legacy/default
fallback) -> handler reads session -> LIST applies its independent giver/receiver
filter, while detail/write handlers call the broad helper -> TaskService loads
and reads/mutates the object -> commit on successful writes. Database dependency
resolution precedes the handler's authentication denial. Actor permission comes
from cookie ma/role, not a fresh employee/role/status lookup in Task handlers.
HTML shells only check session; their subsequent APIs enforce object access.
Denials generally return JSON success:false with HTTP 200, not a distinct HTTP
401/403 contract. Proposed tests must inspect both response semantics and absence
of side effects; any future status-contract change requires consumer review.

### Confirmed root cause and client-ID bypass

1. routes/tasks.py:14-34: ADMIN role OR employee ma ADMIN passes broad helper;
   existing giver, receiver and comma-separated CC pass. Missing Task also returns
   True. No manager/hierarchy/status/action check.
2. routes/tasks.py:176-197: route CREATE detection only tests blank/TU DONG ID.
   Nonempty client ID takes existing-task branch; missing-object helper allows it.
3. services/task_service.py:120-163: actual absence makes CREATE; supplied ID and
   client nguoiGiao retained. A non-ADMIN can select an unused ID and supply another
   employee as giver, bypassing the route's intended server assigner restriction.
4. templates/tasks/index.html:464-473: normal create UI itself fills txtId from
   suggested-code, so this branch is reached by ordinary creates too, not only a
   manually crafted request. UI save submits nguoiGiao at line 505.
5. Existing-task broad readers can also rewrite nguoiGiao/nguoiNhan/CC and logs
   through save. Forward accepts client giver despite UI deriving it from parent
   receiver (templates/tasks/forward.html:229,345; service:268).

Missing object does NOT cause report/remind/forward to create: each service
rejects absence. Only save's upsert converts the missing-object ALLOW into create.
No production exploit was run; existence/permission/CREATE mismatch is proven by
the connected branches, not a newly measured runtime result.

### Actor matrix: CURRENT implementation, not approved business policy

ALLOW here means the authorization gate allows an existing object; other input/
database errors can still make the request fail. MANAGER/USER/CEO have no automatic
override in the helper. Role and relationship are independent dimensions.

| Actor | DETAIL VIEW | LIST | EDIT/ASSIGN/STATUS/BIND | DIRECT | DELEGATE | REPORT | DELETE |
| --- | --- | --- | --- | --- | --- | --- | --- |
| role ADMIN | ALLOW | All only if ma ADMIN; else own giver/receiver | ALLOW | ALLOW | ALLOW | ALLOW | Absent |
| ma ADMIN, other role | ALLOW | All | ALLOW | ALLOW | ALLOW | ALLOW | Absent |
| MANAGER/USER/CEO as assigner | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | Absent |
| MANAGER/USER/CEO as receiver | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW | Absent |
| MANAGER/USER/CEO as CC only | ALLOW | DENY/omitted | ALLOW | ALLOW | ALLOW | ALLOW | Absent |
| MANAGER/USER/CEO unrelated | DENY | DENY/omitted | DENY | DENY | DENY | DENY | Absent |
| Anonymous/invalid signature | DENY | DENY | DENY | DENY | DENY | DENY | Absent |

Director/delegator/reporter are action semantics, not distinct persisted permission
actors. No director/delegator/reporter IDs or parent FK on Task. Forward UI uses
parent receiver as giver. Journals label NV BAO CAO / SEP CHI DAO without actual
actor identity. Employee has phong_ban and nguoi_ql, but Task authorization never
uses them. A past journal label must not grant future rights.

### Evidence-backed proposed policy and BUSINESS DECISION REQUIRED

Read baseline: tenant-local existing Task; ADMIN role/legacy ma override, giver,
receiver or CC as in detail helper. Reconcile list with the approved READ policy;
ADMIN role vs reserved ID and CEO scope need explicit confirmation (SEC-01/02
identity issues are not silently corrected in this batch).

| Actor/action | Supported minimum / uncertainty |
| --- | --- |
| Non-ADMIN CREATE | ALLOW legitimate creation; server giver must be authenticated actor regardless of whether UI supplied an unused ID. Existing explicit route comment is evidence. |
| ADMIN create on behalf | Existing route allows; confirm whether only ADMIN may do so and which tenant-local targets are eligible. |
| Receiver REPORT | ALLOW supported by index help: report is for receiver (line 808); includes progress/status and report attachment. |
| Receiver DELEGATE | Supported by forward UI's parent receiver identity and intermediate-manager workflow; whether every receiver or only management may delegate is AMBIGUOUS. |
| Assigner/management DIRECT | Supported by top-down guide, but assigner role/hierarchy/department reach is AMBIGUOUS. |
| ADMIN unrestricted writes | Implemented today; field/history/status exceptions and role-vs-ma privilege are BUSINESS DECISION REQUIRED. |
| Assigner EDIT/ASSIGN | Generic UI supports assignment/edit; allowed fields, post-start reassignment and history replacement are AMBIGUOUS. |
| Receiver generic EDIT/ASSIGN/DIRECT | Generic buttons enabled, but receiver REPORT semantics do not establish these rights; AMBIGUOUS. |
| CC REPORT/EDIT/DIRECT/DELEGATE | Broad API permits; no affirmative CC write business rule in help/model; AMBIGUOUS. |
| MANAGER unrelated department Task | Current DENY; no department-wide override evidence. Expansion requires BUSINESS DECISION REQUIRED. |
| CEO global READ/WRITE | Service comment says all, implementation not so; BUSINESS DECISION REQUIRED. |
| Reporter UPDATE old report/history | No report identity; rewriting journals is AMBIGUOUS. Do not invent author-owned report objects or schema. |
| DELETE / assigner delete after start | No current feature; no policy to infer or implement. |

UI index:390,422 enables all action buttons for every listed selection without
actor-specific gates. Help:731,743-759 describes management directives/bottom-up
reports; delegation:798; receiver report:808. UI convenience is evidence of a
conflict, not proof that every write is an intended business permission.

### Proposed architecture and dependencies (NOT IMPLEMENTED)

- One centralized policy module: can_view/create/edit/assign/direct/delegate/
  report/change_status/bind_attachment; separate READ from every WRITE capability.
- Build actor from verified session and tenant-local identity; never from payload.
  Existing session expiration/revalidation remains SEC-02, not an automatic scope
  expansion. Missing/invalid tenant context must fail closed in Task boundary;
  global resolver path/fallback remediation remains separate SEC-06/07.
- Load existing Task in authenticated tenant before existing-object authorization;
  absence is not permission. Resolve save CREATE vs EDIT once from DB existence,
  not ID shape; authorize CREATE independently and force legitimate server giver.
  Keep normal UI prefilled-ID compatibility; don't blindly classify every nonempty
  ID as update or require all legacy IDs rewritten. An EDIT cannot fall through
  into CREATE after authorization; operate on the loaded object in the transaction.
- Bind actor/giver server-side per approved action. Validate receiver/CC in the
  same tenant. Validate changes by field/action: generic save must not circumvent
  REPORT/DIRECT/ASSIGN/BIND checks or rewrite privileged history wholesale.
- Services receive authorized object/context, rather than re-resolving an upsert
  after a broad route check. UI capability buttons can mirror policy later;
  backend remains authoritative. Denials must cause zero DB/file mutations.
- Legacy ma ADMIN override/CEO/hierarchy and write-field policy require decisions;
  no new role, registry, FK or report schema is proposed in this batch.

SEC-04 depends PARTIALLY on SEC-05: can_view_task on a tenant-local existing
object is the reusable Task attachment READ check. Do not call any WRITE check
or current missing-object-ALLOW helper. It is necessary, not sufficient: file
gateway still needs independently trusted file-to-tenant/object mapping, safe
binding policy and legacy UNKNOWN denial. Editable Task URLs cannot prove physical
ownership. Inherited forward attachment needs a vetted shared-binding policy.

SEC-06/07: Task route doesn't select DB from client task ID/company query; get_db
uses signed session company_mst, with default fallback (connection.py:21-35).
Tenant path is not confined (multi_tenant.py:35-45); login prefix lookup/fallback
(auth_service.py:54-82) can misroute identity. An ID from B submitted under A
queries A; absent ID may create an A row via upsert, not read B's physical DB.
Same Task IDs may exist in A and B; ID/filename pattern cannot prove tenant.
Action-specific SEC-05 fixes can be developed independently in guarded sandbox,
but end-to-end isolation cannot be declared resolved while SEC-06/07 remain open.
Dashboard/AI/mobile have their own list queries; note policy drift, do not expand
this fix into those modules or fix existing mobile crashes.

### Planned sandbox regression matrix (NOT RUN in Batch 3A)

Use synthetic A/B ADMIN, MANAGER, USER; cross product each role with giver,
receiver, CC and unrelated relationship for VIEW/EDIT/DIRECT/DELEGATE/REPORT.
Expected writes marked BUSINESS DECISION REQUIRED must be resolved before tests
are used as pass/fail acceptance, not guessed by the implementer.

| Case | Expected |
| --- | --- |
| Existing same-tenant giver/receiver/CC VIEW | ALLOW under proposed existing detail READ baseline; LIST align after explicit policy approval. |
| Unrelated MANAGER/USER VIEW or WRITE | DENY; department-wide expansion is BUSINESS DECISION REQUIRED. |
| ADMIN VIEW; ADMIN writes | READ ALLOW baseline; exact write fields/exceptions BUSINESS DECISION REQUIRED. |
| Receiver REPORT with own Task | ALLOW; no forged reporter actor accepted. |
| Assigner/CC REPORT; receiver/CC DIRECT | BUSINESS DECISION REQUIRED; current broad ALLOW is not desired-policy evidence. |
| Receiver DELEGATE; assigner/CC DELEGATE | BUSINESS DECISION REQUIRED for role limits and nonreceiver exceptions. |
| Giver/receiver/CC EDIT, reassign, change CC/status, replace attachment/history | BUSINESS DECISION REQUIRED by field; no VIEW-implies-WRITE acceptance. |
| Anonymous/invalid signature VIEW/WRITE/suggested-code | DENY; no DB mutation or data exposure. |
| Missing Task detail/report/remind/forward/existing EDIT | DENY/not-found; no side effects. Intentional CREATE with unused ID is separately authorized. |
| Non-ADMIN CREATE with unused client ID + forged giver | DENY forged identity or canonicalize to session giver as current explicit rule; never create under forged actor. |
| Normal UI CREATE with suggested ID and legitimate giver | ALLOW; test not only blank ID creation. |
| Existing unauthorized ID in save | DENY, never overwrite or convert to create. |
| Forged forward giver / role / company / reporter / body report id | Actor fields cannot grant rights. Body report id must not override path. Forward on-behalf exceptions require business decision. |
| A actor -> B-only Task | DENY, no B reads/writes. Intentional CREATE must not inherit authority from foreign ID. |
| Same ID in A/B | Operate only authorized A row; B row unchanged. Client company/MST cannot change DB. |
| Cross-tenant receiver/CC targets | DENY unknown foreign identities; never resolve another tenant to satisfy target. |
| Attachment READ vs WRITE | Authorized Task READ alone must not permit rebinding another file; no gateway or registry implemented here. |
| DELETE | No endpoint; no hypothetical business delete policy test. |
| Existing login/dashboard/tasks/logout + SEC-03 + collision regressions | Preserve PASS; known mobile 500 baseline separate. DB/data before/after unchanged. |

Focused future scope: routes/tasks.py; services/task_service.py; a new Task policy
module if approved; tests/runtime_sandbox.py and tests/RUNTIME_SANDBOX.md; this
log. templates/tasks/index/report/remind/forward only if capability UI approved.
No model/schema/migration, global Task ID rewrite, session/resolver/mobile changes,
private-file gateway/registry, Drive rename or CRM/QuoteFlow cleanup. BUG-03 route
order and BUG-07 allocation are adjacent findings requiring separate approval.

Validation this audit: connected source/UI analysis and documentation diff review
PASS. New runtime tests NOT RUN; no app import/startup, provider request or new
test fixture. Latest runtime remains 147/149 PASS, two known mobile FAIL; SEC-03
84 PASS and collision 13 PASS remain historical results, not new Batch 3A runs.
SEC-05 OPEN; SEC-04 OPEN; SEC-03 PARTIALLY FIXED; Drive rename BLOCKED; BUG-10
PARTIALLY FIXED. Next step: business-policy approval, then explicitly authorized
small SEC-05 implementation batch with the synthetic regression matrix.

### Batch 3B implementation handoff: written, NOT runtime validated

Recorded 2026-09-30 20:59 +07:00. Original fix/test instruction remained in
context and implementation had already been performed when the user requested
review only. No further code changes or test runs were made after that steering.

Files changed by Batch 3B only:

- routes/tasks.py: replace broad helper with centralized action policy, tenant
  targets, CREATE/EDIT existence classification, history protection, suggested
  code authentication. JSON HTTP 200 + success:false denial contract preserved.
- services/task_service.py: list follows READ, including CC; persistence receives
  loaded authorized objects and explicit create flag; no re-lookup/upsert fallback;
  journals append server actor identity. Generic save cannot replace journals.
- services/task_policy.py (new): actor/session and exact tenant-local employee
  lookup; existing-object checks; centralized capabilities and target validation.
- tests/runtime_sandbox.py: added synthetic USER/MANAGER/CEO relationship matrix,
  ADMIN cases, CREATE/bypass/tenant/denied-write assertions. **Not executed.**
- CODEX_AUDIT_FIX_LOG.md: this evidence/status handoff.
- tests/RUNTIME_SANDBOX.md and Task templates were NOT modified in this batch.

Approved matrix implemented in source (not a measured runtime result):

| Actor | VIEW | EDIT/ASSIGN | DIRECT | REPORT | DELEGATE |
| --- | --- | --- | --- | --- | --- |
| ADMIN role | ALLOW | ALLOW | ALLOW | ALLOW | ALLOW |
| Giver | ALLOW | ALLOW | ALLOW | DENY | DENY |
| Receiver | ALLOW | DENY | DENY | ALLOW | ALLOW |
| CC | ALLOW | DENY | DENY | DENY | DENY |
| Unrelated | DENY | DENY | DENY | DENY | DENY |

Relationships combine when an actor has multiple relationships. MANAGER/CEO
receive no global privilege; role ADMIN is the Task override, not employee ID
alone. Task actor must exist in the current tenant; session expiry/revocation
architecture remains unchanged. LIST filters through the same can_view_task,
so CC and role ADMIN are included. Dashboard/AI/mobile queries remain unchanged.

CREATE: blank/TU DONG/suggested unused ID uses actual tenant DB existence.
Legacy default operation=save preserves existing UI; optional operation=create
rejects existing IDs and operation=edit rejects missing IDs. Non-ADMIN giver
always server canonicalized to session ma, including unused nonempty ID. ADMIN
on-behalf giver/receiver/CC must pass exact tenant employee-code checks. Service
receives the resolved create flag; denied existing EDIT cannot fall through to
CREATE. Client-selected-ID/forged-giver bypass is addressed in source, but its
runtime regression result is **NOT RUN**, not PASS.

EDIT/ASSIGN and Task attachment binding: ADMIN/giver only; local target validation.
Non-ADMIN cannot forge giver in edits. Generic save rejects report/directive
journal fields and file_bao_cao and does not replace histories in persistence.
No schema/ownership registry/private static gate implemented.

DIRECT: ADMIN/giver; existing Task required; server session actor appended to
directive journal. REPORT: ADMIN/receiver; route passes loaded path Task, never
body id; service updates only progress/status/explanation/report attachment and
journal/count, with server reporter identity. Generic-edit fields in report body
cannot mutate giver/title/CC. Runtime field/body-ID tests **NOT RUN**.

DELEGATE: ADMIN/receiver; existing parent required. Receiver becomes child giver
from session. ADMIN on-behalf uses the existing parent-receiver semantics; giver
is derived from parent, not client payload, and must exist in current tenant.
New receiver/CC are validated locally; inherited attachment behavior preserved.
Missing/unresolvable target denies before service mutation. ADMIN exception is
implemented for this source-supported subcase only; runtime test **NOT RUN**.

Cross-tenant targets: exact Employee.ma_nv lookup in current DB only; no global
index/email prefix/other-tenant fallback. Client company/MST/role/actor fields do
not select DB or grant authority. Tenant resolver/session architecture is not
changed (SEC-01/02/06/07 remain). Cross-tenant/same-ID assertions **NOT RUN**.

Denied-write zero-mutation evidence: source returns before mutation service; new
harness checks complete A/B Task row state, uploaded-file content hashes and
Drive stub count on every tested denied write. These assertions **NOT RUN**, so
zero-mutation runtime guarantee is not claimed. Suggested-code now requires a
tenant-local session actor; anonymous/invalid-session assertions **NOT RUN**.
Temporary ID remains navigation only; BUG-03 route order unchanged.

Test execution and regression evidence:

- Batch 3B tested = NO. SEC-05 dedicated matrix PASS/FAIL count unavailable.
- Latest prior completed guarded run remains run-46b82e21daba4fa588e4ce4f07201b2a:
  147 PASS / 2 FAIL, total 149, **historical Batch 2B.1 only**.
- SEC-03 prior 84 PASS; Batch 3B regression NOT RUN.
- BUG-10 collision prior 13 PASS; Batch 3B regression NOT RUN.
- Known /mobile and /mobile/tasks 500 remain historical baseline; not rerun.
- Diff review + git diff --check PASS. No runtime, integration or new syntax-test
  execution is implied by diff review. Production integrity before/after matches.

Git diff: Batch 3B tracked changes routes/tasks.py +74/-70 and task_service.py
+18/-56 (combined +92/-126); new untracked policy and edits inside already
untracked tests/log are outside git diff --stat. Overall tracked tree is 15 files
+190/-269 versus baseline 13 files +98/-143; those earlier changes are not Batch
3B work. Existing mobile/VPS/untracked files preserved; no commit/reset/cleanup.

Remaining risks: current implementation and harness are untested; frontend
capability buttons unchanged and can show actions that backend now denies; LIST
currently filters tenant rows in memory (scale concern); session role revalidation
and global tenant isolation unresolved; existing numeric/concurrent ID bugs
unchanged; trusted attachment ownership absent and SEC-04 OPEN. Strict target
validation can reject legacy noncanonical/missing employee references; compatibility
must be measured in sandbox, not inferred from this source review.

SEC-05 = PARTIALLY FIXED. Next recommended action: separately authorize running
the existing guarded sandbox and reviewing results, without expanding into any
other finding. Current instruction requires stopping after this documentation.

### Batch 3C SEC-05 runtime validation: FAIL / incomplete acceptance

Recorded 2026-09-30 21:07 +07:00. Command executed exactly once:
` .\venv\Scripts\python.exe -B tests/runtime_sandbox.py `.
No production source, tests, fixtures, expected results or configuration modified.
Only this central log updated; generated run artifacts remain in sandbox.

Static: AST syntax PASS for routes/tasks.py, services/task_service.py,
services/task_policy.py, tests/runtime_sandbox.py. Local import target exists;
actual Core imports completed safely inside guarded worker. Diff check PASS.
Guarded preflight PASS; routers auth/tasks/master/companies/documents/personal/ai/
processes/jds/org_chart/mobile all loaded. Test-only startup/seed stayed within
the snapshot's synthetic databases. No production startup/provider action.

Failure evidence:

- Worker traceback: tests/runtime_sandbox.py:492, `created[0][0]` raises
  `IndexError: list index out of range` while recording CREATE canonical giver.
- Read-only source analysis: the loop iterable at lines 484-486 calls
  suggested-code BEFORE executing blank/TU DONG/ASCII automatic creates.
  Those three iterations consume A_USER.001/.002/.003. Suggested ID is stale by
  its turn: it already exists, so default operation=save correctly selects EDIT,
  not creation of a fresh Task. The test assumes one newly created row and indexes
  the empty result. This is a **CONFIRMED test-harness/fixture ordering failure**,
  not evidence that production authorization granted an unauthorized mutation.
- Read-only sandbox DB confirms three synthetic A_USER.001/.002/.003 rows, each
  giver A_USER, receiver A_MANAGER. This corroborates prior canonical creation
  state, but cannot recover the lost per-assertion results or prove every test.
- `record()` accumulates failures without asserting; no runtime_results.json was
  persisted before the uncaught exception. Prior traversed cases cannot be called
  PASS merely because execution reached CREATE. Do not reconstruct counts.

| Acceptance group | Batch 3C result / evidence limit |
| --- | --- |
| VIEW ADMIN/giver/receiver/CC/unrelated | Matrix requests reached before abort; results not persisted, full PASS/FAIL unavailable. |
| LIST giver/receiver/CC/unrelated | Same: no retained assertion results. |
| CREATE blank/TU DONG/ASCII | Three synthetic local rows with canonical A_USER giver found; full assertion counts unavailable. |
| CREATE suggested unused ID | FAIL validation: stale suggested fixture selected existing row; harness IndexError. Fresh unused-ID case not proven. |
| CREATE unused ID + forged giver / ADMIN on behalf / foreign targets | Later cases not reached; NOT RUN in this attempt. |
| EDIT/DIRECT/REPORT/DELEGATE approved role/relationship matrix | Traversed before abort; no persisted results, so not accepted as PASS. |
| Missing object, existing ID overwrite, forged actor/role/company, EDIT denial cannot CREATE, report body ID | Later dedicated bypass cases not reached; NOT RUN. |
| Cross-tenant, same ID A/B, foreign receiver/CC/client tenant spoof | Dedicated later cases not reached; NOT RUN. Earlier baseline visibility traversed but not persisted. |
| Denied-write Task/attachment/provider unchanged | Assertions added and traversed for matrix; no retained results, acceptance NOT PROVEN. |
| Suggested-code anonymous/invalid session; authenticated valid actor | Later auth cases not reached. Authenticated suggestion requested to build loop; fresh-ID behavior not validated. |
| SEC-03 84 regression checks | Traversed before abort; no persisted results, current PASS/FAIL unavailable. Prior 84 PASS remains historical only. |
| BUG-10 13 collision checks | Traversed before abort; no persisted results, current PASS/FAIL unavailable. Prior 13 PASS remains historical only. |
| login/dashboard/tasks/logout | Baseline traversed; no retained assertions; 11 router import preflight PASS independently. |
| /mobile and /mobile/tasks | Located after failing CREATE: NOT RUN this attempt. Historical 500 baseline remains; no new mobile conclusion. |

New failure: harness IndexError / incomplete result reporting. No new production
regression or authorization bypass is demonstrated, but absence of regressions
cannot be established without complete results. SEC-05 targeted and total counts
UNAVAILABLE. Do not mark any full acceptance group PASS from execution order.

Integrity: run integrity before/after equal, production_data_modified=false;
independent SHA-256/size/mtime snapshots equal for all 10 protected files; source
manifest matches current files. PRODUCTION DB MODIFIED=NO; PRODUCTION DATA
MODIFIED=NO. Runner/tests unchanged; no external provider requests or migration.

SEC-05 remains PARTIALLY FIXED. SEC-04 OPEN; SEC-03 PARTIALLY FIXED; Drive rename
BLOCKED; BUG-10 PARTIALLY FIXED. Recommended next action, not performed: explicitly
authorize narrow harness repair (get suggested ID immediately before its create;
preserve partial results on failure without altering authorization expectations),
then rerun guarded validation on a fresh snapshot. No security finding fix,
fixture workaround hiding production behavior, or next batch started here.

### Batch 3D test-harness-only repair and fresh SEC-05 acceptance

Recorded 2026-09-30 21:17 +07:00. Only modified tests/runtime_sandbox.py,
tests/RUNTIME_SANDBOX.md and this log. Production code/fixtures/matrix/expected
authorization results unchanged. No skipped security assertions.

Exact repair:

- Suggested ID fetched inside its case immediately before CREATE, after previous
  creates. Record authenticated response/type and unused-ID check before POST.
- Query suggested/explicit-ID result by that exact ID. Missing rows record FAIL;
  automatic cases index a discovered row only when exactly one row exists.
- Mutation helper tolerates non-JSON/wrong-shape failure responses as failures,
  not success. Missing delegated ID/row records FAIL rather than raising KeyError.
- Every business record persists partial runtime_results.json (complete=false);
  normal completion writes complete=true. Isolation failures still raise.
  No exception or failed authorization is converted into PASS.
- Harness AST parse and diff check PASS; reviewed test-only changes. Existing
  15-file tracked diff (+190/-269) unchanged; untracked tests/log documentation
  contain this batch's changes. Core fingerprint comparison confirms no source
  edits; existing mobile/VPS/user changes retained.

Command executed once on fresh snapshot:
`.\venv\Scripts\python.exe -B tests/runtime_sandbox.py`.
Run `.test_runtime/run-601a577af1c54f719542bfde7f8da525/` contains complete
runtime_results.json, integrity.json, preflight.json and source_manifest.json.
Exit 0 is not acceptance evidence by itself: all report assertions reviewed.

| Acceptance | Current result |
| --- | --- |
| VIEW ADMIN/giver/receiver/CC/unrelated | PASS: allow ADMIN and related giver/receiver/CC; deny unrelated. |
| LIST ADMIN/giver/receiver/CC/unrelated | PASS: same READ policy, including CC and ADMIN role. |
| CREATE blank/TU DONG/ASCII automatic | PASS: one new row, canonical giver=session actor. |
| CREATE fresh suggested unused ID | PASS: authenticated code, ID absent before POST, exact ID row exists afterwards, canonical giver. |
| CREATE explicit unused ID + forged giver | PASS: new row with session actor, not supplied foreign giver. |
| ADMIN on-behalf, tenant targets | PASS: local giver allowed; foreign giver/receiver/CC denied. |
| operation=create existing ID / operation=edit missing ID | PASS: denied without mutation; unknown intent denied. |
| EDIT ADMIN/giver/receiver/CC/unrelated | PASS: allow ADMIN/giver only; attachment binding follows EDIT. |
| DIRECT ADMIN/giver/receiver/CC/unrelated | PASS: allow ADMIN/giver only; server director identity recorded. |
| REPORT ADMIN/receiver/giver/CC/unrelated | PASS: allow ADMIN/receiver only; server reporter identity; report attachment allowed; giver/title edits not accepted via REPORT. |
| DELEGATE ADMIN/receiver/giver/CC/unrelated | PASS: allow ADMIN/receiver only; forged giver ignored, canonical child giver=parent receiver (ADMIN on behalf) or authenticated receiver; inherited attachment preserved. |
| MANAGER and CEO | PASS as giver/receiver/CC/unrelated; no automatic global privilege. |
| Missing Task / unauthorized existing ID / denied EDIT cannot CREATE | PASS: absence/unauthorized object cannot grant existing action; complete A/B state unchanged. |
| Forged actor/role/company/MST | PASS: forged fields cannot grant permissions or select other DB. |
| Report body ID vs path | PASS: only route's authorized Task changed; body-target row unchanged. |
| A -> B-only Task | PASS: denied existing action; foreign target employee codes rejected. |
| Same ID in A/B | PASS: only authorized A row updated; B unchanged despite client tenant/path fields. |
| Foreign receiver/CC in CREATE/EDIT/DELEGATE | PASS: exact current-tenant lookup, denied before mutation. |
| Denied-write zero mutation | PASS: 67 DB-state checks cover all A/B Task fields, 67 upload byte-hash checks, 67 provider-count checks; all pass. |
| Suggested-code auth | PASS: anonymous/invalid signature denied; authenticated local actor returns fresh usable code. |

Group counts by test-name filter (overlap; do not sum these): VIEW 14/14,
LIST 13/13, CREATE 64/64, EDIT 86/86, DIRECT 68/68, REPORT 79/79,
DELEGATE 80/80, suggested 10/10, foreign 78/78, missing 25/25.
Unique SEC-05 checks: **530 PASS / 0 FAIL**.

Regressions: SEC-03 **84 PASS / 0 FAIL**; collision **13 PASS / 0 FAIL**.
Existing login/dashboard/tasks/logout PASS. All 11 Core routers loaded; no guard
violations. Provider mutation count=0. Total **677 PASS / 2 FAIL**, 679 checks.
Failures only `mobile dashboard baseline` and `mobile tasks baseline`: current
actual500/expected200, reproducing the two known failures. No new regression.
No mobile/PWA changes or expectation changes made to hide these failures.

Integrity: independent pre/post SHA-256/size/mtime snapshots match all 10 protected
files; new integrity before==after, production_data_modified=false. Production
source snapshot manifest matches current code; Core source/asset fingerprints
unchanged across repair/run. PRODUCTION DB MODIFIED=NO; PRODUCTION DATA
MODIFIED=NO. Production app never started; test initialization occurred only in
synthetic snapshot; no external provider request, production migration or seed.

SEC-05 = FIXED for the approved action matrix, CREATE identity/bypass, tenant-local
target validation and denied-write acceptance. This does not resolve global
session/tenant selection risks SEC-01/02/06/07 or claim trusted ownership of
submitted file URLs. SEC-04 stays OPEN; SEC-03 PARTIALLY FIXED with rename BLOCKED;
BUG-10 PARTIALLY FIXED due numeric validation. Dashboard/AI/mobile policy drift,
legacy missing employee target compatibility and list-in-memory scaling remain.
Next recommended action: separately authorize SEC-04 design/implementation scope
decisions, reusing can_view_task only alongside trusted file ownership; no further
batch or registry/gateway implemented now.

### Batch 4A SEC-04 final architecture and implementation-scope audit

Recorded 2026-09-30 21:30 +07:00. Labels below distinguish CONFIRMED FROM SOURCE
(C), DESIGN DECISION / recommendation (D), and BLOCKED / NEEDS USER DECISION (U).
No runtime/DB query; no inference of real-file ownership from filenames/URLs.

#### Static exposure and deployment (C)

- app.py:58-66 creates/mounts /static/uploads before parent /static. Normal run
  parent directory is static; packaged run parent is _MEIPASS/static. Routers
  registered afterwards at 76-86. Removing dedicated mount alone leaves uploads
  accessible through parent static in normal layout. Packaged storage differs;
  must test both roots rather than assume upload root equals asset root.
- Installed Starlette routing.py:675-681 dispatches first FULL match; a route
  added after the mount is not reached. staticfiles.py:109-185 serves GET/HEAD,
  resolves physical path, emits FileResponse and may return 304 without QLCV ACL.
  Filesystem traversal protections there do not provide authentication.
- app.py:141-150 already returns real JSON 404 for /api/ and /static/; other
  unmatched HTML paths redirect dashboard. Gateway should return its own responses
  and never rely on global exception behavior or redirect authentication failures.
- nginx_vps_default.conf and vps_default.conf have proxy_pass only, no root/alias/
  try_files/static filesystem serving. /qlcv/ strips prefix and proxies same app.
  Reviewed deploy_vps.sh/run_vps.bat/chay_app.bat run FastAPI on 8081; deploy uses
  two workers and opens direct backend port. Direct backend reaches same gateway,
  so Nginx-only protection is insufficient. Actual production Nginx/CDN/other
  webservers NOT VERIFIED. No reload/deploy/firewall commands executed.
- app.py:71-73 optional /local_docs mount is another public filesystem root.
  If it overlaps/aliases uploads it bypasses a URL-only gateway; configuration
  value not read from secret env. Overlap is U, not asserted to exist. Filter its
  private-file resolved paths or prohibit overlap before acceptance; protection
  of unrelated /local_docs documents is separate scope decision.

#### Active consumer/model inventory (C unless stated)

| Consumer | Flow / evidence | Classification |
| --- | --- | --- |
| Local upload | routes/documents.py upload-local -> DriveService UUID exclusive write into Config.UPLOAD_DIR -> /static/uploads/name, original name returned | ACTIVE; no persistent provenance |
| Task assignment | Task.file_giao_viec -> TaskService DTO link -> index.html upload:564/save:511/open:595 | ACTIVE; DB editable URL; local open currently wrongly prepends https:// to relative URL |
| Task report | Task.file_bao_cao -> detail DTO; report.html upload:254 -> linkBaoCao -> update_bao_cao | ACTIVE writer; no separate report/file entity, dedicated old report-file link consumer not found |
| Forward | save_forward inherits parent file_giao_viec into child; forward.html uploads local file at297 and sends link, but service ignores that link | ACTIVE inherited reader/binding; independently uploaded forward file may remain orphan |
| Directive | remind.html loads Task and posts message; update_nhac_nho no attachment write | ACTIVE Task action; no separate directive file feature |
| Task list/detail | service returns assignment URL, detail also report URL; report-center/overdue use Task list | ACTIVE DTO consumers; not independent file ACL |
| Document CRUD | documents.link_file -> DocumentService client linkFile -> management page open link at249; upload-local:364 | ACTIVE editable URL, no uploader identity |
| Repository preview | documents library builds previewUrl; repository.html:245 fetches DOCX, :268 iframe for PDF/images/other; external Drive preview URLs preserved | ACTIVE; local URL stays relative, same-origin cookie can protect fetch/iframe |
| Personal | personal_tasks.file_dinh_kem; PersonalService.create_task/update_task writes it, but active routes create/update whitelist omits it; tasks/personal.html no attachment UI found | LEGACY/unused attachment mutator, ACTIVE model serialization may return old field; no new feature proposed |
| AI | AIService reads Task objects for textual answers/prompts; no local upload/file-byte download path found in active AI routes/service | No active attachment reader found; future arbitrary Markdown links UNCERTAIN, gateway must protect any URL |
| Mobile | active mobile templates no local attachment open/upload found; broken Task pages remain known baseline | No active file UI found; do not add feature or fix mobile |
| PWA | sw.js caches any GET200 URL containing /static/; offline caches.match then /mobile fallback | ACTIVE bypass via cached uploads |
| Excel seed | sheet_service imports Task file fields and document links at139/174-175 | LEGACY/source-import references, not trusted ownership; startup untouched |

Search covered active routes/services/models/templates/static/config/app for all
six requested fields and upload paths, excluding disabled CRM/QuoteFlow internals.
No Core local rename/delete/download endpoint or ownership table found. Some
external Drive link consumers are ACTIVE but outside local-file ownership scope.
Current existence of arbitrary original URL records is not queried or assumed.

#### Ownership and classification (C)

CAN EXISTING SQL SCHEMA PROVE PHYSICAL FILE OWNERSHIP = NO. Task stores giver,
receiver, CC and editable file URL; Document stores editable link/dept/update date;
PersonalTask stores owner and editable/legacy attachment string. DB tenant is
object provenance, not file provenance. No physical-file ID, file tenant, uploader,
upload timestamp, persistent original filename/hash, attachment table or trusted
binding exists. Document update date/AuditLog event is not upload provenance.
UUID/collision-safe filename proves uniqueness, not tenant ownership. A matching
SQL URL (even in several objects) is only a candidate reference.

No legitimate PUBLIC upload category found in active source; therefore recommend
new QLCV local uploads PRIVATE (D), existing files UNKNOWN until verified (D/U).
Public CSS/JS/images/manifest/sw outside uploads remain public. Do not infer
PUBLIC from current static exposure. Any claimed public upload exception needs U.

#### Registry options and recommended ONE design (D/U)

| Option | Strength / limitation |
| --- | --- |
| Single JSON registry | Atomic temp+fsync+replace protects individual replacement, but cross-process locking, lost updates, full-file writes and corruption recovery are custom; poor default for two workers. |
| SQLite sidecar | Recommended: ACID transactions, unique constraints, multiworker process locking, bounded busy timeout and local-disk durability; new persistent state, not business SQL DB migration. |
| Per-file metadata | Smaller corruption radius and atomic per-record replacement; multi-file binding/rebind transactions and reconciliation/locking still custom; harder multiworker consistency. |

Recommended location (not created): project/private_metadata/file_registry.sqlite3,
outside static and LOCAL_DOCS roots, app-user-only permissions, explicitly configured
absolute path, same confined path in every worker; test path only in sandbox.
Create sidecar tables/indexes only with explicit USER approval: this is a NEW DB
and persistent-state schema, despite no ALTER/migration of existing business DBs.
Single host/local disk assumption must be verified; SQLite WAL/shared state is
not recommended on NFS or across hosts without a separate design.

Record: opaque UUID file_id; authenticated tenant_id/uploader_id; server storage_name
and trusted storage-root ID; sanitized original_name; created_at; size/sha256;
PRIVATE/UNKNOWN/verified classification; WRITING/UNBOUND/BOUND/REVOKED state,
expires_at/version. Bindings: file_id, tenant, object kind/id, field slot, generation,
PENDING/ACTIVE/REVOKED, timestamps. Unique storage locator and unique active
file/object/slot binding; physical filename/tenant values never supplied as authority.

Atomicity: short BEGIN IMMEDIATE registry transactions, unique constraints,
busy timeout/retry bounded, one connection/session per worker/thread, synchronous
durability; WAL on verified local disk. Timeout/corrupt/unavailable registry denies
access, never static fallback/auto-empty reset. Check schema version at startup;
do not destructive rebuild. Registry transactions cannot atomically commit with
tenant DB: use PENDING intent before authorized object save, activate only after
business commit and exact live field/object revalidation. Crash leaves PENDING
unservable until explicit reconciliation; rollback intent if business save fails.
Object save success but activation failure must surface pending/access failure,
never expose bytes. Rebind prepare/activate and revoke previous binding; gateway
checks both ACTIVE binding AND current object field. No implicit auto-claim.

Duplicate same binding is idempotent; stale field/object means deny immediately.
Delete/unbind hooks revoke bindings without deleting physical bytes. ID reuse and
imports require binding-generation handling and explicit reconciliation; an old
object ID alone cannot resurrect access. Orphans/abandoned writes remain denied.
Back up sidecar transactionally plus bytes and tenant DBs at coordinated recovery
points (SQLite backup API or checkpoint-aware backup, not naive live main-file copy).
Recover ambiguous backup/crash combinations as PENDING/UNKNOWN, verify before read.
Never auto-delete bytes or cleanup legacy data. Registry source-of-truth rollback
retains state/backups and keeps gateway denial; restoring public mount is unsafe.

#### Legacy policy options / approval (D/U)

| Policy | Security / compatibility | Recommendation |
| --- | --- | --- |
| A UNKNOWN denied for everyone including ADMIN | Strongest; old URLs remain but unverified bytes unavailable | Recommended, requires USER approval and acknowledgement of blocked legacy preview/download |
| B Tenant ADMIN reads if their DB references URL | Guess/copied URL can masquerade as ownership; cross-tenant exposure remains | Reject; URL alone cannot justify exception |
| C First matching reference auto-claims | Race/order poisoning and conflicting references create false ownership | Reject |
| D Evidence-verified manual/tool-assisted mapping | Candidate DB references plus independent uploader/storage/backup provenance, review conflict/hash before activation | Recommended controlled complement to A; approval required |

Hash verifies bytes, not tenant ownership. Tenant ADMIN cannot bootstrap access to
UNKNOWN solely from current DB URL. No HTTP escape hatch for unknown legacy bytes.
Verification tool must run by an explicitly authorized custodian, dry-run/review
first, and write only approved registry mappings; never rewrite/move business data.
Unknown/orphan/conflicting files remain denied. Mapping evidence availability U.

#### Upload -> binding -> read lifecycle (D/U)

Validate signed session AND exact tenant-local actor -> extension/size validation
preserved -> collision-safe exclusive UUID physical create -> compute size/hash
and trusted record -> mark UNBOUND only after bytes/metadata durable -> return
same url/name contract plus optional opaque file_id (no DB URL rewrite).
If bytes exist but metadata write fails: return failure, orphan/WRITING inaccessible;
no fallback public read, no automatic deletion of preserved data. Missing metadata
never qualifies as owned upload. Metadata state before byte creation may record
WRITING intent for crash recovery; only complete records can become readable.

UNBOUND recommended uploader-only same tenant, with bounded expiry (24h proposed,
duration U); ADMIN has no implicit unbound-read override. Bind to authorized
Task/Document only from same-tenant owned unbound upload or approved existing
binding/share; possession of URL/file_id never enough. Other user/ADMIN binding
of another uploader's unbound file requires explicit share policy, default deny.
Expired unbound denied; no automatic physical cleanup. Failed Task create keeps
UNBOUND until expiry/retry; abandoned/unknown bytes retained. Duplicate binding
idempotent; pending/crash states deny. Do not revive an expired unbound by guessing.

Task: reuse SEC-05 can_edit_task/can_bind_task_attachment for file_giao_viec;
can_report_task for file_bao_cao. READ can_view_task plus trusted tenant/binding
AND exact current field. Forward authorized can_delegate_task copies vetted
parent binding to child's assignment slot within same tenant. Parent and child
share one physical blob with separate bindings; either current authorized object
READ may permit download (union-of-valid-bindings). Removing one reference does
not destroy other's access. Same-tenant fan-out grants intended child readers;
cross-tenant sharing prohibited. Explicit USER approval required for shared
semantics; do not support forward's ignored independent link as new feature.

Document (C/D): existing routes/documents.py permits ADMIN/CEO CRUD. Library READ
permits ADMIN/CEO all, general dept None/empty/Tat ca all authenticated users,
USER own dept, MANAGER own plus direct subordinates' departments (Employee.nguoi_ql,
not recursive). CEO receives no raw linkFile in library but still previewUrl.
Proposed centralized can_view_document exactly mirrors library selection;
can_bind_document_file mirrors ADMIN/CEO CRUD, with trusted file mapping and
exact tenant targets. No broader department/admin privilege introduced. Missing
tenant actor/object denies gateway; factor shared predicate rather than divergent
copy. Editable link_file alone never proves ownership.

Personal (C/D): attachment write UI/active route absent; do not create a new
upload/binding feature. Preserve/classify old fields UNKNOWN. Verified legacy
PersonalTask binding could use tenant-local user_id == session ma, no global
ADMIN/department override; optional future adapter only if verified mappings need
it. Generic active PersonalTask serialization is not an attachment capability.

#### Gateway / static ordering / HTTP (D)

Required order: mount authenticated private-upload gateway FIRST at
/static/uploads (whole subtree; GET/HEAD only, other methods deny), replacing
dedicated public mount; mount filtered public /static SECOND; Core routers and
manifest/sw remain available. Alternative router must be included BEFORE static
mounts and handle GET/HEAD, but whole-subtree mount reduces fall-through risk.
Public StaticFiles wrapper must reject every canonical/resolved upload path,
not just textual prefix; deny symlink/junction aliases into private roots or known
private locators. Filter/prohibit overlapping /local_docs root as applicable.
Router after mount will not work. Parent exclusion essential even with gateway.
Preserve CSS/JS/images with explicit private exclusion; do not remove all static.

Request -> authenticate (before metadata/existence/conditional responses) -> reject
malformed/alias path -> opaque-ID or exact registered storage_name lookup ->
tenant match -> ready state/unexpired uploader-only unbound OR active bindings ->
live tenant object+current field+READ policy -> confined physical locator -> file
response. Return endpoint-owned JSON errors: unauthenticated/invalid 401;
unknown/foreign/unreadable/missing object or bytes 404 (avoid existence disclosure);
invalid path generic400/404; unsupported method405. No stack/internal path,
dashboard redirect, metadata update, reconciliation or provider action on GET.
Legacy exact /static/uploads/name stays; optional /api/files/{id} deferred.

Path guard: one registered basename, no arbitrary path; reject separators,
dot segments, residual/double percent encoding, NUL/control, mixed slash,
Windows drive/UNC/absolute paths/case aliases. Honor legitimate validated extension
case from registry, do not invent lowercase rename. Compare canonical realpath
under trusted configured root and exact locator; reject symlink/reparse/junction
escape. Prevent race by trusted storage permissions and safe/no-follow open
where supported, verify file handle/stat; FileResponse delayed reopen TOCTOU
requires explicit handling/testing. Public alias resolution obeys same exclusion.
Config.UPLOAD_DIR may differ from static root; root selection/legacy roots need
explicit safe configuration, never fallback to arbitrary client path.

Authorize BEFORE stat, HEAD metadata, GET/Range206, If-Range, ETag/Last-Modified,
If-None-Match/If-Modified-Since304. Unauthorized conditional/HEAD requests return
same denial, no validators/length/filename. Installed FileResponse supports HEAD/
Range; StaticFiles adds conditional304. Recommendation first gateway does not
return304 (ignore conditional cache reuse, authorized full200/range206), sets
Cache-Control private,no-store and Vary:Cookie on success/errors. If conditional
304 added later, authorization first mandatory. Invalid Range416 only after auth.
Inline only approved PDF/image/text/document types; attachment for other types;
Content-Type trusted server allowlist, nosniff, safe RFC filename/filename* from
sanitized original name, no CRLF/header path. DOCX fetch preserved; no inline
active HTML/SVG/script based solely on extension. Download flag changes disposition
only, not ACL; local URL same origin keeps fetch/iframe session.

#### PWA and compatibility (C/D)

static/sw.js caches GET200 whenever URL contains /static/ (line36 onwards), even
uploads; fallback caches.match then /mobile. Activate deletes caches with other
names; current v1 cache persists. No logout cache purge hook found. Cache-Control
no-store ALONE is NOT sufficient: explicit Cache API cache.put ignores that intent.
Minimal narrow change (future): classify same-origin private paths before normal
handler; network-only with request cache:no-store, never cache.put/cache.match,
offline private access explicit denial, never /mobile fallback. Version bump plus
activation removal of known app caches/old private entries; do not indiscriminately
delete unrelated origins/apps. Cover normalized/encoded legacy paths and optional
new API path. Existing-worker transition needs activation/claim and browser tests;
previously copied/downloaded bytes cannot be revoked by server. Narrow USER-approved
purge of cached authenticated /mobile shell may be needed if it contains private
data; do not redesign mobile/PWA business flow in private-file batch.

Compatibility: existing DB URL strings and physical files unchanged; verified
old exact URLs resolve via protected gateway. UNKNOWN will stop working until
verified: zero URL rewrite does not promise zero disruption. Document DOCX/PDF/
image preview can retain consumers. Task index open:595-596 needs narrow relative
local URL adapter (currently prepends https://); required for working local open,
not generic UI redesign. Report/forward consumers need no broad rewrite; forward
fresh upload behavior is not repaired here. External URLs/Drive and /local_docs
outside mapped uploads retain separate ownership/security limitations.

#### Future test matrix and implementation slices (D/U)

Required sandbox tests: anonymous/invalid signed session; authenticated tenant
actor; Task ADMIN/giver/receiver/CC/unrelated READ and bind action; Document
ADMIN/CEO/general/own dept/MANAGER direct subordinate/foreign dept; A/B file and
same basename/forged tenant; verified/UNKNOWN/orphan/conflicting legacy; raw/encoded/
double-encoded traversal, Windows mixed slash/case/drive/UNC/NUL/symlink/junction/
realpath race; GET/HEAD/Range206/416/conditional304-or-authorized200/inline/download;
PWA online/offline/logout/old cache/worker transition; new/unbound/expired/pending/
bind/rebind/denied bind/deleted object/reused ID/shared child; crashes, corruption,
registry unavailable, multiworker contention and recovery; all denied requests
zero DB/file/registry/provider mutation. Browser tests needed for Cache API.
Regressions: current SEC-05 530, SEC-03 84, collision13; login/dashboard/tasks/
logout/11routers; reproduce known two mobile500 separately. Before/after integrity
DB/data/source; no production provider, migrations, startup or fixture secrets.

| Slice | REQUIRED expected files | Objective / acceptance / dependency / rollback |
| --- | --- | --- |
| 4B1 metadata foundation | new services/file_registry.py; config.py path override only; tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; log | Approved sidecar design only, multiworker/crash/corruption/confined tests; new state preserved on rollback. No security closure while static public. |
| 4B2 upload + binding integration | routes/documents.py; services/drive_service.py; routes/tasks.py; services/task_service.py; services/document_service.py; new services/document_policy.py and services/file_access_service.py; tests/docs/log | Trusted metadata/register upload and authorized pending/active bindings including forward/delete/rebind; no SQL migration; approved UNBOUND/share policies. Registry failure denies writes/reads. Keep DB/bytes/state intact on rollback. |
| 4B3 gateway + static exclusion | app.py; new routes/files.py; new services/private_static.py; file_access_service.py; templates/tasks/index.html narrow relative link adapter; tests/docs/log | Auth before bytes/metadata, parent/static and overlap alias exclusion, exact legacy URLs/public assets preserved; depends vetted bindings and UNKNOWN approval. Rollback to maintenance-deny, never restore public serving. |
| 4B4 narrow cache protection | static/sw.js; tests/docs/log | No private cache/fallback; version+approved old cache purge, browser logout/offline acceptance. Must be bundled operationally with gateway activation for full SEC-04 claim; old workers need transition. |
| 4B5 verified legacy onboarding | proposed tools/verify_legacy_files.py; registry/access helpers only if approved; tests/docs/log | Read-only candidate inventory plus reviewed evidence mapping; UNKNOWN/conflicts stay denied; no DB URL rewrite/file move. Revoke mappings to roll back; preserve data. |

OPTIONAL: PersonalTask adapter in file_access_service only for approved verified
legacy references; /api/files logical route; preview UX for denied legacy files;
Nginx template changes only if actual bypass found; isolated browser test artifact
if authorized. Exact names above are proposed, not created.
DO NOT TOUCH: business models/database schema, session/resolver SEC-01/02/06/07,
mobile BUG-01/02, allocation BUG-07/temp-ID BUG-03, Drive rename, CRM/QuoteFlow,
uploads/exports/backups/secrets and production databases. No general UI redesign.
Intermediate metadata/binding batches leave SEC-04 OPEN. Gateway activation and
cache exclusion need coordinated release; slices are not permission to expose
new files during staging or call incomplete phases FIXED.

#### USER decisions required before implementation (U)

| Decision | Options | Security / compatibility impact | Recommendation |
| --- | --- | --- | --- |
| Registry/location | JSON / SQLite sidecar / per-file | New persistent state, durable backup, multiworker safety; outside static/local_docs mandatory | Approve local-disk private_metadata/file_registry.sqlite3 and explicit test override; no business SQL migration |
| UNKNOWN legacy | A deny all / B admin URL reference / C auto-claim / D vetted mapping | B/C unsafe; A breaks old unverified downloads | A + evidence-reviewed D; ADMIN also denied UNKNOWN |
| UNBOUND read | uploader / tenant ADMIN / nobody | Preview-before-save vs cross-user disclosure | Uploader-only same tenant, proposed24h expiry; approve duration, no cleanup |
| Shared parent/child | per-binding union / require parent ACL / copy bytes | Union intentionally expands same-tenant child READ; no physical move | Separate vetted bindings, union of valid authorized objects; explicit approval |
| PWA invalidation | private entries / all known app cache versions | Previously cached private bytes can outlive logout; shell caching may matter | Network-only uploads, version bump and approved known-app purge; browser verify transition |
| Legacy URL exactness | retain exact / rewrite API references | Preserve DB/UI links vs migration | Exact /static/uploads/name via gateway; optional opaque API deferred |
| Verified legacy mapping | manual / admin-assisted / tool-assisted | URL-only proof forbidden; need independent evidence, conflicts review | Custodian-reviewed tool dry-run plus approved mapping; no automatic claim |
| Deployment/storage assumptions | local disk vs multi-host; LOCAL_DOCS overlap/actual Nginx | Alternate file server/root can bypass gateway | Verify actual topology; reject overlap or filter; do not claim live deployment verified |

SQL MIGRATION REQUIRED=NO for existing business DBs; NEW sidecar DB/schema/state
requires explicit approval. PHYSICAL FILE MIGRATION REQUIRED=NO. Recommended
architecture C legacy gateway + A retained storage + trusted sidecar/binding.
All registry/HTTP/ACL/cache choices above are design recommendations, not existing
source behavior or implementation. Decisions/legacy provenance/deployment topology
are blockers, not new facts asserted about production.

Integrity audit: independent before/after fingerprints match all protected data
(SHA-256,size,mtime) and selected Core source/assets. PRODUCTION DB MODIFIED=NO;
PRODUCTION DATA MODIFIED=NO; PRODUCTION SOURCE MODIFIED=NO. Only this log updated.
No runtime/tests executed this batch; Batch3D 530/0 and677/2 remain historical
current-source acceptance, not a new Batch4A run. SEC-04 OPEN; other statuses
unchanged. Next: USER selects registry/UNKNOWN/UNBOUND/share/cache/verification
policies and authorizes a specific small implementation slice; STOP now.

### Batch 4B1 SEC-04 Metadata Foundation

Recorded 2026-09-30 22:33 +07:00. USER-approved architecture implemented ONLY as
metadata foundation. SEC-04 remains OPEN. No source/data activation via app startup,
upload/Task/Document handlers/static/PWA; no legacy scan or auto-registration.

Files:
- NEW services/file_registry.py: metadata-only service, controlled RegistryError,
  lazy constructor, explicit initialize_registry; no business ACL/HTTP/byte writes.
- config.py: pathlib import and FILE_REGISTRY_ROOT/PATH absolute resolved settings
  only (six added lines); existing port8081 change predates this batch.
- tests/runtime_sandbox.py: sandbox config override, explicit synthetic sidecars,
  targeted lifecycle/path/transaction/failure/concurrency checks; two guarded
  metadata-only subprocesses orchestrated from parent. No extra helper file.
- tests/RUNTIME_SANDBOX.md and this log: lifecycle/testing/handoff documentation.
No modifications to app/routes/other services/models/database/templates/static/
deployment/mobile source. Preexisting user/mobile/VPS/PhaseA/3B changes preserved.

Configuration: default <project>/private_metadata/file_registry.sqlite3. Root/path
resolve absolute; service validates parent confinement before initialization and
each operation, rejects public static, UPLOAD_DIR and configured LOCAL_DOCS paths.
Runner overrides both variables into each fresh run/private_metadata directory.
Import and constructor leave sidecar absent; only explicit initialize creates it.
Production registry created=NO (checked before/after). Config retains existing
upload-directory behavior; it adds no sidecar creation on import.

Schema v1: PRAGMA user_version=1. files includes opaque UUID, tenant/uploader,
logical storage root/name, original display name, created timestamp, size/hash,
classification, state, expiry/version. classifications PRIVATE/UNKNOWN/
VERIFIED_LEGACY; states WRITING/UNBOUND/BOUND/REVOKED constrained.
bindings includes binding UUID, tenant/file, object kind/id/field slot/generation,
state/timestamps; PENDING/ACTIVE/REVOKED constrained. Composite FK(file_id,tenant)
prevents tenant mismatch. Storage root/name UNIQUE; composite file/tenant UNIQUE.
Partial unique index enforces one live PENDING/ACTIVE binding per tenant/object/
slot; exact same file+generation repeat returns same binding. Tenant/state and
file/binding indexes support lookup. Shared blob may have several distinct vetted
object slots; registry itself does not grant authorization.

Connection per operation, foreign_keys ON, bounded busy timeout(default300ms,
allowed1..5000ms); short BEGIN IMMEDIATE writes, SQLite constraints/locks authoritative
across threads/processes, rollback on failure. Default rollback journal; WAL only
explicit opt-in with verified_local_disk=True, exercised on sandbox local disk.
Caller/deployment must verify local storage; this flag is not network-filesystem
detection. Schema version/column validation rejects unknown/newer versions.
Existing corrupt/empty/unavailable files fail closed, not reset/deleted/recreated.
Initialization failures leave inaccessible state rather than recovery by deletion.

Primitives: register_writing, complete_unbound, get_file/storage lookup,
create_pending_binding, activate_binding, revoke_binding, list_active_bindings,
mark_revoked. Completion computes expiry24h metadata; expired_unbound identifiable.
UNKNOWN/WRITING/REVOKED or expiredUNBOUND cannot bind/activate. Reads scoped by
tenant; UNKNOWN read metadata is not HTTP byte permission. Gateway must enforce
approved deny-all UNKNOWN and uploader-only UNBOUND, not rely on registry alone.
Storage basename rejects empty/path separators/absolute drive/UNC/traversal/NUL;
UUID/hash/identity/state/generation validation. Display original name never locator.

Atomicity: sidecar transaction rollback tested; not atomic with business DB.
4B2 MUST write PENDING intent, perform authorized tenant-object business commit,
then exact current-object/field revalidation and activate. No gateway or business
object revalidation exists here. Stale live object fields, unbind/rebind/delete and
crash reconciliation remain integration responsibilities, never inferred from URL.

Tests/read reports:
- First run run-9cfa27371b504e00bdc17c473177dc0f: registry72/0, total749/2.
- Expanded tests for actual two workers, then reran fresh snapshot ONCE:
  run-c00b7009fb654fb9ae233e7670be6da5: registry77/0, total754/2.
- Lifecycle, tenant mismatch, path/UUID/hash/classification, duplicate storage,
  idempotent binding/conflict/generation, PENDING/ACTIVE/revoke, expiredUNBOUND/
  PENDING, UNKNOWN/missing activation denial and rollback PASS.
- Concurrency14/0: independent thread connections distinct registrations/no lost
  rows, same locator one winner, same binding one ID, conflict one ACTIVE slot,
  integrity readability, bounded busy failure; two independent guarded processes
  (not merely threads) distinct registrations, locator race, idempotent ACTIVE
  binding, conflicting slot and readable database PASS. No in-memory lock boundary.
- Fail-closed13/0 subset: public/outside/LOCAL_DOCS path, WAL without local assertion,
  corrupt and empty files preserved, newer schema rejected, missing sidecar,
  busy timeout controlled; read-only connection failure injected (real elevated
  Windows ACL behavior not claimed tested). Missing-parent explicit init PASS.
- SEC-05 530/0, SEC-03 84/0, collision13/0 CURRENT regressions PASS;
  login/dashboard/tasks/logout and11routers PASS; no provider mutation, guard
  violations none. Current mobile dashboard/tasks each500 reproduce known baseline.
- No new regression. Total754 PASS/2 FAIL; runtime_results complete=true. Independent
  process checks appended by parent after children finish; integrity verified after
  all workers. Do not use exitcode alone as pass evidence.

Integrity: protected production DB/data SHA-256/size/mtime unchanged, both independent
snapshot and new integrity report. Production registry absent. Core source snapshot
matches current files; comparison to tested Batch3D old manifest shows ONLY config.py
changed among existing Core modules. New registry is approved additional source.
PRODUCTION DB MODIFIED=NO; PRODUCTION DATA MODIFIED=NO; PRODUCTION REGISTRY CREATED=NO.
No production app, seed/migration, provider call, file deletion or package install.

Diff: existing tracked15files +190/-269 before this batch; now same15files
+196/-269 due six config additions. New untracked registry/test/doc/log changes
are not counted by git diff --stat. Diff/check/status reviewed; no commit/reset/
cleanup. No unrelated source changes attributed to Batch4B1.

Remaining limits: no registry backup/recovery tooling, physical byte/hash verification,
binding integration/reconciliation, gateway/static exclusion, legacy verification,
or PWA protection. Private root OS permissions/local-disk topology must be verified
at deployment. Existing registry initialization concurrency can fail closed while
another initializer is in progress; initialization should precede worker serving,
not retry by resetting state. These are not falsely claimed implemented features.
SEC-04 OPEN; SEC-05 FIXED; SEC-03/BUG-10 PARTIALLY FIXED; Drive rename BLOCKED.
Next recommended slice: separately authorize4B2 trusted upload provenance and
object binding lifecycle. STOP; no4B2/gateway/PWA or other finding performed.

### Batch 4B2 pre-implementation audit / scope stop

Recorded 2026-10-01 04:53 +07:00. Status BLOCKED; Batch4B2 COMPLETE=NO.
User section C explicitly says stop before adding a new production file. This
entry records the proposed reviewable scope, not permission to implement it.
Only CODEX_AUDIT_FIX_LOG.md changed. No source/test/registry/physical byte changes.

Current source evidence:

- routes/documents.py:172-194 file session uses signed ma/company_mst; upload
  route currently has no tenant DB actor validation. DriveService allocates UUID
  then opens exclusive physical file and writes bytes before returning URL.
  Current upload creates no metadata; WRITING before write must be integrated.
- Task assignment route:199 calls save_task_data after approved SEC-05 checks;
  service commits create/update at147/164. Generated blank-ID Task identity is
  finalized inside service, so exact binding target must be resolved there or
  returned explicitly. Client ID alone cannot identify the successfully saved row.
- Report route:224 passes loaded path Task to update_bao_cao; service commits193.
  file_bao_cao remains distinct from assignment. Body ID must remain ignored.
- Document routes:58/67 call DocumentService.add/update_document. That service
  commits internally at98/120, returns message strings, and is NOT in allowed
  modification scope. Integration can wrap callbacks at authorized routes and
  explicitly reload known document ID, without changing DocumentService itself.
- Forward route:252 calls save_forward; child ID allocated in service, inherits
  parent file_giao_viec, then commits244. Vetted inherited child binding needs
  returned/loaded exact child after commit. Client independent forward link is
  ignored; no new attachment feature proposed.
- FileRegistry metadata layer deliberately has no business ACL or HTTP/object
  mutation logic. It supports tenant/file/state validation and schema v1.
- file_registry.py:120 binding_slot_live unique index covers BOTH PENDING and
  ACTIVE for tenant/object/field. create_pending_binding:175-187 rejects a
  different file in the same live slot. Thus current primitive cannot stage a
  replacement PENDING while retaining old ACTIVE until confirmed business commit.
  Prematurely revoking old ACTIVE violates user section J and is not proposed.
- Canonical /static/uploads URL parser is not present. Current DB fields accept
  client references, while registry cannot infer object/provenance from those
  strings. Existing external/local_docs compatibility must remain separate.

Proposed additional production file (not created):
services/file_binding_service.py, to coordinate canonical local URL resolution,
trusted file tenant/uploader/state check, exact slot/generation preparation,
business callback/commit boundary, post-commit reload/field match, activation,
old-binding revocation and failure compensation. Callers retain existing Task/
Document authorization; coordinator does not implement gateway, READ/PWA, legacy
claim or a new policy. Generic callbacks avoid adding Task/Document ACL into the
metadata-only registry or coupling Document routes to TaskService internals.
This is an architecture/scope recommendation, not a claim that Python cannot
physically place helpers in an existing file. USER must approve new module under
the explicit stop rule before implementation.

Proposed sidecar revision requiring review before coding:
allow old ACTIVE plus one reserved replacement PENDING per exact slot, using
separate SQLite uniqueness/serialization constraints and generation checks.
Activation transaction must atomically revoke previous exact binding and activate
new one only after confirmed business state; other object bindings remain intact.
Concurrent different replacements rejected; exact retries idempotent. No in-memory
lock authority. Stale PENDING unreadable; compensation does not revoke old ACTIVE
before business success. Sidecar schema version must distinguish revised constraints;
existing v1 handling must be explicit (no silent reset). This is sidecar state,
NOT business DB ALTER/migration. No revision/migration executed this batch.

Expected scope if approved: new coordinator plus already allowed drive/documents
and Task routes/service, registry/config as needed, tests/docs/log. DocumentService,
task_policy/models/database/app/static/templates/deployment remain untouched.
Test fixtures for existing SEC-05 local-link success cases may need actual synthetic
registered uploads rather than fictitious unregistered URL strings; preserve all
approved action expectations, do not permit untrusted URLs just to keep tests green.
No fixture or expectation changed yet.

Runtime/upload/binding/failure/concurrency acceptance NOT RUN for Batch4B2.
Targeted counts unavailable. Latest prior completed run remains Batch4B1
run-c00b7009fb654fb9ae233e7670be6da5: total754/2, registry77/0, SEC05 530/0,
SEC03 84/0, collision13/0. These are historical, not Batch4B2 evidence.
No new regression introduced by source changes (none); current runtime not assessed.

Integrity: independent protected SHA-256/size/mtime snapshots equal; selected Core
source fingerprints equal. PRODUCTION DB MODIFIED=NO; PRODUCTION DATA MODIFIED=NO;
PRODUCTION SOURCE MODIFIED=NO; PRODUCTION REGISTRY CREATED=NO; PRODUCTION UPLOAD
CREATED=NO. No startup, provider, seed/migration, upload scan or secret inspection.
Git working tree earlier changes retained; only this untracked log updated.
SEC04 OPEN; SEC05 FIXED; SEC03/BUG10 PARTIALLY FIXED; Drive rename BLOCKED.
Next: USER approval for coordinator file and sidecar replacement/version plan;
then resume Batch4B2 only. STOP; no gateway/static/PWA/legacy or other batch.

### Batch 4B2 SEC-04 Upload + Trusted Binding Integration — 2026-10-01 05:34 +07:00

Outcome: COMPLETE; batch status FIXED; **SEC-04 OPEN**. USER explicitly approved
new coordinator and revised replacement/schema constraints after the 04:53 stop.
No new scope approval required beyond those decisions; no prohibited file edited.

Files: NEW services/file_binding_service.py; services/file_registry.py;
services/drive_service.py; routes/documents.py; routes/tasks.py;
services/task_service.py; config.py (trusted LOCAL_UPLOADS identifier only);
tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; this log. DocumentService,
task_policy, models/business schema/database/session/app/static/templates/mobile/
deployment untouched. No additional production/test helper file introduced.

Upload: signed session tenant + exact tenant-local employee identity, server UUID
basename, explicit WRITING before exclusive physical open. Actual completed size
and SHA-256, flush/fsync then UNBOUND/24h expiry. Compatible URL/name response plus
additive opaque file_id; client owner/company/path/hash/size/identity not authority.
Failure never reports successful upload or creates usable metadata. Failed bytes
can remain revoked/unusable; no cleanup of old or pre-existing physical files.
Uploader-only same-tenant UNBOUND binding eligibility; ADMIN no implicit override.
UNBOUND READ/download enforcement is not implemented and static remains public.

Binding: canonical local upload URL -> exact server registry locator lookup,
tenant/classification/state/expiry/uploader and vetted binding check. NEW unknown,
foreign, other-uploader UNBOUND, expired/revoked/UNKNOWN and path/absolute aliases
fail closed before business write/PENDING authority. Client file_id does not grant
permission. Existing unchanged/inherited unregistered references preserve business
compatibility WITHOUT trusted ownership claim; no legacy scan/auto-claim. External
and local_docs behavior preserved without local private registry binding.

Task file_giao_viec uses existing SEC05 CREATE/EDIT authorization; file_bao_cao uses
REPORT and a distinct field slot. Server actor identity and path Task ID remain
authoritative. Document create/update uses unchanged ADMIN/CEO authorization and
unchanged DocumentService wrapped by route coordinator. Exact committed object ID
and exact persisted URL are reloaded before ACTIVE. Forward trusted parent file
gets a separate same-tenant child binding after successful child commit/reload;
parent/other bindings survive. Legacy inherited URL creates no trusted child claim.

Replacement: sidecar **v2** has separate unique partial indexes for ACTIVE and
PENDING tenant/object/field slots. One old ACTIVE plus one reserved PENDING may
coexist. Expected binding/generation activation transactionally supersedes only
old exact-slot ACTIVE. Clearing/external replacement revokes only confirmed exact
slot after business commit/reload. Shared other bindings and all old bytes survive;
files are not globally revoked on replacement/clear. Exact retry idempotent;
different reserved replacements fail closed. Index/schema/version checks fail
closed: incompatible v1/newer/missing constraints are NOT reset/recreated/upgraded.
No v1 production sidecar exists; no migration helper/business ALTER used.

Atomicity: PENDING commits first; registry BEGIN IMMEDIATE then spans short
business callback commit + exact reload + activation/revocation. SQLite constraints
and bounded busy handling serialize slots across processes; no in-memory lock.
Business and sidecar commits are separate. Fault after business commit may leave
new business URL persisted but NO new ACTIVE binding; old ACTIVE remains. API
reports failure; PENDING compensation revokes only still-PENDING receipt, never
ACTIVE retries. Busy/crash/compensation failure can leave unusable stale PENDING.
Future gateway MUST check live persisted field as well as ACTIVE binding + object
ACL; reconciliation/custodian tooling not implemented. No fabricated cross-DB
atomicity/automatic business rollback is claimed.

Tests: exact approved runner, final fresh directory
`.test_runtime/run-a81a2e790b8045a4ba8bf00ee958c0f3/`.
Read runtime_results.json, preflight.json and integrity.json; complete=true,
preflight PASS, **1092 PASS / 2 FAIL**. Targeted338/0 broken down above. Covers
three upload roles/server provenance/UUID/hash/size/expiry/auth denies/order,
unknown/foreign/unbound/path denial zero mutation, Task/report/Document/forward,
replacement reservation preserving old ACTIVE, failed commit/revalidation keeping
old ACTIVE, successful exact replacement and shared binding preservation, clearing,
exact retries, concurrent thread AND two-process replacements, incompatible version
and missing constraints with original bytes preserved. Fault injection at upload
registry/physical/completion, PENDING reservation, Task/report/Document/child commit,
exact Task/Document reload and activation boundaries. Authorization denials verify
A/B Task/Document rows, registry metadata, physical hashes and provider counts.
SEC05 positive attachment fixtures now use genuine synthetic trusted uploads;
all530 authorization expectations unchanged, no security assertion skipped/narrowed.

Rerun history (not final acceptance evidence): initial
run-353795891086431a936db60f29ad5c44 stopped at test bytes JSON serialization;
repaired boolean assertion. run-7dc71548daf946a1b2b609801c3e8466 completed1079/2,
then coverage expanded. run-4c01d965f11c426c8be92599af29e6c2 stopped at new legacy
Document fixture missing required loai; repaired fixture field (not authorization
expectations). Final fresh run above includes expanded checks and complete reports.
No production behavior FAIL observed in these incomplete runs; never count their
partial results as final acceptance. All finished parent integrity comparisons
showed production data unchanged.

Final regressions: foundation77/0; SEC05 530/0; SEC03 84/0; collision13/0;
login/dashboard/tasks/logout PASS; all11 routers load; only the two current
historical mobile500s; no new regression; provider calls0. Independent and guarded
protected SHA-256/size/mtime checks agree: production DB/data modified NO;
production registry/upload created NO. No production app/provider/seed/migration.
Core source change confined to approved files. Git diff/check reviewed: tracked
working tree now15 files +294/-292 vs entering4B2 +196/-269; this is cumulative,
NOT all 4B2 work. New/untracked registry/tests/log/mobile/VPS work retained. Compared
production hunks with preserved4B1 source snapshot to distinguish new integration.

Remaining: public static bypass, private HTTP/read ACL, PWA/cache protection and
custodian-reviewed legacy mapping; stale intent/post-commit reconciliation and
operational SQLite contention. SEC03 PARTIALLY FIXED/Drive rename BLOCKED;
BUG10 PARTIALLY FIXED; SEC05 FIXED. Next: request separate gateway/static scope;
STOP now, no4B3/PWA/legacy/other finding or commit.

### Batch 4B3 — SEC-04 Authenticated Private File Gateway

Reviewed 2026-10-01 06:37 +07:00 (Asia/Ho_Chi_Minh). USER authorized execution;
pre-implementation audit found no scope blocker. Outcome COMPLETE; batch status
FIXED, **SEC-04 OPEN**. This is online FastAPI source/runtime acceptance, not a
production deployment or PWA/offline security claim.

#### Source evidence and architecture

- Before: app.py dedicated public `/static/uploads` StaticFiles mount preceded
  parent `/static`; removing only the dedicated mount would still expose uploads.
  Global404 redirects HTML navigation but handles static/API errors separately.
- After: explicit GET/HEAD `/static/uploads/{storage_name:path}` before parent
  `PublicStaticFiles`. Parent independently refuses upload segments (case variants,
  separators/aliases) and resolved configured/conventional upload roots. Frozen
  and normal mounts use the same exclusion. No other Core router/startup change.
- Runtime precedence: authenticated canonical URL carries gateway marker and
  exact verified bytes; anonymous/unregistered/UNKNOWN URLs deny; direct parent
  `get_response('uploads/...')` denies, and HTTP alias matrix never returns private
  sentinel bytes. Representative CSS/JS/manifest/service worker remain200.
- Source nginx_vps_default.conf and vps_default.conf proxy to127.0.0.1:8081;
  deploy_vps.sh/run_vps.bat/chay_app.bat contain no direct uploads alias/root.
  **SOURCE NGINX BYPASS: NONE FOUND; ACTUAL PRODUCTION NGINX: NOT VERIFIED.**
- FileRegistry v2 supplies trusted locator, tenant/uploader, state/classification,
  expiry, size/hash and independent bindings. New access_snapshot uses exact
  `mode=ro`, query_only, foreign_keys, bounded busy timeout and readonly transaction.
  Missing/corrupt/incompatible/schema/busy errors never initialize/reset/fallback.
- Existing Document library predicate was extracted into readable_documents_query
  without changing semantics: ADMIN/CEO all; general and own department; MANAGER
  own plus direct-subordinate departments. Library and gateway share that query.
  DocumentService, Task policy/flows and business SQL schema were not changed.

#### Gateway decision and HTTP behavior

- Canonical single basename/raw URL required; session comes from current
  AuthService signed-session mechanism; tenant comes only from that session and
  actor from tenant-local task_policy.actor_from_session. Query/header role,
  actor/company/MST cannot grant authority. Existing untimed/stale-session risks
  SEC02 are not fixed; no expiration guarantee beyond the current mechanism.
- Registry entry mandatory. UNKNOWN/unregistered deny even ADMIN. WRITING and
  REVOKED deny. PRIVATE UNBOUND requires exact uploader, same tenant and unexpired
  24-hour intent; no ADMIN override and no fake object binding.
- BOUND requires at least one supported same-tenant ACTIVE binding with live
  object, exact current persisted URL and current READ ACL. Task assignment/report
  use authoritative can_view_task; Document uses the shared library predicate.
  Parent/child bindings remain independent; union of valid bindings grants READ.
  PENDING/revoked/unsupported or stale bindings never grant authority.
- Live tests cover deleted Task/Document, changed assignment/report/link fields,
  lost Task relationship/Document department permission, missing object, revoked
  binding, denied parent/allowed child, parent-only, both and neither relationship.
- Path guards reject nesting, encoded/double-encoded separators, traversal,
  drives/UNC, control characters and aliases. Server locator plus exact resolved
  root, lstat regular/reparse check and opened-handle final path confinement are
  required. Actual Windows symlink creation lacked privilege; junction NOT FULLY
  TESTABLE. Injected opened-handle outside-root denial PASS; do not equate that
  with real OS symlink/junction creation coverage.
- Size and full SHA-256 verified per request. Immutable verified bytes are served
  without a second filesystem open (avoids pathname replacement between hashing
  and FileResponse). Missing/directory/size/hash mismatch deny; tampered HEAD and
  If-None-Match also deny. Current new upload cap20MB bounds normal blob size;
  memory/IO cost and larger future verified legacy blobs need operational review.
- Authorization/hash precede GET/HEAD/Range206, invalid Range416 and conditional
  ETag/date304. Range is single-range; multi-range rejected416 only after auth.
  UNAUTHORIZED never receives ETag/mtime/size/range metadata, redirect or bytes.
  Anonymous/invalid401; authenticated unavailable/unauthorized404 use uniform
  private JSON, bypassing global HTML dashboard redirects.
- All private/error responses: Cache-Control private,no-store; Pragma no-cache;
  Expires0; nosniff. Content-Disposition sanitizes original_name for presentation;
  MIME comes from trusted extension with conservative inline types; other types
  download as octet-stream. Existing HTML/SVG extension blocking unchanged.
  **This does NOT solve service-worker Cache API. static/sw.js unchanged.**
- Every tested read/denial fingerprints synthetic business DB/registry/uploads
  and checks provider count; no mutation. Registry URI allowance in the guarded
  runner accepts only exact readonly URI inside the fresh run, not production.

#### Attempts and fresh evidence

1. `.test_runtime/run-e48fba78587d415b80f47d64f40577ab/`: completed with two new
   public CSS/JS404 failures plus two historical mobile failures. ROOT CAUSE:
   Windows StaticFiles normalizes separators to backslashes; initial guard
   rejected framework-produced separators. FIX: app.py checks raw request
   backslashes while retaining upload segment/realpath exclusion. Expectations
   unchanged; no security assertion skipped or downgraded.
2. `.test_runtime/run-c692f8711a85458fa11c4aace4114c57/`: fresh after repair,
   gateway482/0, total1574/2, prior security groups PASS. This provided targeted
   acceptance before the final full run. Then added report/Document/general and
   parent-only/hash-HEAD/conditional cases, cleaned readonly connection closure,
   enabled its foreign_keys, explicit classification allowlist, canonical URL
   quoting and controlled SQLAlchemy read errors; no ACL expectation change.
3. **Final fresh full run**:
   `.test_runtime/run-9dc4c7d902ef4445a5f90e9f836874ef/`.
   Read runtime_results.json, integrity.json, preflight.json,
   gateway_environment.json and source_manifest.json, not just exit status.
   Complete=true, no guard violations; preflight PASS; current Core hashes match
   tested manifest; provider mutations0. No production startup/provider request.

| Current targeted category | PASS | FAIL |
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
| TOTAL TARGETED | **531** | **0** |

Full guarded sandbox **1623 PASS / 2 FAIL**. Current 4B2 **338/0**;
registry foundation **77/0**; SEC05 **530/0**; SEC03 **84/0**;
BUG10 collision **13/0**. Login/dashboard/tasks/logout PASS, all11 Core routers
loaded. Only failures: `/mobile`500 and `/mobile/tasks`500 expected200, exactly
the two historical baseline bugs. **NEW REGRESSIONS: NONE in final run.**

#### Integrity, diff, checklist and remaining work

- Protected production DB/data/upload inventory: all10 SHA-256/size/mtime_ns
  before==after both across the batch and within each completed fresh run.
  PRODUCTION DB MODIFIED=NO; DATA MODIFIED=NO; REGISTRY CREATED=NO;
  UPLOAD CREATED=NO. No migration/seed on production, package install or commit.
- Approved production delta only: app.py, routes/documents.py (predicate only),
  services/file_registry.py (readonly snapshot), NEW file_access_service.py.
  Tests/docs/log/checklist also updated. Config, binding coordinator, Task/Drive,
  mobile/PWA/deployment/schema unchanged from pre-4B3 source fingerprints.
  Existing Phase A/4B1/4B2/SEC05/mobile/VPS/user working-tree edits retained.
  AST5 files and git diff --check PASS; reviewed full diff and changed source
  individually. Cumulative tracked diff includes prior work, not all attributable
  to4B3; untracked source/tests/docs likewise include historical artifacts.
- CODEX_REVIEW_CHECKLIST_4B3.md records current runtime evidence and explicit
  Windows link/actual-Nginx limitations. Historical CODEX_REVIEW_CHECKLIST.md
  unchanged. Checklist is reviewer evidence mapping, not a substitute for reports.
- **SEC04 OPEN**, SEC05 FIXED, SEC03/BUG10 PARTIALLY FIXED, Drive rename BLOCKED.
  Remaining: separately approved4B4 network-only Cache API/private-cache purge,
 4B5 verified custodian-reviewed legacy resolution, actual production proxy
  verification. UNKNOWN historical URLs now intentionally deny; no DB rewrite,
  legacy file move/scan/claim, registry production creation or deployment occurred.
  Recommend USER review4B3 first; stop without starting another batch.

### Batch4B4 — PWA Private Cache Protection

Reviewed2026-10-01 08:07 +07:00 (Asia/Ho_Chi_Minh). USER explicitly authorized
implementation/runtime validation. Outcome COMPLETE; batch status FIXED.
**SEC04 OPEN; Batch4B5 NOT STARTED.** No defined scope blocker encountered.

#### Pre-implementation audit: current architecture

- static/sw.js is authoritative and served by app.py `/sw.js` FileResponse.
  Whole-project source search (excluding dependencies/generated snapshots)
  found one registration in templates/mobile/layout.html: `/sw.js`, default root
  scope. No alternate active SW/cache architecture found; desktop layout does not
  register another worker. Manifest starts `/mobile`, references missing icons
  already tracked as HARD03; neither manifest nor mobile business code changed.
- OLD CACHE VERSION: qlcv-mobile-v1. Precache: authenticated `/mobile`, public
  mobile.css and manifest. Uploads not explicitly precached, but successful GET
  with raw URL.includes('/static/') entered Cache API, including uploads and
  cross-origin static-looking URLs/query strings. Method check only GET; no
  origin/path authority check. APIs/dashboard were not written dynamically, but
  offline fallback could return cached authenticated `/mobile` HTML for them.
- Old fetch fallback used origin-wide caches.match(request), including historical
  upload bytes, then cached `/mobile`. Activate removed ALL other cache names,
  not only QLCV-owned ones. Logout clears cookie, no SW message/purge; historical
  mobile logout-method bug remains untouched. Old Cache API bytes could outlive
  logout/tenant/user changes. Old same-version entries could survive updates.
- Gateway HEADERS already enforce private,no-store/Pragma/Expires/nosniff.
  Explicit Cache API put ignores HTTP cache directives; those headers alone
  were insufficient. Registryv2, signed sessions and gateway ACL unchanged.
- Existing Node22.11.0 available. Playwright/Puppeteer/selenium-webdriver module
  resolution unavailable; no packages installed. REAL BROWSER TEST=NOT RUN;
  PRODUCTION CLIENT TEST=NOT VERIFIED, neither treated as a false scope blocker.

#### Implementation and scope

- NEW CACHE VERSION: **qlcv-mobile-v2**. App-owned namespace is exact
  `^qlcv-mobile-v[0-9]+$`; similar third-party names are not owned by inference.
- Parsed same-origin URL.pathname is authority. Relevant encoding/separator/case
  aliases normalize for private `/static/uploads` namespace before generic cache
  logic. Query strings/fragments do not turn public CSS into a private request;
  uploads2/upload/foo-static lookalikes and foreign origin are distinguished.
- Private uploads and clearly dynamic/HTML/API non-public routes: network-only
  fetch(request,{cache:'no-store'}) for every method. No Cache API open/match/put/
  add/addAll/private fallback, including network rejection,401/403/404/5xx,
  logged-out or changed identity. Native Request method/headers remain intact.
- Cross-origin requests are not intercepted or put into app Cache API.
  Public same-origin static and manifest GET remain network-first/public scoped
  cache fallback. Other methods never cached. Public responses must be200,
  nonredirected, public final URL, non-HTML and without private/no-store headers.
  Public-URL redirect/no-store/private-target smuggling cannot populate cache.
- Install precaches only public CSS/manifest using validated fetch/put, no
  authenticated `/mobile` or private addAll. Activation explicitly enumerates
  every relevant QLCV cache; private entries are deleted without reading bytes.
  Old authenticated HTML/API/cross-origin entries in these caches are removed.
  Vetted public CSS/JS/manifest/other static entries migrate into current cache;
  obsolete QLCV versions are then removed. Non-QLCV caches remain untouched.
  clients.claim waits until cleanup completes. Version bump alone is not evidence.
- Public cached offline assets continue working; uncached public asset returns
  plain503, never cached authenticated `/mobile` HTML. Private/dynamic offline
  fetch rejects. No logout/session redesign or server-side revocation claim.
- Production delta ONLY static/sw.js. Test runner embeds actual-SW Node VM
  simulation rather than adding a new production/helper module. Test docs/log and
  NEW CODEX_REVIEW_CHECKLIST_4B4.md updated. App/gateway/registry/manifest/templates/
  Task/Drive/deployment untouched. No4B5 scan/onboarding/UNKNOWN claim/SQL migration.

#### Evidence classification and fresh runs

SOURCE VERIFIED: manual SW install/activate/fetch/path/write review, one registration,
server no-store, app-owned namespace; Node syntax and changed-Python AST PASS.
DETERMINISTIC SW LOGIC + SIMULATED CACHE LIFECYCLE VERIFIED: Node VM executes
actual snapshot static/sw.js with synthetic CacheStorage/fetch/clients/events;
no browser profile, real network, provider or production cache operation.
ACTUAL SYNTHETIC FASTAPI GATEWAY VERIFIED: existing guarded worker captures real
synthetic signed-session GET/HEAD/206/304/401/404 bodies/headers; Node replay checks
that the SW preserves them without any Cache API use. This is not real-browser
end-to-end cookie/SW/storage verification. REAL BROWSER=NOT RUN;
PRODUCTION CLIENT ACTIVATION/CACHE STATE=NOT VERIFIED.

- Standalone `.test_runtime/run-4acf8eac5007418ab9922dcc10b0c094/`:239/0.
  Additional request-header forwarding assertion then fresh standalone
  `.test_runtime/run-36dacce0ff4242c788e9ae68cca85058/`:240/0.
  No failed security assertion, expectation relaxation or skip occurred.
- First fresh full guarded run:
  `.test_runtime/run-cd82033620e84a3bae56f37fa7b1647a/`:310 targeted/0,
  full1933/2 historical mobile failures. Final review then added a second distinct
  old private filename (not just aliases of file A), with unchanged policy and
  expectations. Fresh standalone run-dc034ef6f4834d80a352031dd0c92f81:244/0.
- Final fresh full guarded run:
  `.test_runtime/run-7b3e6a1e3b29440fb38ff3a24dfc2c5d/`.
  Read runtime_results.json, pwa_results.json, pwa_gateway_fixtures.json,
  preflight.json, integrity.json and source_manifest.json. Node278 assertions
  (including actual gateway replay) +36 live worker integration/fingerprint
  assertions = **314 targeted4B4 PASS/0 FAIL**. Standalone counts are not
  substituted for full-run current evidence.

| Current4B4 category | PASS | FAIL |
| --- | ---: | ---: |
| PWA_PRIVATE_CLASSIFICATION | 19 | 0 |
| PWA_NETWORK_ONLY | 77 | 0 |
| PWA_NO_PRIVATE_WRITE | 47 | 0 |
| PWA_OLD_CACHE_PURGE | 19 | 0 |
| PWA_OFFLINE_PRIVATE | 22 | 0 |
| PWA_METHODS | 23 | 0 |
| PWA_PUBLIC_CACHE | 8 | 0 |
| PWA_CROSS_ORIGIN | 4 | 0 |
| PWA_CACHE_VERSION | 3 | 0 |
| PWA_4B3_INTEGRATION | 52 | 0 |
| PWA_ZERO_MUTATION | 40 | 0 |
| TOTAL TARGETED | **314** | **0** |

Old-cache fixtures include private A/B/aliases, public CSS/JS/manifest/other static,
authenticated mobile/API and cross-origin responses across v0/v1/v2/v12. Cleanup
removes app private entries/obsolete versions, preserves safe public data and
leaves unrelated/near-prefix third-party caches intact. Permanent private policy
also ignores deliberately reinserted stale fixtures; offline/logout/tenant/user
switch/UNKNOWN/denial cannot retrieve those bytes. Request Range/conditional
headers and methods preserve forwarding. Denied fixture replay preserves gateway
body/status/header, not cached successes.

Full complete=true: **1937 PASS/2 FAIL**. Gateway4B3 **531/0**;
4B2 **338/0**; registry **77/0**; SEC05 **530/0**; SEC03 **84/0**;
collision **13/0**. Login/dashboard/tasks/logout PASS;11/11routers;
guard violations empty; provider mutation count0; preflight PASS.
Only FAIL: `/mobile`500 and `/mobile/tasks`500 expected200, reproduced exact
historical baseline. **NEW REGRESSIONS: NONE.**

#### Integrity, review and remaining work

- All10 protected production DB/data/uploads inventory entries have equal
  SHA-256/size/mtime_ns before/after across batch and fresh run. Production DB
  modifiedNO; data modifiedNO; registry createdNO; upload createdNO. No production
  startup, seed/migration, real provider or browser-cache/profile operation.
- Current source_manifest (now includes static/sw.js) matches tested snapshot.
  Across-batch selected Core fingerprints differ ONLY for approved static/sw.js;
  historical gateway/registry/Task/mobile/VPS/source work preserved.
- git status/diff/stat/full diff/diff --check reviewed; syntax PASS. The tracked
  cumulative stat remains15 files +336/-306 from prior batches; SW/tests/docs are
  existing untracked artifacts, so git diff alone cannot show this batch's full
  delta. Do not attribute cumulative mobile/VPS/Phase A/4B1/4B2/4B3 work to4B4.
- Checklist4B4 maps each applicable acceptance criterion to current evidence;
  browser/client verification is explicitly NOT RUN/NOT VERIFIED. Historical
  4B2/4B3 checklists unchanged. No commit/destructive Git/package/deploy action.
- Guarantees apply after the updated worker activates. Unupdated clients,
  browser update timing, in-flight old workers and actual profile/cache persistence
  require browser/rollout verification; deterministic simulation is not proof of
  all engine lifecycle behavior. This does not erase downloaded/memory-resident
  files, third-party cache contents or revoke copied server sessions SEC02.
- **SEC04 OPEN**, SEC05 FIXED, SEC03/BUG10 PARTIALLY FIXED, Drive rename BLOCKED.
  Remaining4B5: verified custodian-reviewed UNKNOWN/legacy resolution, separately
  authorized; NOT STARTED. Actual production Nginx remains NOT VERIFIED. Recommend
  USER review4B4 and its browser-evidence limitations first; stop, no next batch.

## 13. Change History

The retrospective entries below were initialized at 2026-09-30 19:57 +07:00.
Their recording time is not an invented completion time for prior batches.
New work has an explicit date/time in its entry.

| Batch / finding | Files modified / change | Tests / outcome | Production DB/data | Regression / remaining risk / next step |
| --- | --- | --- | --- | --- |
| Phase A / scope removal | Ten files listed in section 6; disabled CRM/QuoteFlow runtime/UI entry points while retaining source/data | Static validation PASS; production runtime NOT RUN; phase outcome COMPLETE | NO / NO | Preserve user changes; no Phase B cleanup. |
| Core audit / SEC, BUG, HARD, CLEAN findings | No source change; source audit | AST/Jinja/diff PASS; targeted runtime initially NOT RUN | NO / NO | Findings remain open with confidence/limits above; prepare isolated tests. |
| Batch 1 / test isolation | Harness, fixtures, documentation and sandbox ignore | Sandbox PASS; 49/52 baseline checks PASS, three known FAIL | NO / NO | Sandbox safe through runner; initial harness issues corrected; no business fixes. |
| Batch 2A / SEC-03 | documents router and two test files | 84 SEC-03 checks PASS; overall 134/136 PASS, two known FAIL | NO / NO | Rename BLOCKED; mobile baseline unchanged; recommend private-file design audit. |
| Batch 2B.0 / SEC-04 inspection | No source/config/data change; preliminary read-only investigation | No new runtime test; design report incomplete | NO / NO | DEFERRED by documentation-only instruction; resume design when requested. |
| Documentation initialization / status handoff | Created this file | No runtime test; documentation review and Git status/diff review | NO / NO | No new fix authorized; maintain log after future authorized audit/fix/test. |
| 2026-09-30 20:10 +07:00; Batch 2B.0 / SEC-04 design completion | Only CODEX_AUDIT_FIX_LOG.md; completed flow/ownership/legacy/static/cache/options/scope/test design | Source/consumer review PASS; diff review/check PASS; 10 protected and 60 selected Core fingerprints unchanged; runtime NOT RUN | NO / NO | Design status DEFERRED -> FIXED (deliverable only); SEC-04 OPEN; SEC-03 PARTIALLY FIXED and rename BLOCKED. Full ACL/cache/legacy guarantees have dependencies; request policy/scope decisions before implementation. |
| 2026-09-30 20:25 +07:00; Batch 2B.1 / BUG-10 collision foundation | services/drive_service.py, tests/runtime_sandbox.py, this log; UUID identity + exclusive create/retry only | 13 targeted checks PASS; SEC-03 84 PASS; total 147/149 PASS, two baseline mobile FAIL; AST/diff review PASS | NO / NO | No new observed regression; numeric validation remains open, BUG-10 PARTIALLY FIXED; SEC-04 OPEN; no registry/gateway/cache changes. Recommend explicit policy/scope decisions before next private-file batch. |
| 2026-09-30 20:45 +07:00; Batch 3A / SEC-05 design audit and handoff confirmation | Only CODEX_AUDIT_FIX_LOG.md; source-connected action/actor/ID-bypass/tenant/file dependency audit, current flow and proposed policy/test scope | Source/UI and diff review PASS; protected/Core fingerprints unchanged; new runtime NOT RUN | NO / NO | No code regression introduced; business rules ambiguous, SEC-05 OPEN. SEC-04 still OPEN, SEC-03 PARTIALLY FIXED, rename BLOCKED. Approve business matrix before a separate fix instruction. |
| 2026-09-30 20:59 +07:00; Batch 3B / SEC-05 implementation and review-only stop | routes/tasks.py; services/task_service.py; new services/task_policy.py; tests/runtime_sandbox.py; this log. Approved action matrix, create identity/target validation and regressions written | Diff review/check PASS; runtime NOT RUN. Prior 147/149, SEC-03 84 and collision 13 PASS are historical, not current validation | NO / NO (before/after SHA-256/size/mtime match) | SEC-05 PARTIALLY FIXED; no acceptance/regression PASS claim. No further code/tests after user's review instruction. Recommend separately authorized guarded validation; stop now. |
| 2026-09-30 21:07 +07:00; Batch 3C / SEC-05 runtime validation | Central log only; unchanged guarded runner executed once, run-66c003f48123430e8bb962332aeb457f | AST/import-preflight/diff PASS; runtime FAIL with harness IndexError at line 492; runtime_results.json absent, counts unavailable; later tests/mobile not reached | NO / NO (independent snapshot and runner report agree) | SEC-05 PARTIALLY FIXED; no acceptance PASS claim. New harness failure, no proven new production regression. Recommend separately authorized test-only repair and fresh validation; no fix/rerun performed. |
| 2026-09-30 21:17 +07:00; Batch 3D / harness-only repair + fresh SEC-05 validation | tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; this log. Just-in-time suggestion, safe missing-row failure and incremental report persistence; no production changes | Fresh run-601a577af1c54f719542bfde7f8da525: 677 PASS/2 mobile baseline FAIL; SEC-05 530/0, SEC-03 84/0, collision 13/0; AST/preflight/diff PASS | NO / NO; hashes/size/mtime and source snapshot unchanged | SEC-05 FIXED within approved Task scope; no new regression. SEC-04 OPEN and other findings unchanged. Recommend separately authorized private-file scope; stop. |
| 2026-09-30 21:30 +07:00; Batch 4A / SEC-04 final architecture audit | Only CODEX_AUDIT_FIX_LOG.md; current-source static/consumer/ACL/cache/deployment review and sidecar/gateway/legacy/lifecycle/test/scope design | Source review and protected/Core fingerprints PASS; runtime NOT RUN; no registry created | NO / NO; source modified NO | Design COMPLETE only, SEC-04 OPEN; USER decisions and actual deployment/legacy evidence required. Recommend explicit policy approval then small authorized slice; stop. |
| 2026-09-30 22:33 +07:00; Batch4B1 / metadata foundation | New services/file_registry.py; config.py six added lines; tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; this log. Lazy sidecar v1 and metadata tests only | First registry72/0 run then fresh expanded two-process run-c00b7009fb654fb9ae233e7670be6da5: registry77/0, concurrency14/0, failclosed13/0; total754/2 mobile baseline; SEC05 530,SEC03 84,collision13 PASS; AST/diff PASS | NO/NO; production registry created NO | Foundation COMPLETE/FIXED, SEC04 OPEN; no production flow activation/new regression. Recommend separately authorized4B2; stop. |
| 2026-10-01 04:53 +07:00; Batch4B2 / pre-change scope audit | Only central log; examined upload/Task/report/Document/forward commits and v1 slot constraint | Source review and integrity PASS; runtime NOT RUN, no test counts claimed | NO/NO; registry/upload created NO; source changed NO | BLOCKED before new coordinator under explicit scope rule; request services/file_binding_service.py approval and sidecar replacement/version decision. SEC04 OPEN, other statuses unchanged; stop. |
| 2026-10-01 05:34 +07:00; Batch4B2 / resumed upload + trusted binding integration | Ten approved files listed above; new coordinator, lazy sidecar v2, trusted new upload and exact Task/report/Document/forward/replace/clear lifecycle | Final fresh run-a81a2e790b8045a4ba8bf00ee958c0f3: targeted338/0, foundation77/0, SEC05 530/0, SEC03 84/0, collision13/0; total1092/2 known mobile500s; AST/preflight/diff PASS. Earlier harness-only failures/retests disclosed above | NO/NO; production registry/upload created NO; Core source changed only approved scope | Batch COMPLETE/FIXED; SEC04 OPEN. Public files/PWA/legacy and cross-DB reconciliation remain. Recommend separately authorized gateway/static slice; STOP, no commit/next batch. |
| 2026-10-01 06:37 +07:00; Batch4B3 / authenticated private gateway | app.py, new file_access_service.py, readonly registry snapshot, exact Document READ predicate extraction, tests/docs/checklist/log | Final fresh run-9dc4c7d902ef4445a5f90e9f836874ef: gateway531/0; full1623/2; 4B2 338,registry77,SEC05 530,SEC03 84,collision13 PASS; Core/11routers/preflight/source manifest/AST/diff PASS. Initial Windows static guard defect and fresh repair runs disclosed | NO/NO; registry/upload created NO; only approved source changes | COMPLETE/FIXED batch; SEC04 OPEN; two historical mobile500s, no final new regression. Actual Nginx unverified, real Windows links partially testable. USER review before separate4B4/4B5; stop. |
| 2026-10-01 08:07 +07:00; Batch4B4 / PWA private cache protection | static/sw.js only production delta; embedded Node tests/actual synthetic gateway replay, test docs/log/new4B4 checklist | Final run-7b3e6a1e3b29440fb38ff3a24dfc2c5d: PWA314/0; full1937/2; gateway531,4B2 338,registry77,SEC05 530,SEC03 84,collision13 PASS; Core11/preflight/syntax/diff/source snapshot PASS. Earlier239/240/310 and final fixture244 fresh runs disclosed | NO/NO; production registry/upload createdNO; no actual browser/profile cache operation | COMPLETE/FIXED batch for source/deterministic simulated scope; REAL BROWSER NOT RUN, production clients NOT VERIFIED; SEC04 OPEN,4B5 NOT STARTED. USER review then separately authorize legacy resolution; stop, no deploy/commit. |

For each future authorized update, record actual date/time, batch/finding, files,
change, tests and PASS/FAIL, integrity, regressions, remaining risks and next step.
Do the requested work, tests, diff review and integrity verification first, then
update this handoff. Never include terminal dumps, secrets or production records.
# Batch 4B5 pre-implementation scope stop — 2026-10-01 08:23 +07:00

Documentation follow-up 2026-10-01 10:27 +07:00: uploader blocker reconfirmed; no production implementation/tests. Created CODEX_REVIEW_CHECKLIST_4B5.md and historical snapshot audit_codex_v1.md. Earlier status-table wording '4B5 not started' means implementation not started; audit has started and is BLOCKED. Latest runtime_results.json remains the historical Batch 4B4 artifact, not a 4B5 run. Versioned summary records this distinction and no fresh runtime PASS. Protected inventory checksum/size/mtime comparison for this documentation update is unchanged. SEC-04 OPEN. Change History: only central log, new 4B5 checklist and new versioned summary changed; no production code/data changes.

Status: BLOCKED before implementation. SEC-04 remains OPEN. No production legacy activation, inventory SQL query, application startup, new tooling, schema change or runtime test was performed in this attempt. Historical 1937 PASS / 2 mobile baseline FAIL remains Batch 4B4 evidence, not Batch 4B5 evidence.

Confirmed current-source blocker: services/file_registry.py:29 uses schema v2; :115 requires files.uploader_id TEXT NOT NULL; :141-143 register_writing validates uploader with _text (nonempty identity). VERIFIED_LEGACY is a classification label, not a separate unknown-uploader provenance representation. models/models.py Task attachment fields, Document.link_file and PersonalTask.file_dinh_kem do not record trusted physical-file uploader provenance. Giver/receiver/personal owner and editable URL cannot substitute for actual uploader. Existing audit evidence at the ownership limitations section also explicitly rejects Document update date/AuditLog event as upload provenance. services/drive_service.py:69,100 captures authenticated uploader for NEW uploads only; it does not establish historical upload provenance.

User prompt STOP conditions 9/23/38 apply: legacy uploader cannot be established from current attachment records, while the current registry registration/schema requires it. Custodian approval of a tenant/object mapping alone must not fabricate that identity. Discovery-only work could remain read-only, but completing the requested approved legacy apply workflow for unknown uploader requires a separately approved provenance/schema decision. No null identity, sentinel user, reviewer/admin identity or first-reference inference was introduced.

Required user decision: either restrict apply to candidates with independently verified actual uploader evidence (all others remain UNKNOWN), defining the accepted evidence source; or authorize an explicit sidecar-only schema revision representing VERIFIED_LEGACY with unknown uploader and separate custodian/provenance evidence, bound-only read semantics and strict atomic reviewed activation. No business DB migration is proposed. Candidate discovery tooling and full synthetic validation resume after that decision. Personal bindings remain unsupported by the current gateway; no new Personal ACL is proposed.

Integrity: before/after SHA-256, size and mtime_ns comparison of protected business DB/data/uploads performed for this read-only stop. PRODUCTION DB MODIFIED = NO; PRODUCTION DATA MODIFIED = NO; PRODUCTION REGISTRY CREATED = NO; PRODUCTION UPLOAD CREATED = NO; PRODUCTION FILE MOVED = NO; PRODUCTION LEGACY ACTIVATED = NO. Only this central log was changed. No Batch 4B5 runtime assertions or regression counts are claimed. Existing source/user changes were preserved. Next action: user decision on uploader provenance representation before implementation.

## Batch 4B5A — Legacy Provenance Model — COMPLETE (2026-10-01 10:51 +07:00)

USER explicitly authorized minimal registry-only provenance/schema work to resolve
the prior4B5 mandatory-uploader blocker. Original4B5 remains a historical stopped
attempt; full discovery/custodian mapping workflow and production apply have NOT
resumed. SEC-04 remains OPEN. No other finding status changed.

Actual uploader evidence audit: models Task.file_giao_viec/file_bao_cao,
Document.link_file, PersonalTask.file_dinh_kem are mutable references. AuditLog
does not record immutable physical upload provenance. Source search of services,
routes/models finds actual signed-session uploader only in NEW local upload flow
(routes/documents.py upload-local -> DriveService -> registry). No trustworthy
historical uploader source found in inspected source/schema; external archives
were not investigated. Reference/filename/business role never substitutes for it.

Chosen option A: explicit provenance fields in existing sidecar files table,
schema user_version3. VERIFIED_UPLOADER requires actual nonempty uploader,
PRIVATE/UNKNOWN classification and no legacy-review fields. Normal registration
cannot select legacy through flags, classification, JSON/form or browser route.
LEGACY_VERIFIED_MAPPING requires NULL uploader, VERIFIED_LEGACY classification,
BOUND/REVOKED state, no UNBOUND expiry and separate review_id/reviewed_by/evidence
digest. Reviewer is explicitly not uploader. SQL CHECKs plus registry/gateway
semantic validation distinguish malformed records; global nullable-uploader alone
was rejected. Binding schema/indexes, FK/busy handling and BEGIN IMMEDIATE remain.

Alternatives: separate legacy store/table adds identity/locator/FK coordination and
cross-store failure complexity; rejected as larger than four explicit fields in
one existing atomic sidecar. A sentinel/reviewer/ADMIN uploader or classification
label alone fabricates/mixes identity and was rejected. No business SQL change,
schema migration, URL rewrite, physical move or production sidecar upgrade.

New services/legacy_provenance.py is an offline infrastructure API only, imported
by synthetic tests and not any HTTP/business route. approve_mapping requires an
explicit APPROVED decision bound to exact mapping digest, individual review ID,
reviewer and independent-evidence input. register_verified_legacy rejects raw
client dictionaries; only the reviewed internal value is accepted. This is not
authentication against malicious Python code already holding SQLite write access.
Future trusted administrative tooling must authenticate custodian and validate
independent provenance and full tenant/reference/conflict inventory. No public
legacy mode, application startup hook, discovery tool or approve-all exists.

Atomic synthetic apply: validate allowed TASK assignment/report or DOCUMENT slots,
basename, actual confined file size/hash; BEGIN IMMEDIATE; trusted exact current
object revalidation callback; insert legacy identity with no uploader plus all
ACTIVE bindings; revalidate again and verify bytes; commit. Any exception or slot
conflict rolls back the whole metadata transaction. This applies already-existing
objects and does not mutate business DB. Live gateway revalidation remains
authoritative despite cross-DB races: legacy needs ACTIVE same-tenant supported
binding + live exact field + existing can_view_task/Document READ + size/hash/path.
No binding/uploader fallback/unsupported object/UNKNOWN/Admin override grants READ.
Normal upload/UNBOUND behavior, forward sharing and replacement policy unchanged.

Backward compatibility: read-only gateway accepts explicit v2 shape and valid
PRIVATE/UNKNOWN actual-uploader records as VERIFIED_UPLOADER without writing or
converting them to legacy. Malformed/ambiguous old records fail closed. All v2
mutation/init-upgrade attempts explicitly require a separate sidecar migration;
no upgrade helper or silent migration/reset/recreation here. Current production
registry is absent, so no immediate production migration required. Existing v2
deployments would need separately reviewed upgrade before mutations.

Files changed this batch: services/file_registry.py, services/file_binding_service.py,
services/file_access_service.py, NEW services/legacy_provenance.py,
tests/runtime_sandbox.py, tests/RUNTIME_SANDBOX.md, this log,
NEW CODEX_REVIEW_CHECKLIST_4B5A.md and NEW audit_codex_v2.md. Only the three existing
registry/binding/access modules differ from accepted4B4 source manifest; Task/Document
policy/routes, drive upload, config/app/static/SW/deployment/mobile unchanged.
Tracked git diff remains pre-existing15 files +336/-306; current modules/tests/docs
are untracked prior work, so tracked diff alone does not describe this batch.

Attempt1 run-7c6418a4981a46179c23fb5c5c96e21f:2153PASS/2 historical mobile FAIL;
diagnostic only, rejected by source-manifest check because provenance validation
was additionally applied to binding mutation and assertions were expanded during
the initial snapshot run. No production/security assertion was loosened. Final
fresh unchanged-source run-56914c095017492d97da57114b97fc2f accepted below.

Fresh targeted categories (all0FAIL):
PROVENANCE_MODEL5; NORMAL_UPLOADER_REQUIRED4; LEGACY_CREATION_AUTHORITY7;
LEGACY_NO_UPLOADER_FALLBACK10; LEGACY_BINDING_REQUIRED8; LEGACY_TASK_ACL16;
LEGACY_DOCUMENT_ACL10; LEGACY_TENANT_ISOLATION7; LEGACY_UNKNOWN_DENY9;
PROVENANCE_BACKWARD_COMPAT12; PROVENANCE_MALFORMED_DENY12; PROVENANCE_ATOMICITY5;
PROVENANCE_ATTACKS9; PROVENANCE_PATH_INTEGRITY10; PROVENANCE_PWA_INTEGRATION7;
PROVENANCE_ZERO_MUTATION103. TOTAL234PASS/0FAIL.

Final guarded sandbox2171PASS/2FAIL, complete=true; PWA314/0, gateway531/0,
4B2338/0, registry77/0, SEC05530/0, SEC0384/0, BUG10collision13/0. Only actual
/mobile500 and /mobile/tasks500 remain historical baseline failures. Core
login/dashboard/tasks/logout PASS; routers11/11; new regressions NONE.
preflightPASS, unexpected guard violations[], provider mutation calls0,
source manifest unchanged, AST and diff-checkPASS. Schema-version assertions
intentionally updated2->3; all prior security assertions remain covered.

Production SHA-256/size/mtime_ns before/after protected DB/master/tenant/data/uploads
unchanged. PRODUCTION DB MODIFIED=NO; DATA MODIFIED=NO; REGISTRY CREATED=NO;
UPLOAD CREATED=NO; FILE MOVED=NO; LEGACY ACTIVATED=NO. No production app startup,
provider request, package install, migration, mapping, deploy or Git commit.

Checklist4B5A:30 evidence-mapped acceptance items PASS; real-browser NOT RUN,
production clients and actual production Nginx NOT VERIFIED. Actual synthetic
legacy gateway response passed unchanged SW network-only/Cache API exclusion and
offline denial in Node VM, not a real-browser claim. Original provenance blocker
RESOLVED; full4B5 can resume after USER review, not automatically. Future workflow
still must implement complete discovery/conflict inventory, authenticated custodian
review and stale-review revalidation; production apply separately unauthorized.

Change History 2026-10-01 10:51 +07:00: Batch4B5A COMPLETE/model foundation;
234/0 targeted,2171/2 full; clean production integrity; immutable audit v1 preserved,
new v2 snapshot/checklist/log consistent with final current-source runtime evidence.
SEC-04 OPEN. Recommended next action: USER review4B5A before separately resuming
4B5 safe tooling; stop here, no production legacy activation.

## Resumed Batch 4B5 — Legacy discovery/review tooling (2026-10-01)

Batch = USER-authorized resumed 4B5 after completed 4B5A.
Status = COMPLETE (tooling/synthetic validation only).
Audit report = [audit_codex_v3.md](audit_codex_v3.md), authoritative acceptance and evidence.
Targeted = 225 PASS / 0 FAIL; all prior security groups PASS.
Full sandbox = 2396 PASS / 2 historical mobile HTTP 500 FAIL; run-44c3751cf1424f059f00b4305853ce0c; no new regression.
Production integrity = unchanged SHA-256/size/mtime_ns; read-only inventory 2 UNKNOWN, 0 activated; no registry/binding/upload created or files moved/deleted.
SEC-04 = OPEN; no production approval/apply or rollout verification.
Next action = USER review audit v3 and decide final production legacy policy; STOP.

## Batch SEC-01 — Master identity escalation (2026-10-01)

Batch = USER-authorized SEC-01 audit.
Finding = SEC-01 master identity escalation.
Root cause = Default-tenant reserved Employee IDs grant master; tenant ADMIN/CEO employee management can create those identities or replace the same ADMIN credential used for master login.
Status = BLOCKED before implementation: complete protection requires a MASTER credential-management boundary changing existing tenant business authorization, an explicit prompt STOP CONDITION. SEC-01 remains OPEN.
Audit report = [audit_codex_v4.md](audit_codex_v4.md).
SEC01 targeted = NOT RUN; source structural proof only.
Full sandbox = NOT RUN; latest historical v3 remains 2396 PASS / 2 mobile FAIL.
New regression = NOT ASSESSED by fresh runtime; production/test source unchanged.
Production integrity = PASS, fresh protected SHA-256/size/mtime_ns match; registry absent; legacy activated0.
Next action = USER authorize narrow MASTER-account creation/credential/role protection against ordinary default-tenant Employee management before SEC-01 implementation; STOP.

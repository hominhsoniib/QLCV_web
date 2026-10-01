# 1. AUDIT VERSION

AUDIT FILE = audit_codex_v3.md
CREATED = 2026-10-01T12:07:56+07:00
PROJECT ROOT = D:\App_Claude_Antigravity\QLCV_web
CURRENT BATCH = Resumed 4B5, post-4B5A verified legacy discovery/review tooling
VERSION = 3
PREVIOUS VERSION PRESERVED = YES

Exact root filename scan found v1/v2 only. This report is created exclusively, without overwriting either historical version. Existing checklist files remain untouched.

# 2. EXECUTIVE SUMMARY

RESUMED BATCH 4B5 TOOLING COMPLETE = YES.
Read-only discovery, conservative classification, signed independent custodian review, complete tenant-scope validation and atomic synthetic apply are implemented. Reference-only files remain UNKNOWN; reviewer never becomes uploader. No production mapping, registry initialization, binding, migration or activation occurred.

Fresh targeted = 225 PASS / 0 FAIL. Fresh full sandbox = 2396 PASS / 2 historical mobile FAIL. All prior security groups pass; NEW REGRESSION = NONE. SEC-04 remains OPEN pending USER-approved final production legacy policy and rollout evidence. No unrelated finding is newly marked FIXED.

# 3. CURRENT PROJECT STATUS

4B1, 4B2, 4B3, 4B4, 4B5A and resumed 4B5 tooling are COMPLETE.
The original v1 mandatory-uploader representation blocker was resolved by v2/4B5A. This batch completes discovery/review tooling, not production legacy restoration.
Production legacy activated = 0. Final production legacy policy/review remains OPEN.
Historical /mobile and /mobile/tasks HTTP 500 remain. Drive rename remains BLOCKED.
BUG-10 is PARTIALLY FIXED: collision protection passes; numeric validation is outside this batch.
Real browser PWA testing is NOT RUN. Production-client rollout and actual production Nginx remain NOT VERIFIED. No further batch is started.

# 4. CURRENT SECURITY STATUS

| Finding | Current status | Evidence/limit |
|---|---|---|
| SEC-01 master identity escalation | OPEN | Historical status retained; not modified here |
| SEC-02 session lifetime/revocation/revalidation | OPEN | No session redesign or revocation claim |
| SEC-03 upload/Drive ownership | PARTIALLY FIXED | 84 fresh regression PASS; Drive rename remains blocked |
| SEC-04 private files | OPEN | Foundations and tooling pass; production legacy policy/rollout not accepted |
| SEC-05 Task authorization | FIXED | 530 fresh assertions PASS; existing policy unchanged |
| SEC-06 tenant path confinement | OPEN | No resolver or unrelated path-policy change |
| SEC-07 identity lookup/index ownership | OPEN | Not modified here |

These statuses derive from historical audits/log plus current regressions, not a claim that unrelated findings were re-audited or fixed.

# 5. CURRENT BATCH RESULT

IMPLEMENTATION PERFORMED = YES.
TOOLING ACCEPTANCE = PASS.
PRODUCTION LEGACY ACTIVATION = NO.
PRODUCTION INVENTORY = READ-ONLY RUN.
UPLOADER PROVENANCE = NOT FABRICATED.
DEFAULT APPROVAL = UNAPPROVED.
APPLY-TIME REVALIDATION = PASS.
ATOMIC SYNTHETIC APPLY = PASS.
UNKNOWN DEFAULT DENY = PASS.
CROSS-TENANT HANDLING = PASS.
PRODUCTION CANDIDATES ACTIVATED = 0.
Separate new checklist created = NO. Acceptance is embedded below.
Central log updated with a concise reference to this version.

# 6. LEGACY DISCOVERY ARCHITECTURE

Before editing: registry v3 distinguishes VERIFIED_UPLOADER from LEGACY_VERIFIED_MAPPING. Normal uploads require the actual authenticated uploader; reviewed legacy uses NULL uploader, separate review metadata and a BOUND identity with valid ACTIVE binding. The offline 4B5A primitive already atomically inserts identity/bindings and revalidates. The 4B3 gateway requires live Task/Document references and ACL; 4B4 SW is private network-only. Full discovery/conflict/custodian workflow did not exist.

Now services/legacy_discovery.py provides a standalone offline module, never imported by startup/HTTP routes. Explicit trusted tenant DB manifest + physical upload root + optional existing sidecar feed discovery. No Config/app/resolver startup imports occur during discovery. SQLite uses mode=ro&immutable=1, query_only, bounded handling and fingerprint checks; active WAL/journal sources are refused rather than ignored. Physical evidence uses confined canonical regular files, opened-file identity, size, SHA-256 and stable metadata. Symlink/reparse/invalid paths are not candidates.

Sources inventoried: tasks.file_giao_viec, tasks.file_bao_cao, documents.link_file, personal_tasks.file_dinh_kem where schema exists; forwarded Tasks are actual separate Task rows. Existing registry identities and bindings are inspected without initialization. Personal has no approved gateway ACL and remains unsupported/UNKNOWN for apply.

Only literal canonical persisted /static/uploads/basename references qualify. Queries/fragments, encoding, separators, dot/drive/UNC/NUL/case aliases are rejected as ownership/binding input. Absolute URLs are excluded: current trusted binding flow does not accept them. Public lookalikes/local_docs remain non-upload references. No URL rewrite occurs.

References/tenant DB context are observations, not ownership. Structurally consistent files remain UNKNOWN and UNAPPROVED. Physical aliases/hardlinks are AMBIGUOUS; cross-tenant physical/reference overlap is CROSS_TENANT_CONFLICT. Supported same-tenant multiple bindings use existing union ACL semantics only after reviewed synthetic approval.

Read-only CLI: venv\\Scripts\\python.exe -B -m services.legacy_discovery --upload-root <root> --tenant TENANT=DATABASE [--tenant ...] [--registry <existing-sidecar>].
Default stdout is aggregates. Optional --output exclusively creates a private raw JSON artifact outside uploads/static; there is no production apply or approve-all CLI option.

# 7. PRODUCTION INVENTORY

STATUS = READ-ONLY RUN, aggregate-only output.
Trusted tax codes were read from master_companies with immutable SQLite. Current resolver path convention and every actual tenant DB source were matched explicitly; the resolver itself was not imported/run. Configured upload/root defaults were checked without app startup. Complete-scope validation passed.

Physical uploads = 2 (housekeeping .gitkeep excluded).
Nonempty references = 21: Task assignment 4, Task report 1, Document 16, Personal 0.
Local canonical references = 2; unique normalized local references = 2.
External references = 8; invalid paths = 11.
Registry status = ABSENT.
Structurally reviewable UNKNOWN = 2; independently verified candidates = 0.
Production candidate approvals = 0; production candidates activated = 0.
No confidential production filenames or user records are exported in this report. No full production mapping artifact was created; raw aggregate evidence is production_legacy_inventory.json.

# 8. CLASSIFICATION RESULTS

| Class | Meaning | Production count |
|---|---|---|
| VERIFIED_CANDIDATE | Independent custodian evidence approved for exact review; never automatically ACTIVE | 0 |
| AMBIGUOUS | Physical aliases or evidence cannot determine one safe identity | 0 |
| CONFLICT | Incompatible trusted registry identity/metadata | 0 |
| CROSS_TENANT_CONFLICT | Same physical identity referenced by multiple tenants; no sharing inferred | 0 |
| ORPHAN | Physical bytes with no supported reference; do not register/delete | 0 |
| MISSING_PHYSICAL | Canonical reference with missing bytes; no placeholder | 0 |
| MISSING_OBJECT | Existing binding points to deleted/missing object; no activation | 0 |
| INVALID_PATH | Unsafe/noncanonical path/reference, excluded | 11 references |
| EXTERNAL_REFERENCE | Absolute/external URL, excluded from local registry | 8 references |
| PUBLIC_NON_UPLOAD | Non-upload local source/lookalike, excluded | 0 |
| ALREADY_REGISTERED | Existing compatible trusted identity; never overwritten | 0 |
| UNKNOWN | Insufficient independent provenance or unsupported ACL; denied | 2 |

Production file counts and excluded-reference counts are different units; classification totals are not claimed to equal physical file count. Synthetic raw inventory demonstrates Task/Document/Personal, multi-reference, hardlink ambiguity, cross-tenant conflict, registry conflict, missing object/physical, orphan and excluded-reference cases.

# 9. REVIEW / APPROVAL MODEL

Discovery emits deterministic JSON with candidate_id, physical identity/hash/size/path, references, exact proposed object bindings, tenant/source manifest, conflicts, ambiguity reasons, registry/binding evidence, evidence_digest, approval_status=UNAPPROVED and review_id absent.

Trusted offline CustodianAuthority uses an independent principal/key. An explicit independent attestation/backup/immutable record must identify the tenant and actual physical SHA-256, source ID and statement. Approval signs the exact candidate/evidence digest with HMAC-SHA256; no ADMIN/browser role or editable URL issues authority. Reviewer is separate metadata, never uploader. Tests use ephemeral synthetic keys; no production key, approval or custodian authentication rollout is created. Actual key custody and human evidence validation remain administrative responsibilities.

apply_synthetic hard-rejects the production checkout before configuration/import/mutation. The copied module, registry, upload root and every DB must reside in the exact guarded .test_runtime/run-* directory. Complete current master tenant metadata and actual tenant DB inventory are required before and within apply; a partial manifest cannot omit a conflicting tenant. The entire manifest is included in candidate evidence.

Apply rediscovery rechecks path/physical hash/size, exact tenant/object/field references, registry conflicts, eligibility and signed evidence. Material changes produce STALE_REVIEW/denial. The legacy primitive's minimal optional serialized callback inspects the same BEGIN IMMEDIATE transaction, excluding only its own newly inserted identity/bindings. Pre/post validation plus physical verification run before commit. Any exception rolls back identity and all bindings. Business DBs/bytes are never written by apply. No atomic business-DB/sidecar transaction is claimed: the gateway still revalidates live references and ACL on every read.

Successful synthetic mapping is LEGACY_VERIFIED_MAPPING, NULL uploader, BOUND plus exact ACTIVE supported bindings. There is no uploader fallback. Already-applied receipts fail closed instead of duplicating identities. Existing registered UNKNOWN/revoked/conflicting rows are not overwritten/promoted, and unsupported Personal references remain denied.

# 10. ACCEPTANCE CHECKLIST

All applicable tooling items PASS. PASS = 46; FAIL = 0; supplemental NOT RUN = 3; NOT FULLY TESTABLE = 0.
Evidence labels below refer to the fresh final runtime_results.json unless a source/raw artifact is named.

- **reference != ownership**: STATUS = PASS. EVIDENCE = LEGACY_CLASSIFICATION: consistent Task references remain UNKNOWN, only eligible for independent review.
- **uploader not fabricated**: STATUS = PASS. EVIDENCE = LEGACY_PROVENANCE_INTEGRATION: NULL uploader; LEGACY_CUSTODIAN_BINDING: reviewer stored separately.
- **4B5A provenance preserved**: STATUS = PASS. EVIDENCE = LEGACY_PROVENANCE_INTEGRATION plus all 234 original 4B5A assertions.
- **UNKNOWN default deny**: STATUS = PASS. EVIDENCE = LEGACY_UNKNOWN_DENY: anonymous, authenticated and ADMIN denials.
- **normalization safe**: STATUS = PASS. EVIDENCE = LEGACY_NORMALIZATION: 23 assertions; exact persisted URL agrees with 4B2 binding parser.
- **traversal rejected**: STATUS = PASS. EVIDENCE = LEGACY_NORMALIZATION: encoded/double-encoded traversal, separators, drive/NUL/dot/case aliases denied.
- **external references excluded**: STATUS = PASS. EVIDENCE = LEGACY_EXTERNAL_REFERENCE: external URL excluded from local identity; absolute URLs never become ownership.
- **orphan fail-closed**: STATUS = PASS. EVIDENCE = LEGACY_ORPHAN: ORPHAN classification and approval rejection; LEGACY_UNKNOWN_DENY.
- **missing physical fail-closed**: STATUS = PASS. EVIDENCE = LEGACY_MISSING_PHYSICAL: classification and approval rejection; no placeholder.
- **missing object fail-closed**: STATUS = PASS. EVIDENCE = LEGACY_MISSING_OBJECT plus LEGACY_STALE_REVIEW deleted-object rejection.
- **cross-tenant conflict detected**: STATUS = PASS. EVIDENCE = LEGACY_CROSS_TENANT: conflict/approval denial/incomplete manifest denial; LEGACY_STALE_REVIEW new tenant conflict.
- **same-tenant multi-reference safe**: STATUS = PASS. EVIDENCE = LEGACY_MULTI_BINDING: one identity, three exact Task/Document bindings and separate parent/forwarded-child bindings.
- **physical alias ambiguity denied**: STATUS = PASS. EVIDENCE = LEGACY_CLASSIFICATION: real synthetic hardlinks classified AMBIGUOUS, approval denied.
- **review artifact deterministic**: STATUS = PASS. EVIDENCE = LEGACY_REVIEW_ARTIFACT: repeated discovery JSON identical; legacy_review_synthetic.json.
- **default UNAPPROVED**: STATUS = PASS. EVIDENCE = LEGACY_REVIEW_ARTIFACT: every discovered candidate UNAPPROVED, review_id absent.
- **explicit custodian approval required**: STATUS = PASS. EVIDENCE = LEGACY_APPROVAL_REQUIRED: no authority/evidence/unapproved receipt denied; no HTTP approval route.
- **reviewer != uploader**: STATUS = PASS. EVIDENCE = LEGACY_CUSTODIAN_BINDING and NULL uploader assertion.
- **evidence digest binding**: STATUS = PASS. EVIDENCE = LEGACY_CUSTODIAN_BINDING: signed candidate/evidence digest; tampering and fake ADMIN/client reviewer denied.
- **complete tenant scope required**: STATUS = PASS. EVIDENCE = LEGACY_CROSS_TENANT: partial manifest denied; apply checks current master sources and all tenant DBs; digest includes full scope.
- **apply-time revalidation**: STATUS = PASS. EVIDENCE = LEGACY_REVALIDATION and LEGACY_STALE_REVIEW; complete rediscovery before and inside serialized transaction.
- **stale review denied**: STATUS = PASS. EVIDENCE = LEGACY_STALE_REVIEW: six material-change cases, no partial authority.
- **hash change denied**: STATUS = PASS. EVIDENCE = LEGACY_STALE_REVIEW: changed hash at same size denied.
- **size change denied**: STATUS = PASS. EVIDENCE = LEGACY_STALE_REVIEW: changed size denied.
- **physical removal denied**: STATUS = PASS. EVIDENCE = LEGACY_STALE_REVIEW: removed physical file denied.
- **reference change denied**: STATUS = PASS. EVIDENCE = LEGACY_STALE_REVIEW: removed reference denied.
- **deleted object denied**: STATUS = PASS. EVIDENCE = LEGACY_STALE_REVIEW: deleted business object denied.
- **new conflict denied**: STATUS = PASS. EVIDENCE = LEGACY_STALE_REVIEW: newly added foreign-tenant reference denied.
- **atomic synthetic apply**: STATUS = PASS. EVIDENCE = LEGACY_ATOMIC_APPLY: BOUND identity/all bindings succeed atomically; injected post-insert failure rolls back.
- **UNKNOWN B remains denied when A approved**: STATUS = PASS. EVIDENCE = LEGACY_UNKNOWN_DENY: unapproved Document B denied to ADMIN after approved Task A.
- **no public fallback**: STATUS = PASS. EVIDENCE = LEGACY_UNKNOWN_DENY plus 531 GATEWAY assertions, including parent static exclusion.
- **4B5A regression**: STATUS = PASS. EVIDENCE = Original provenance group, separate from B4B5-prefixed assertions.
- **4B4 regression**: STATUS = PASS. EVIDENCE = PWA group; actual unchanged worker executed in Node VM/CacheStorage simulation.
- **4B3 regression**: STATUS = PASS. EVIDENCE = GATEWAY group; actual ASGI protected file requests.
- **4B2 regression**: STATUS = PASS. EVIDENCE = B4B2 upload/binding/replacement/process-concurrency group.
- **Registry regression**: STATUS = PASS. EVIDENCE = REGISTRY foundation including multi-process assertions.
- **SEC-05 regression**: STATUS = PASS. EVIDENCE = SEC05 authorization matrix preserved.
- **SEC-03 regression**: STATUS = PASS. EVIDENCE = SEC03 authenticated uploads/denied Drive rename; provider mutation count 0.
- **BUG-10 collision regression**: STATUS = PASS. EVIDENCE = BUG10 exclusive-create/collision assertions; numeric validation remains outside scope.
- **Core smoke**: STATUS = PASS. EVIDENCE = 32 fresh login/dashboard/tasks/logout smoke assertions PASS; mobile excluded explicitly.
- **11 routers**: STATUS = PASS. EVIDENCE = runtime_results.json routers: all eleven loaded.
- **mobile baseline unchanged**: STATUS = PASS. EVIDENCE = Only two raw FAIL: /mobile500 and /mobile/tasks500, matching accepted historical HTTP baseline.
- **production inventory read-only**: STATUS = PASS. EVIDENCE = production_legacy_inventory.json; immutable/query-only SQLite, complete trusted master manifest, no startup.
- **production integrity**: STATUS = PASS. EVIDENCE = integrity.json plus independent before/after SHA-256/size/mtime_ns; all protected entries identical.
- **production legacy activated = 0**: STATUS = PASS. EVIDENCE = Production registry remains absent; no production binding/activation/apply.
- **private PWA behavior preserved**: STATUS = PASS. EVIDENCE = LEGACY_PWA_INTEGRATION: approved legacy network response/no-store, zero Cache API operation and offline denial.
- **normal uploader requirement preserved**: STATUS = PASS. EVIDENCE = 234 original 4B5A and 338 4B2 assertions; VERIFIED_UPLOADER still mandatory, no public legacy mode.

- **Real browser/PWA execution**: STATUS = NOT RUN. EVIDENCE = pwa_results.json uses actual SW in Node VM with synthetic CacheStorage/network, not browser ServiceWorker registration.
- **Actual production Nginx/client rollout**: STATUS = NOT RUN. EVIDENCE = no deployment/production connection authorized or performed; historical live verification remains outstanding.
- **Production custodian review/final legacy policy**: STATUS = NOT RUN. EVIDENCE = production approvals/activation 0; USER review still required. This is outside tooling acceptance and keeps SEC-04 OPEN.

# 11. TARGETED TEST RESULTS

Fresh final run: .test_runtime/run-44c3751cf1424f059f00b4305853ce0c/runtime_results.json.

| Category | PASS | FAIL |
|---|---:|---:|
| LEGACY_APPROVAL_REQUIRED | 3 | 0 |
| LEGACY_APPROVED_ACCESS | 15 | 0 |
| LEGACY_ATOMIC_APPLY | 3 | 0 |
| LEGACY_CLASSIFICATION | 8 | 0 |
| LEGACY_CONFLICT | 1 | 0 |
| LEGACY_CROSS_TENANT | 3 | 0 |
| LEGACY_CUSTODIAN_BINDING | 7 | 0 |
| LEGACY_DISCOVERY | 3 | 0 |
| LEGACY_EXTERNAL_REFERENCE | 1 | 0 |
| LEGACY_MISSING_OBJECT | 1 | 0 |
| LEGACY_MISSING_PHYSICAL | 2 | 0 |
| LEGACY_MULTI_BINDING | 11 | 0 |
| LEGACY_NORMALIZATION | 23 | 0 |
| LEGACY_ORPHAN | 2 | 0 |
| LEGACY_PROVENANCE_INTEGRATION | 5 | 0 |
| LEGACY_PWA_INTEGRATION | 7 | 0 |
| LEGACY_REVALIDATION | 1 | 0 |
| LEGACY_REVIEW_ARTIFACT | 2 | 0 |
| LEGACY_STALE_REVIEW | 6 | 0 |
| LEGACY_UNKNOWN_DENY | 33 | 0 |
| LEGACY_ZERO_MUTATION | 88 | 0 |
| TOTAL RESUMED 4B5 | 225 | 0 |

B4B5-prefixed assertions are separated from the original 4B5A LEGACY_/PROVENANCE_ assertions. SW replay assertions for approved legacy bytes are included in LEGACY_PWA_INTEGRATION; no prior security assertion was dropped or weakened.

# 12. REGRESSION RESULTS

Fresh final results, not historical counts reused:

| Group | PASS | FAIL |
|---|---:|---:|
| 4B5A | 234 | 0 |
| B4B2 | 338 | 0 |
| BUG10 | 13 | 0 |
| GATEWAY | 531 | 0 |
| PWA | 314 | 0 |
| REGISTRY | 77 | 0 |
| SEC03 | 84 | 0 |
| SEC05 | 530 | 0 |

Historical v2 full baseline = 2171 PASS / 2 FAIL; fresh final full adds exactly 225 passing 4B5 assertions. Original groups remain equal to their accepted coverage. PWA evidence is deterministic runtime/simulation; real-browser NOT RUN.

# 13. FULL GUARDED SANDBOX

Command = .\\venv\\Scripts\\python.exe -B tests/runtime_sandbox.py
Final run = .test_runtime/run-44c3751cf1424f059f00b4305853ce0c
complete = true
PASS = 2396
FAIL = 2
NEW REGRESSION = NONE
unexpected_guard_violations = []
provider mutation count = 0
production integrity = PASS
tested current source match = PASS

Only raw failures: mobile dashboard baseline actual500/expected200; mobile tasks baseline actual500/expected200. They are retained as FAIL in raw results and explicitly recognized as historical, not relabeled PASS.

Fix/rerun history (raw details: legacy_attempts.json):
1. run-93284f08fa9347c696a626c93a2a80b1: incomplete, immutable read-only URI rejected by harness guard. Repair only allows the exact additional immutable read-only query and retains path/URI/ATTACH isolation. No successful acceptance is claimed for this run; checkpoint JSON can predate the guard exception.
2. run-d5f8dec9a50741a7b7ea20f36305d6db: incomplete, missing-file helper KeyError before approval validator. Repair uses .get for missing SHA so actual approval denial is exercised, without weakening expected denial. Hardlink ambiguity coverage added.
3. run-4bad803ec3aa4acaaced78feaf2064db: complete222/0 targeted,2393/2 full. Post-run review found incomplete tenant manifest could omit conflicts. Added complete master/DB scope validation and digest binding, requiring a fresh rerun.
4. Final run above: complete225/0 targeted,2396/2 full; partial-scope attack denied, all security groups PASS.

Supplementary guarded synthetic apply smoke PASS is not added to targeted counts. Its initial import hit the known Windows platform subprocess/devnull guard before DB mutation; the existing harness OS-version stub allowed safe isolated import. No provider call or production change occurred in any attempt.

# 14. CORE APPLICATION STATUS

login = PASS
dashboard = PASS
tasks = PASS
logout/post-logout = PASS
32 fresh Core smoke assertions PASS.
routers = 11 / 11: auth, tasks, master, companies, documents, personal, ai, processes, jds, org_chart, mobile.

/mobile = HTTP 500, HISTORICAL BASELINE.
/mobile/tasks = HTTP 500, HISTORICAL BASELINE.
No mobile source/template/business fix is made.

# 15. PRODUCTION INTEGRITY

PRODUCTION DB MODIFIED = NO
PRODUCTION DATA MODIFIED = NO
PRODUCTION REGISTRY CREATED = NO
PRODUCTION BINDING CREATED = NO
PRODUCTION UPLOAD CREATED = NO
PRODUCTION FILE MOVED = NO
PRODUCTION FILE DELETED = NO
PRODUCTION LEGACY ACTIVATED = NO

Harness integrity.json before/after SHA-256, size and mtime_ns match. Independent snapshot covering the earlier production inventory and every attempt also matches all 10 protected entries. Upload membership/metadata/bytes are identical and production registry remains absent, so no binding/legacy identity was created. Approved source edits are separate from data integrity.

No production app startup, schema migration, seed, package install, provider request, deployment, restart, Nginx reload, firewall modification or production browser-cache operation occurred.

# 16. FILES CHANGED BY CURRENT BATCH

CURRENT BATCH CHANGES:

- services/legacy_discovery.py (new offline discovery/review/synthetic-only apply).
- services/legacy_provenance.py (minimal optional same-transaction revalidation callback; existing behavior retained).
- tests/runtime_sandbox.py (new B4B5 fixtures/assertions, exact immutable URI guard support, approved legacy SW fixture).
- tests/RUNTIME_SANDBOX.md (workflow/isolation/evidence documentation).
- CODEX_AUDIT_FIX_LOG.md (concise historical entry referencing this audit).
- audit_codex_v3.md (this new immutable snapshot).

No registry schema, gateway/read ACL, upload endpoint, Task/Document policy, service worker, resolver, business schema, mobile or deployment code changed.

PRE-EXISTING WORKING TREE CHANGES:

15 tracked files (+336/-306), unchanged by this batch: HUONG_DAN_DEPLOY_CLOUD_VPS.md; app.py; chay_app.bat; config.py; deploy_vps.sh; main_launcher.py; nginx_vps_default.conf; routes/documents.py; routes/tasks.py; run_vps.bat; services/drive_service.py; services/task_service.py; templates/help_guide.html; templates/layout.html; vps_default.conf. Prior untracked work includes mobile builder/routes/templates/assets, historical audits/checklists, registry/binding/access/task-policy/provenance modules, tests and .test_runtime artifacts. These are not attributed to resumed 4B5.

Against accepted 4B5A source_manifest, the only modified existing selected Core source is services/legacy_provenance.py; legacy_discovery.py is new. Final source_manifest matches current tested source. Git diff/status/stat reviewed; tracked diff remains prior +336/-306. Git diff --check and new/module comparison whitespace checks found no whitespace errors (Git reports existing LF/CRLF conversion notices). Python AST PASS for three changed/new Python files; isolated imports/runtime PASS.

# 17. NEW FILES CREATED

Production/tooling source: services/legacy_discovery.py.
Human-readable report: audit_codex_v3.md.
No new separate checklist/report is created; old checklists and audit v1/v2 remain untouched.

Raw synthetic/run evidence under .test_runtime includes runtime_results.json, integrity artifacts, legacy_review_synthetic.json, legacy_workflow_evidence.json, legacy_counts.json, legacy_attempts.json, aggregate production_legacy_inventory.json, independent_integrity.json, pwa_results.json/fixtures and git diff/status artifacts. These remain raw evidence, not substitute audit reports. No sensitive full production mapping file was generated.

# 18. REMAINING RISKS

Two production local files remain UNKNOWN and denied. Human-independent provenance review/final deny policy is not performed. No production activation path is enabled by this batch.

Real browser testing, production SW/client rollout and actual Nginx verification remain outstanding. Offline custodian key custody/authentication must be established before any later authorized operational review/apply. Discovery requires complete trusted/quiescent DB sources; active journals/changed sources deny rather than being ignored. Existing registered UNKNOWN/conflicting identities remain denied, with no overwrite/promotion recovery or implicit v2 migration.

SEC-01/02/06/07 remain OPEN; SEC-03 Drive ownership/rename remains incomplete. BUG-10 numeric validation and historical mobile/HARD findings are unchanged. No prior FIXED finding is reopened without regression evidence.

# 19. REMAINING WORK

P0: USER review final production legacy policy/evidence; independently authorize outstanding high-priority security findings.
P1: Separately authorized custodian evidence/operational approval and rollout/browser/Nginx verification; any future production activation requires explicit new USER authorization.
P2: Previously open numeric/mobile/HARD or unrelated work, only in separately authorized batches.

No remaining action is executed automatically.

# 20. SEC-04 STATUS

OPEN.

4B1/4B2/4B3/4B4/4B5A and resumed 4B5 tooling are COMPLETE. This does not establish an accepted final production legacy policy, verified/activated production mappings, real-browser rollout or live deployment evidence. Tooling PASS alone is not SEC-04 FIXED.

# 21. RECOMMENDED NEXT ACTION

USER review this audit and decide the final production policy/evidence requirement for the two UNKNOWN local files before authorizing any separate activation or rollout work. STOP; no next batch/apply is started.

# 22. AUDIT EVIDENCE

Final runtime result artifact = [runtime_results.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/runtime_results.json)
Fresh targeted/category aggregates = [legacy_counts.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/legacy_counts.json)
Raw deterministic candidate artifact = [legacy_review_synthetic.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/legacy_review_synthetic.json)
Synthetic approval/apply evidence = [legacy_workflow_evidence.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/legacy_workflow_evidence.json)
Production read-only aggregates = [production_legacy_inventory.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/production_legacy_inventory.json)
Harness production integrity = [integrity.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/integrity.json)
Independent pre-inventory/post-all-attempts integrity = [independent_integrity.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/independent_integrity.json)
Tested source hashes = [source_manifest.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/source_manifest.json)
PWA runtime/simulation = [pwa_results.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/pwa_results.json)
Repair history = [legacy_attempts.json](.test_runtime/run-44c3751cf1424f059f00b4305853ce0c/legacy_attempts.json)
Git diff/status = .test_runtime/run-44c3751cf1424f059f00b4305853ce0c/git_diff.patch; git_status_before_audit.txt; final status checked after this file creation.
Acceptance checklist = section10 of this file.
Central historical index = CODEX_AUDIT_FIX_LOG.md.
Historical immutable snapshots = audit_codex_v1.md; audit_codex_v2.md.

# 23. CONSISTENCY CHECK

PASS.

Fresh raw runtime, legacy_counts, integrity artifacts and current-source hashes agree:225/0 targeted,2396/2 full, all original groups passing, guards/provider0 and production unchanged. Central log's new concise entry references this v3 and the same counts; historical entries remain chronological evidence, not current test claims.

v1 records pre-implementation BLOCKED and historical4B4 results; v2 records resolved representation/4B5A234/0 and2171/2 full, with workflow not yet resumed at that date. v3 adds225 passing resumed workflow assertions; these are expected chronology/coverage differences, not contradictions.

A broad initial Core summary filter accidentally included the historical mobile dashboard FAIL. Explicit Core actor/route selection confirms32 PASS, while both mobile FAIL remain reported. This aggregation correction changed no runtime expectation.

Immutable previous hashes preserved:
audit_codex_v1.md = 77f8f639145ec5d528582c30b32da67e394d5699682d221998362466c72654e9
audit_codex_v2.md = 4b7bcd58a8eab62241bfe390995221cd04d794aa88e46f96c660143f9bf4f2f1

No unresolved consistency issue is identified. Old checklist hashes are unchanged; no duplicate checklist is created.

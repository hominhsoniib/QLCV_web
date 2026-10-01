# 1. AUDIT VERSION

AUDIT FILE = audit_codex_v2.md
CREATED = 2026-10-01T10:55:35+07:00
PROJECT ROOT = D:\App_Claude_Antigravity\QLCV_web
CURRENT BATCH = 4B5A ? Legacy Provenance Model

Exact root filename scan selected version 2; all prior versions remain immutable.

# 2. EXECUTIVE SUMMARY

4B5A COMPLETE for safe registry provenance infrastructure and synthetic validation.
The 4B5 uploader representation blocker is resolved without fabricating an uploader.
No production mapping/activation/migration occurred. SEC-04 remains OPEN; no unrelated
finding changed status. Fresh targeted234/0; full2171/2 with only historical mobile failures.

# 3. CURRENT PROJECT STATUS

Completed4B1/4B2/4B3/4B4/4B5A; SEC05 validation previously completed3D.
Original4B5 audit stopped before implementation; full4B5 workflow is NOT resumed.
Drive rename BLOCKED. BUG10 PARTIALLY FIXED (collision only; numeric validation open).
Production legacy activated0. Human review remains required; this model does not approve candidates.

# 4. CURRENT SECURITY STATUS

SEC01 OPEN; SEC02 OPEN; SEC03 PARTIALLY FIXED; SEC04 OPEN; SEC05 FIXED;
SEC06 OPEN; SEC07 OPEN. No prior fixed finding is reopened without evidence.
Known historical /mobile and /mobile/tasks500 remain. Actual Nginx, production-client
rollout not verified; real-browser PWA testing NOT RUN.

# 5. CURRENT BATCH RESULT

A. BATCH 4B5A COMPLETE = YES
B. IMPLEMENTATION PERFORMED = YES
C. ORIGINAL 4B5 BLOCKER = mandatory actual uploader incompatible with legacy unknown uploader.
D. ACTUAL HISTORICAL UPLOADER SOURCE = NOT FOUND in inspected source/schema; external archives not audited.
E. UPLOADER FABRICATED = NO
F. CHOSEN DESIGN = explicit v3 VERIFIED_UPLOADER / LEGACY_VERIFIED_MAPPING, conditional NULL uploader only for reviewed legacy.
G. ALTERNATIVES REJECTED = separate store increases identity/atomicity complexity; nullable-only/sentinel/reviewer-as-uploader mixes or fabricates identity.
H. NORMAL UPLOAD UPLOADER REQUIRED = YES
I. LEGACY UPLOADER REQUIRED = NO; stored NULL, not identity evidence.
J. LEGACY UPLOADER FALLBACK = DISABLED
K. LEGACY CREATION AUTHORITY = dedicated offline reviewed permit plus trusted exact revalidation, no HTTP route.
L. CLIENT CAN REQUEST LEGACY MODE = NO
M. LEGACY REQUIRES ACTIVE BINDING = YES
N. UNKNOWN DEFAULT DENY = PASS
O. ADMIN UNKNOWN BYPASS = BLOCKED
P. TENANT ISOLATION = PASS
Q. BACKWARD COMPATIBILITY = PASS with read-only v2 support and explicit mutation-upgrade gate.
R. SCHEMA/MODEL CHANGE = sidecar v3 with four provenance/review fields and conditional SQL constraints; no business schema.
S. PRODUCTION MIGRATION PERFORMED = NO
T. TARGETED 4B5A = 234 PASS / 0 FAIL; category table below.
U. 4B4 REGRESSION = 314 PASS / 0 FAIL
V. 4B3 REGRESSION = 531 PASS / 0 FAIL
W. 4B2 REGRESSION = 338 PASS / 0 FAIL
X. REGISTRY = 77 PASS / 0 FAIL
Y. SEC-05 = 530 PASS / 0 FAIL
Z. SEC-03 = 84 PASS / 0 FAIL
AA. BUG-10 = 13 PASS / 0 FAIL (collision only)
AB. FULL GUARDED SANDBOX = 2171 PASS / 2 historical mobile FAIL
AC. CORE = login/dashboard/tasks/logout PASS; routers11/11.
AD. MOBILE BASELINE = /mobile500; /mobile/tasks500.
AE. NEW REGRESSIONS = NONE
AF. PRODUCTION INTEGRITY = DB/data modified NO; registry/upload created NO; file moved NO; legacy activated NO.
AG. FILES CHANGED = services/file_registry.py; services/file_binding_service.py; services/file_access_service.py; services/legacy_provenance.py (new); tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; CODEX_AUDIT_FIX_LOG.md; CODEX_REVIEW_CHECKLIST_4B5A.md (new); audit_codex_v2.md (new)
AH. NEW FILES = services/legacy_provenance.py; CODEX_REVIEW_CHECKLIST_4B5A.md; audit_codex_v2.md.
AI. CHECKLIST = CODEX_REVIEW_CHECKLIST_4B5A.md PASS,30 acceptance items with stated evidence limits.
AJ. CENTRAL LOG UPDATED = YES
AK. SEC-04 STATUS = OPEN
AL. ORIGINAL 4B5 BLOCKER STATUS = RESOLVED (representation only)
AM. CAN 4B5 RESUME SAFELY = YES after USER review; not resumed here.
AN. REMAINING RISKS = full discovery/conflict/custodian workflow not built; v2 mutation upgrade separately required if encountered; browser/production rollout/Nginx live verification outstanding.
AO. RECOMMENDED NEXT ACTION = USER review4B5A before separate resumption of4B5 tooling.
AP. VERSIONED SUMMARY = audit_codex_v2.md; path D:\App_Claude_Antigravity\QLCV_web\audit_codex_v2.md; version2; previous versions preserved YES; consistency PASS.


# 6. FRESH TEST RESULTS

Fresh final run = .test_runtime\run-56914c095017492d97da57114b97fc2f

| Category | PASS | FAIL |
|---|---:|---:|
| PROVENANCE_MODEL | 5 | 0 |
| NORMAL_UPLOADER_REQUIRED | 4 | 0 |
| LEGACY_CREATION_AUTHORITY | 7 | 0 |
| LEGACY_NO_UPLOADER_FALLBACK | 10 | 0 |
| LEGACY_BINDING_REQUIRED | 8 | 0 |
| LEGACY_TASK_ACL | 16 | 0 |
| LEGACY_DOCUMENT_ACL | 10 | 0 |
| LEGACY_TENANT_ISOLATION | 7 | 0 |
| LEGACY_UNKNOWN_DENY | 9 | 0 |
| PROVENANCE_BACKWARD_COMPAT | 12 | 0 |
| PROVENANCE_MALFORMED_DENY | 12 | 0 |
| PROVENANCE_ATOMICITY | 5 | 0 |
| PROVENANCE_ATTACKS | 9 | 0 |
| PROVENANCE_PATH_INTEGRITY | 10 | 0 |
| PROVENANCE_PWA_INTEGRATION | 7 | 0 |
| PROVENANCE_ZERO_MUTATION | 103 | 0 |

TOTAL TARGETED4B5A =234/0.
Fresh PWA314/0; Gateway531/0;4B2338/0; Registry77/0;SEC05530/0;SEC0384/0;
BUG10collision13/0; full2171/2. complete=true, preflightPASS, guard violations[],
provider mutation count0. Only failures are the two mobile HTTP500 baseline checks.
New regressions NONE. Source manifest matches current tested production code.

Historical evidence: accepted4B4 run1937/2 is comparison only. First4B5A diagnostic
run-7c6418a4981a46179c23fb5c5c96e21f recorded2153/2 but was rejected by source-manifest
check after in-scope source/assertion strengthening; not final acceptance. Fresh rerun
above includes all strengthened assertions. No expected security behavior was weakened.

# 7. CORE APPLICATION STATUS

Fresh loginPASS; dashboardPASS; tasksPASS; logoutPASS; routers11/11.
/mobile500 and /mobile/tasks500 are actual FAILs matching historical baseline,
not passing mobile functionality. They were not fixed.

# 8. PRODUCTION INTEGRITY

PRODUCTION DB MODIFIED = NO
PRODUCTION DATA MODIFIED = NO
PRODUCTION REGISTRY CREATED = NO
PRODUCTION UPLOAD CREATED = NO
PRODUCTION FILE MOVED = NO
PRODUCTION LEGACY ACTIVATED = NO

Before/after protected SHA-256/size/mtime_ns unchanged; fresh integrity.json agrees.
No production startup, migration, provider requests, package install or physical-file writes.
Production default private_metadata/file_registry.sqlite3 remains absent.
Source changes are separately listed, not classified as production-data mutation.

# 9. FILES CHANGED BY CURRENT BATCH

CURRENT BATCH CHANGES = services/file_registry.py; services/file_binding_service.py; services/file_access_service.py; services/legacy_provenance.py (new); tests/runtime_sandbox.py; tests/RUNTIME_SANDBOX.md; CODEX_AUDIT_FIX_LOG.md; CODEX_REVIEW_CHECKLIST_4B5A.md (new); audit_codex_v2.md (new)

PRE-EXISTING WORKING TREE: tracked15 files+336/-306 remain earlier/user work:
deployment guide,app.py,chay_app.bat,config.py,deploy_vps.sh,main_launcher.py,
nginx_vps_default.conf,routes/documents.py,routes/tasks.py,run_vps.bat,
services/drive_service.py,services/task_service.py,templates/help_guide.html,
templates/layout.html,vps_default.conf. Existing untracked tests/services/mobile/PWA/
VPS/history artifacts predate this batch. Because current modules/tests/docs are
untracked, tracked diff-stat does not measure current-batch changes.
Against accepted4B4 source manifest only registry/binding/access existing modules changed;
new legacy module added. Task policy, business routes, upload service, SW/static/app/config
and deployment unchanged. Per-module no-index diff reviewed against4B4 snapshot.

# 10. NEW FILES CREATED

services/legacy_provenance.py
CODEX_REVIEW_CHECKLIST_4B5A.md
audit_codex_v2.md

# 11. LEGACY PROVENANCE STATUS

Actual historical uploader NOT FOUND in inspected source/data structures. Editable
Task/Document/Personal references, roles and AuditLog are not immutable upload proof.
NEW flow retains real signed-session uploader, WRITING->UNBOUND and24h uploader policy.

Chosen explicit provenance on one v3 files record: VERIFIED_UPLOADER keeps uploader
mandatory; LEGACY_VERIFIED_MAPPING has NULL uploader, separate review ID/reviewer/evidence
digest, VERIFIED_LEGACY classification and only BOUND/REVOKED states. SQL constraints
and registry/gateway validation fail closed on malformed/null/unknown/case-alias provenance.
Only offline explicit digest-bound reviewed permit may request legacy identity; normal
registration/API flags cannot. No dedicated legacy route or app-startup behavior exists.
Reviewer is not uploader; legacy has no UNBOUND/uploader fallback. An ACTIVE binding alone
still never authorizes: same tenant, supported Task/Document slot, live object, exact current
field, existing live READ ACL, confined actual size/hash are required. UNKNOWN remains denied.

Atomic sidecar apply creates identity and all bindings in one BEGIN IMMEDIATE transaction;
pre/post exact revalidation callback plus physical verification; any error rolls back all.
No business mutation occurs. Future trusted offline tooling must authenticate custodian,
verify independent evidence and full reference/conflict inventory. This API is not isolation
against privileged Python code already able to write SQLite.

v2 valid normal reads deterministically retain VERIFIED_UPLOADER semantics without mutation.
Ambiguous/malformed v2 denies. v2 mutations/implicit upgrades explicitly refused; no migration
helper/production migration. Existing v2 deployments need separately reviewed upgrade before
mutation. Production registry absent. No production inventory/candidates/apply performed.

Alternatives rejected: separate store expands identity/locator/FK/atomicity coordination;
nullable-only or sentinel/reviewer identity fabricates or mixes provenance. Explicit four
fields on existing sidecar is the smallest model allowing one transaction and validation.

# 12. CHECKLIST STATUS

CODEX_REVIEW_CHECKLIST_4B5A.md:30 applicable acceptance items PASS;0FAIL;0NOT RUN;
0NOT FULLY TESTABLE for listed items with evidence limitations documented. Model batch
acceptance PASS, USER review pending. Real-browser test NOT RUN, production client/Nginx
NOT VERIFIED; synthetic Node evidence is not real-browser PASS. Original representation
blocker resolved; full4B5 review/discovery tooling remains future work.

# 13. REMAINING RISKS

SEC01/02/06/07 OPEN, SEC03 Drive ownership incomplete, SEC04 full verified legacy workflow
and accepted production final policy unresolved. Real browser/client rollout/Nginx verification
outstanding. Any existingv2 mutation requires an explicit upgrade before use. Privileged
administrative tooling must validate custodian and evidence; review strings alone are not
provenance from an untrusted client. Normal upload/client authority was not expanded.

# 14. REMAINING WORK

P0: review4B5A then separately resume safe discovery/conflict/custodian workflow; approve
final production legacy verified/deny policy and rollout; separately schedule other open P0s.
P1: approved real-browser/production-client/deployment verification and sidecar upgrade plan if needed.
P2: separately authorized mobile baseline and outstanding numeric-validation work. None auto-started.

# 15. RECOMMENDED NEXT ACTION

USER review4B5A before separately authorizing resumed4B5 tooling; no production apply.

# 16. AUDIT EVIDENCE

Fresh runtime = .test_runtime\run-56914c095017492d97da57114b97fc2f/runtime_results.json
Integrity = same run/integrity.json + integrity_before.json
Isolation = same run/preflight.json
Source = same run/source_manifest.json (all digests current)
SW simulation = same run/pwa_results.json + actual synthetic gateway fixtures
Checklist = CODEX_REVIEW_CHECKLIST_4B5A.md
Central log = CODEX_AUDIT_FIX_LOG.md dated4B5A section/current completed-phase note
Git diff check = PASS (existing CRLF notices only); current modules separately compared against4B4 snapshot
Source proof = registryv3 conditional provenance constraints, legacy offline primitive,
access valid_provenance/UNBOUND gate and unchanged task_policy/Document READ.
Historical immutable audit_codex_v1.md SHA256 = 77f8f639145ec5d528582c30b32da67e394d5699682d221998362466c72654e9

CONSISTENCY CHECK = PASS. Current source/schema3, fresh counts, checklist and latest log
section agree. Earlier log/schema2/not-started counts are explicitly historical; 4B5 audit
BLOCKED record remains historical, representation now resolved by4B5A. No4B5 full workflow
completion or production approval is inferred. No fresh4B5A evidence is replaced with1937/2.

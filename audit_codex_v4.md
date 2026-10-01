# 1. AUDIT VERSION

AUDIT FILE = audit_codex_v4.md
CREATED = 2026-10-01
PROJECT ROOT = D:\App_Claude_Antigravity\QLCV_web
CURRENT BATCH = SEC-01 master identity escalation
VERSION = 4
PREVIOUS VERSIONS PRESERVED = YES

Exact root filename scan found v1/v2/v3. This new snapshot does not replace prior versions or historical checklists.

# 2. EXECUTIVE SUMMARY

BATCH STATUS = BLOCKED before implementation. SEC-01 remains OPEN.
Current source structurally proves reserved-ID escalation and shared master-credential control by tenant employee managers. Completing the fix requires a decision about protecting MASTER identity from default-tenant ADMIN/CEO employee-management permissions. The prompt explicitly lists changing tenant business authorization as a STOP CONDITION.

Production code modified = NO. Targeted tests and full sandbox = NOT RUN. No fresh runtime regression conclusion is claimed. Fresh protected-data integrity comparison PASS. Production legacy activated = 0.

# 3. CURRENT PROJECT STATUS

4B1/4B2/4B3/4B4/4B5A and resumed 4B5 tooling remain COMPLETE (historical v3).
SEC-01 implementation is blocked; no other batch started.
Two production UNKNOWN files remain denied; no final production legacy policy/activation authorized.
Historical mobile HTTP 500/500, Drive rename blocked, BUG-10 numeric validation open.
Real-browser PWA test NOT RUN; production client rollout and actual Nginx NOT VERIFIED.

# 4. CURRENT SECURITY STATUS

| Finding | Status |
|---|---|
| SEC-01 | OPEN: source-confirmed, fix blocked |
| SEC-02 | OPEN |
| SEC-03 | PARTIALLY FIXED |
| SEC-04 | OPEN |
| SEC-05 | FIXED |
| SEC-06 | OPEN |
| SEC-07 | OPEN |

Other statuses retained from v3; this audit does not reopen an accepted fixed finding or claim fresh regression validation.

# 5. SEC-01 ORIGINAL FINDING

Historical log line89 identifies default-tenant reserved employee IDs granting master identity, with no reservation in employee creation. Current source still contains that mechanism. Escalation is conditional on default-tenant employee-management access or an existing reserved account; this audit does not assert such an attacker exists in production.

# 6. CURRENT IDENTITY ARCHITECTURE

Authentication verifies Employee.mat_khau in a selected tenant database. Employee.ma_nv is the tenant-local stable primary key; email is unique only inside that tenant. Numeric-ID collisions correspond to tenant-local employee-code collisions; there is no independent numeric MASTER identity.

Master DB contains MasterCompany and GlobalUserIndex, not an independent MasterUser credential source (models/master_models.py:9,26). Default tenant 0312345678/default maps to qlcv.db (database/multi_tenant.py:33). The MASTER designation is derived from selected tenant plus employee code.

AuthService.check_login strips input, uppercases employee code/lowercases email, resolves explicit MST or global index, then first Employee match. Invalid explicit company falls back to first MasterCompany; missing company can default to 0312345678. Prefix email matching, email-local-part fallback and first-match behavior make ambiguous resolution structurally unsafe. These adjacent SEC-07 patterns are documented, not fixed.

routes/auth.py:151-158 signs ma, ten, role, email, company_mst, company_name and is_master_admin. No explicit principal scope/original authority accompanies the flag. Display fields are not independent privilege evidence. Browser form/JSON does not directly set master flag in this login handler; the server computes it incorrectly from mutable tenant records. A signed-cookie secret compromise is not assumed.

AuthService.get_session:240-249 verifies the signature and defaults missing tenant to the default company. database/connection.py then chooses tenant DB from that context. routes/companies.py:299-322 switches master context, retaining true master flag but replacing ma/role with ADMIN and tenant with the target; original authenticated identity is not retained. Logout deletes the cookie; copied-cookie revocation belongs to SEC-02 and is not claimed here.

# 7. ROOT CAUSE

1. services/auth_service.py:123 grants is_master_admin for default-tenant ma_nv ADMIN, SUPERADMIN or ROOT regardless of actual role. The redundant role clause does not restrict the first condition.
2. routes/master.py:121-138 permits tenant ADMIN/CEO Employee creation/update. services/employee_service.py:54-85 accepts caller-selected employee code and role without reserving MASTER identities.
3. services/employee_service.py:100-128 allows those managers to replace an existing employee password and role, including default ADMIN. This same credential becomes MASTER at login.
4. routes/companies.py:22-44 trusts the signed boolean instead of a protected, authoritative MASTER principal.

Adding scoped signed identity or removing ROOT/SUPERADMIN alone cannot prevent takeover of default ADMIN through the existing tenant-management permission. Password validity then proves possession of a tenant-manager-replaced credential, not independent MASTER authority.

STOP CONDITION = safe fix requires changing tenant business authorization (user section24).
WHY CURRENT SCOPE IS INSUFFICIENT = preserving current default-tenant ADMIN/CEO authority over all Employee credentials leaves MASTER credential creation/reset under that authority.
REQUIRED USER DECISION = explicitly authorize a narrowly protected MASTER-account management boundary, including which principals may create/change the master credential and role.
FILES/POLICY REQUIRING APPROVAL = routes/master.py and services/employee_service.py target-account authorization, coordinated with scoped authentication in services/auth_service.py, routes/auth.py and routes/companies.py. A separate MASTER credential store is an alternative requiring its own source/bootstrap/schema decision; no schema change is proposed as already approved.

# 8. EXPLOIT / UNSAFE PATTERN REPRODUCTION

CURRENT-SOURCE STRUCTURAL PROOF = CONFIRMED.
RUNTIME EXPLOIT REPRODUCTION = NOT RUN.

Source path A: default-tenant ADMIN/CEO invokes POST /api/employees with maNV=ROOT and quyen=USER, valid password; creation accepts it; login verifies that account and computes is_master_admin=true; companies guard accepts it.
Source path B: default-tenant CEO/other ADMIN invokes POST /api/employees/update targeting ADMIN with a replacement password; update commits it; subsequent valid-password login gets MASTER flag; companies guard accepts it.

PRE-FIX VULNERABLE BEHAVIOR = tenant-managed reserved identity can satisfy master guard.
REQUIRED POST-FIX EXPECTATION = DENY tenant-to-MASTER escalation, including both creation and credential-replacement paths.
No production user data or actual exploit execution is used. No regression test is falsely claimed to exist.

# 9. FIX IMPLEMENTED

NO. Mandatory scope STOP reached before production or test-code changes.
No partial security fix is installed or labeled complete. A reserved-name-only patch would leave path B open. Scoped sessions alone would sign the same mutable credential-derived authority.
No password reset, session invalidation, new identity provider, business migration or production rollout performed.

# 10. MASTER IDENTITY INVARIANT

Required: only a principal authenticated against a protected authoritative MASTER source satisfies master guard.
Current source does not establish this: authority and credential mutation share tenant Employee management. Explicit authenticated origin/scope plus protected credential authority are both needed; role ADMIN alone is insufficient.

# 11. TENANT IDENTITY INVARIANT

Required: tenant principal cannot change into MASTER because of employee-code/email collision, role, omitted tenant or switched context.
Current source fails the reserved default-tenant identity case. Global lookup fallback and missing-company default need coordinated identity-boundary treatment without silently closing SEC-07 or redesigning SEC-02.

# 12. MASTER-ONLY ROUTE AUDIT

| Operation | Authentication | Scope/role/tenant check | Failure |
|---|---|---|---|
| GET /master/companies | Signed session | Truthy is_master_admin; no authoritative principal check | Login/dashboard redirect |
| GET /api/companies/list | Signed session | Shared check_master_system_admin boolean | 401/403 |
| POST /api/companies/create | Same | Same | 401/403 |
| POST /api/companies/update | Same | Same | 401/403 |
| POST /api/companies/add-employee | Same | Same | 401/403 |
| POST /api/companies/toggle-status | Same | Same | 401/403 |
| POST /api/companies/delete | Same | Same | 401/403 |
| POST /api/companies/switch-tenant | Same | Same; signs ADMIN target context with master flag | 401/403 |

routes/master.py manages tenant departments/employees, despite its name; it is not an independently authenticated MASTER source. Its existing ADMIN/CEO authorization is the blocker dependency, not a newly authorized business policy.
Search of Core routes/services/app/database/models found master flag production reads/writes only in auth_service.py, routes/auth.py and routes/companies.py. No universal new MASTER business ACL is introduced.

# 13. ACCEPTANCE CHECKLIST

PASS here identifies source-audit or fresh integrity evidence only; it never substitutes for runtime validation.

- **authoritative MASTER source identified**: STATUS = PASS. EVIDENCE = auth_service.py:123: default-tenant Employee credential; master_models.py has no MasterUser.

- **authoritative TENANT source identified**: STATUS = PASS. EVIDENCE = Employee in get_tenant_session(company_mst), auth_service.py:77-89.

- **master principal unambiguous**: STATUS = FAIL. EVIDENCE = Reserved ma_nv alone grants master; no separately protected master credential.

- **tenant principal unambiguous**: STATUS = FAIL. EVIDENCE = Prefix/first-match/default-tenant fallback remain; no explicit authenticated principal scope.

- **tenant ADMIN != MASTER**: STATUS = FAIL. EVIDENCE = Default-tenant employee management can create reserved IDs or replace ADMIN credential.

- **username collision denied safely**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **email collision denied safely**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **ID collision denied safely**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **ambiguous lookup fails closed**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **malformed identity fails closed**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **tenant switch cannot escalate**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **client cannot forge MASTER scope**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **logout clears privileged identity**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **master-only routes require actual master principal**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **tenant isolation preserved**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **SEC-01 exploit regression test exists**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **targeted SEC-01 PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **resumed 4B5 regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **4B5A regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **PWA regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **Gateway regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **4B2 regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **Registry regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **SEC-05 regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **SEC-03 regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **BUG-10 regression PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **Core smoke PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **11 routers PASS**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **mobile baseline unchanged**: STATUS = NOT RUN. EVIDENCE = No fresh runtime tests: mandatory scope STOP before implementation. Source findings and historical v3 results are separately documented.

- **production integrity PASS**: STATUS = PASS. EVIDENCE = Fresh .test_runtime/audit-sec01-blocked/integrity.json: SHA-256/size/mtime_ns before=after for all 10 protected entries.

- **production legacy activated = 0**: STATUS = PASS. EVIDENCE = Production sidecar remains absent; no apply, DB write or production startup executed.

# 14. TARGETED SEC-01 TEST RESULTS

All seventeen requested categories = NOT RUN:
SEC01_IDENTITY_MODEL, SEC01_MASTER_AUTHENTICATION, SEC01_TENANT_AUTHENTICATION, SEC01_DUPLICATE_USERNAME, SEC01_DUPLICATE_EMAIL, SEC01_ID_COLLISION, SEC01_MASTER_ROUTE_GUARD, SEC01_TENANT_ADMIN_ISOLATION, SEC01_TENANT_SWITCH, SEC01_SESSION_SCOPE, SEC01_MALFORMED_IDENTITY, SEC01_AMBIGUOUS_LOOKUP_DENY, SEC01_LOGOUT, SEC01_CROSS_TENANT, SEC01_ATTACK_MATRIX, SEC01_BACKWARD_COMPAT, SEC01_ZERO_PRODUCTION_MUTATION.
TOTAL TARGETED SEC-01 = NOT RUN, not 0/0 PASS.

# 15. REGRESSION RESULTS

Fresh SEC-01 batch regressions = NOT RUN; implementation was stopped.
Historical accepted v3 comparison only:

| Group | PASS | FAIL |
|---|---:|---:|
| Resumed 4B5 | 225 | 0 |
| 4B5A | 234 | 0 |
| PWA | 314 | 0 |
| Gateway | 531 | 0 |
| 4B2 | 338 | 0 |
| Registry | 77 | 0 |
| SEC-05 | 530 | 0 |
| SEC-03 | 84 | 0 |
| BUG-10 collision | 13 | 0 |

# 16. FULL GUARDED SANDBOX

Fresh run = NOT RUN. No runtime_results.json is overwritten or fabricated.
Latest historical completed run = .test_runtime/run-44c3751cf1424f059f00b4305853ce0c.
Historical complete=true;2396 PASS/2 FAIL; unexpected guards=[]; provider mutations=0; source match/integrity PASS at that run.
NEW REGRESSION = NOT ASSESSED by fresh runtime; no production/test source changed in this batch.

# 17. CORE APPLICATION STATUS

Fresh login/dashboard/tasks/logout/routers/mobile checks = NOT RUN.
Historical v3: login/dashboard/tasks/logout PASS; routers11/11.
Historical /mobile=500; /mobile/tasks=500. No mobile repair performed.

# 18. PRODUCTION INTEGRITY

Fresh SHA-256/size/mtime_ns snapshots compare equal across all 10 protected production entries.
PRODUCTION MASTER DB MODIFIED = NO
PRODUCTION TENANT DB MODIFIED = NO
PRODUCTION DATA MODIFIED = NO
PRODUCTION REGISTRY CREATED = NO
PRODUCTION UPLOAD MODIFIED = NO
PRODUCTION LEGACY ACTIVATED = NO
Production files moved/deleted/created = NO.
Production registry existence check = absent. No SQL writes, app import/startup, seed, migration or provider requests executed.
Evidence = .test_runtime/audit-sec01-blocked/integrity.json. Hash/metadata inspection is read-only; sensitive names/data are not listed in this report.

# 19. FILES CHANGED BY CURRENT BATCH

CURRENT BATCH CHANGES: CODEX_AUDIT_FIX_LOG.md (concise blocked entry); audit_codex_v4.md (new); raw .test_runtime/audit-sec01-blocked/integrity.json.
Production/test code changed = NONE.

PRE-EXISTING WORKING TREE CHANGES:15 tracked files,+336/-306:
HUONG_DAN_DEPLOY_CLOUD_VPS.md;app.py;chay_app.bat;config.py;deploy_vps.sh;main_launcher.py;nginx_vps_default.conf;routes/documents.py;routes/tasks.py;run_vps.bat;services/drive_service.py;services/task_service.py;templates/help_guide.html;templates/layout.html;vps_default.conf.
Prior untracked work includes auditv1-v3, historical checklists/log, tests/runtime artifacts, registry/binding/access/task policy/legacy modules, mobile/PWA files and guidance. None is attributed to SEC-01.

# 20. NEW FILES CREATED

audit_codex_v4.md.
.test_runtime/audit-sec01-blocked/integrity.json (raw audit evidence; not a fresh sandbox run).
No separate checklist or duplicate human-readable report.

# 21. REMAINING RISKS

SEC-01 reserved-ID and credential takeover remain structurally open. No claim that current production attackers or reserved accounts were enumerated.
Other SEC findings, historical mobile failures, numeric validation, browser/client/Nginx evidence and final UNKNOWN policy remain as in v3. No production legacy files activated.

# 22. REMAINING WORK

P0: decide protected MASTER credential management boundary, then separately resume SEC-01 implementation and all requested attack/regression tests.
P1/P2: previously open findings/rollout/legacy/mobile work remain separately authorized work; none executed here.

# 23. SEC-01 STATUS

OPEN. Root cause structurally proven; fix and fresh targeted/security regression evidence absent because the defined authorization STOP applies.
BATCH COMPLETE = BLOCKED, not FIXED or PARTIALLY FIXED.

# 24. OTHER SECURITY FINDINGS STATUS

SEC-02 OPEN;SEC-03 PARTIALLY FIXED;SEC-04 OPEN;SEC-05 FIXED;SEC-06 OPEN;SEC-07 OPEN.
No modifications or new closure claims. Production UNKNOWN activation remains0.

# 25. RECOMMENDED NEXT ACTION

USER explicitly authorize the narrow MASTER credential-management protection policy for the default tenant before resuming SEC-01; specify that tenant ADMIN/CEO cannot create/reset/promote MASTER principals through ordinary Employee management.

# 26. AUDIT EVIDENCE

Current source references: auth_service.py:41-85,123,240-249; routes/auth.py:151-160; routes/master.py:121-138; employee_service.py:54-85,100-128; routes/companies.py:22-44,299-322; models/master_models.py; database/connection.py; database/multi_tenant.py.
Raw fresh audit integrity/source/history hashes = .test_runtime/audit-sec01-blocked/integrity.json.
Historical runtime_results.json/integrity.json = .test_runtime/run-44c3751cf1424f059f00b4305853ce0c.
Historical snapshots = audit_codex_v1.md,v2.md,v3.md (preserved).
Historical index = CODEX_AUDIT_FIX_LOG.md.
git status/diff/stat inspected; git diff --check PASS, with existing LF/CRLF notices. Python syntax validation not applicable: no Python changed.

# 27. CONSISTENCY CHECK

Historical v3 results are explicitly historical, not fresh SEC-01 tests. Current source still supports log SEC-01 OPEN. Fresh integrity comparison agrees with no production modification.
Historical log SEC-04 table retains earlier 4B4 wording; later resumed4B5/v3 entry is the accepted chronological update. SEC-04 remains OPEN in both; no historical row rewritten.
No runtime-results count is attributed to this blocked batch. Audit/log both record BLOCKED, no implementation/tests, integrity PASS.
Prior v1/v2/v3 and checklist hashes are retained in the raw source/history fingerprint artifact and unchanged. The v3 SHA-256 is 142f00a8b95531b0ec4e351b4edb94c6884ac70ea4f86d4f2006e5564fdea34b.
CONSISTENCY CHECK = PASS with stated historical/fresh limits.


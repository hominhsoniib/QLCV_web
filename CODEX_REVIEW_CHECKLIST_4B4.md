# CODEX REVIEW CHECKLIST — Batch 4B4 / SEC-04

Updated: 2026-10-01 08:07 +07:00 (Asia/Ho_Chi_Minh).
Historical4B2/4B3 checklists are unchanged. USER final review remains pending.
This checklist maps evidence; it is not a substitute for fresh reports.

## Review evidence record

- Scope: USER-authorized PWA/private Cache API protection only.4B5 NOT STARTED.
- Production changed: static/sw.js only; no app/gateway/registry/session/manifest/template edits.
- Test/doc changes: tests/runtime_sandbox.py, tests/RUNTIME_SANDBOX.md,
  CODEX_AUDIT_FIX_LOG.md; this NEW checklist.
- Old/new cache: qlcv-mobile-v1 -> qlcv-mobile-v2.
- Current standalone target: .test_runtime/run-dc034ef6f4834d80a352031dd0c92f81/,
  actual SW Node VM with synthetic CacheStorage/fetch:244 PASS/0 FAIL.
- Final full fresh run (R): .test_runtime/run-7b3e6a1e3b29440fb38ff3a24dfc2c5d/.
- R/runtime_results.json complete=true:1937 PASS/2 FAIL;4B4 targeted314/0.
- Evidence read: runtime_results.json, pwa_results.json, pwa_gateway_fixtures.json,
  preflight.json, integrity.json and source_manifest.json (includes SW).
- Only FAIL: /mobile500 and /mobile/tasks500 expected200, reproduced historical baseline.
- No new regression; no guard violation; provider mutation count0; Core11/11.
- Protected production DB/data SHA-256/size/mtime_ns unchanged; registry/upload createdNO.
- STATIC SOURCE VALIDATION: PASS (Node syntax, Python AST, manual source review).
- DETERMINISTIC SW LOGIC TEST: PASS (actual SW executed by Node22 VM).
- SIMULATED CACHE LIFECYCLE TEST: PASS (synthetic install/activate/fetch events/CacheStorage).
- ACTUAL SYNTHETIC GATEWAY + SW REPLAY: PASS;9 real sandbox gateway response fixtures,
  no cookies/provider/production data. This is not real-browser end-to-end verification.
- REAL BROWSER TEST: NOT RUN. Browser automation modules unavailable; no package installed.
- PRODUCTION CLIENT VERIFIED: NOT VERIFIED; no deployment/cache/profile operations.
- Acceptance: PASS for applicable source/simulated runtime criteria, USER review pending.

## Acceptance checklist

Runtime evidence below is SIMULATED unless explicitly described as live synthetic FastAPI.
R categories are exact prefixes in runtime_results.json. Every criterion has a status/evidence.

| Criterion | STATUS | EVIDENCE |
| --- | --- | --- |
| Current SW architecture audited | PASS | SOURCE: one /sw.js registration in mobile layout; root scope, authoritative static/sw.js; whole source search found no alternate active worker |
| Private namespace defined | PASS | PWA_PRIVATE_CLASSIFICATION parsed same-origin pathname /static/uploads, encoding/case/separator aliases; query/fragment/lookalike distinctions |
| Private classification before generic cache lookup | PASS | PWA_NO_PRIVATE_WRITE private request Cache API operation count0; source early branch before public strategy |
| Private network-only | PASS | PWA_NETWORK_ONLY one fetch, cache:no-store, gateway status/body preserved |
| No private cache.match | PASS | PWA_NO_PRIVATE_WRITE Cache API count0 for each private request, including deliberately reinserted old entries |
| No private cache.put | PASS | PWA_NO_PRIVATE_WRITE online success/denial/5xx and unsafe public-response exclusion |
| No private cache.add/addAll | PASS | Install public-only list + no add/addAll instrumentation; private paths have no Cache API calls |
| No private offline fallback | PASS | PWA_OFFLINE_PRIVATE rejects offline, logout, user/tenant switch and aliases despite stored private bytes |
| Old private cache entries purged | PASS | PWA_OLD_CACHE_PURGE distinct file A/B and aliases across v0/v1/v2/v12 removed; no private body read during purge |
| Cleanup limited to app-owned caches | PASS | Exact ^qlcv-mobile-v[0-9]+$ namespace; unrelated/near-prefix third-party caches unchanged |
| Cache version updated | PASS | PWA_CACHE_VERSION v2, skipWaiting install completion and claim after activation purge |
| Public cache preserved | PASS | PWA_PUBLIC_CACHE safe CSS/JS/manifest/other public entries migrated; public offline JS works |
| Cross-origin behavior safe | PASS | PWA_CROSS_ORIGIN no SW interception/Cache API; app-owned historical cross-origin entries purged only there |
| GET private safe | PASS | PWA_NETWORK_ONLY success/401/403/404/500; actual synthetic gateway replay |
| HEAD private safe | PASS | PWA_METHODS + PWA_4B3_INTEGRATION actual protected HEAD response, no Cache API |
| POST/PUT/PATCH/DELETE/OPTIONS safe | PASS | PWA_METHODS original methods forwarded, private Cache API count0; public strategy never caches mutations |
| Range private safe | PASS | PWA_METHODS exact Range header preserved + PWA_4B3_INTEGRATION actual206 replay without cache |
| Conditional private safe | PASS | PWA_METHODS If-None-Match forwarded + actual304 gateway replay without cache |
| Anonymous cannot receive cached private bytes | PASS | PWA_NETWORK_ONLY401 + live synthetic gateway401 replay, no cache fallback |
| Unauthorized cannot receive cached private bytes | PASS | PWA_NETWORK_ONLY403/404 + actual same-tenant unauthorized404 replay |
| UNKNOWN cannot receive cached private bytes | PASS | PWA_NETWORK_ONLY UNKNOWN404 simulation + gateway531 regression UNKNOWN denial unchanged |
| Unregistered cannot receive cached private bytes | PASS | Actual synthetic unregistered404 fixture replay + private cache operation count0 |
| Tenant/user switch cannot receive old cached bytes | PASS | PWA_NETWORK_ONLY switched identities/statuses and offline failures; actual foreign-tenant404 fixture |
| Logout has no Cache API private fallback | PASS | PWA_OFFLINE_PRIVATE + PWA_4B3_INTEGRATION logout401; no logout/session architecture change |
| Authenticated HTML/API precache/fallback removed | PASS | /mobile removed from install list; old mobile/API app entries purged; dynamic requests network-only, never mobile HTML fallback |
| Server no-store confirmed | PASS | PWA_4B3_INTEGRATION live gateway headers and gateway531 all private header checks preserved |
|4B3 gateway regression | PASS | Current531/0, including parent/direct static exclusion, ACL/tenant/live object/hash/HTTP/fail-closed/zero-mutation |
|4B2 regression | PASS | Current338/0 |
| Registry foundation | PASS | Current77/0; no schema change |
| SEC05 | PASS | Current530/0; no policy change |
| SEC03 | PASS | Current84/0; Drive rename remains fail-closed |
| BUG10 collision | PASS | Current13/0; numeric validation remains outside scope |
| Core smoke | PASS | Current login/dashboard/tasks/logout all PASS |
|11 routers | PASS | preflight/runtime auth/tasks/master/companies/documents/personal/ai/processes/jds/org_chart/mobile11/11 |
| Mobile baseline unchanged | PASS | Only /mobile500 and /mobile/tasks500 expected200; historical bugs NOT FIXED |
| Zero mutation | PASS | PWA_ZERO_MUTATION live synthetic DB/registry/uploads/provider + protected production comparison |
| Production integrity clean | PASS | R/integrity before==after; across-batch10 protected fingerprint equality; production registry/upload absent |
| Real-browser status explicitly stated | NOT RUN | Actual SW in Node VM is not a real browser ServiceWorker/CacheStorage engine; no packages installed |
| Production client activation verified | NOT RUN | No production deployment/client/profile inspected or changed |
| SEC04 remains OPEN | PASS | Central log status OPEN; legacy verified resolution remains |
|4B5 NOT STARTED | PASS | No legacy scan/register/claim/mapping/SQL or physical migration |

## Current targeted results

| Category | PASS | FAIL |
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
| TOTAL | 314 | 0 |

## Attempts / review limitations

- Standalone239/0 then240/0 after header-forwarding coverage; first full
  run-cd82033620e84a3bae56f37fa7b1647a targeted310/0, full1933/2.
- Final fixture review added distinct private file B (no production code or expected
  result change); standalone244/0, fresh final R targeted314/0/full1937/2.
- No assertion FAIL was hidden, skipped or weakened. No new regression.
- Applicable simulated checks PASS, but real browser/production client lifecycle is
  NOT VERIFIED. Guarantee begins after updated SW activation; old clients, update
  timing/in-flight old workers and real CacheStorage durability need rollout testing.
- This does not revoke copied sessions, remove downloaded/memory-resident files or
  clear unrelated third-party caches. Existing session/tenant findings remain open.
- Missing manifest icons remain existing HARD03; no mobile/session/PWA redesign.
- No deploy/restart/Nginx/firewall/package/database/schema/commit/destructive Git operation.
- STOP after USER review handoff; do not start4B5 automatically.

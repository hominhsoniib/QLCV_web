# QLCV Batch 1 runtime sandbox

Run from the project root using the existing project environment:

```powershell
.\venv\Scripts\python.exe -B tests/runtime_sandbox.py
```

The global Python installation is not the supported runner: it lacks Markdown
and has an incompatible optional Google/OpenSSL stack. No packages are installed.

Each run creates a new `.test_runtime/run-<id>/`. No cleanup is performed.
Core Python, templates and public static assets are copied from the current
working tree, preserving uncommitted changes. CRM Python/templates and QuoteFlow
are not copied. Production databases, uploads, seed.xlsx, .env, credentials and
user data are never copied. SQLite schemas and actors are synthetic.

## Safety map

| Production coupling | Sandbox resolution |
| --- | --- |
| config.py DATABASE_URL / connection.engine | Explicit sandbox app/qlcv.db |
| multi_tenant.py master path based on __file__ | Copied app/database/master_system.db |
| default tenant hard-coded qlcv.db based on __file__ | Copied app/qlcv.db |
| tenant paths based on __file__ | Copied app/database/tenants/*.db |
| get_db -> signed cookie -> get_tenant_session | Original Core flow, guarded sandbox engines |
| app startup create_all/ALTER/master sync | Original startup, sandbox only |
| startup seed.xlsx | Not copied; original missing-seed branch runs in sandbox |
| static/uploads and Config.UPLOAD_DIR | Copied app/static/uploads, initially empty |
| LOCAL_DOCS_DIR | Disabled |
| dotenv / provider credentials | dotenv disabled; ephemeral test secret, missing credentials |
| Drive / paid AI / email / HTTP | Provider stubs plus network/process guard |

Before FastAPI lifespan starts, all default/master/sample tenant engine paths and
all 11 registered Core routers are checked. SQLAlchemy URLs and sqlite3 connects
must resolve inside this run. SQLite URI URLs and ATTACH (including VACUUM INTO)
are denied. Write-open, mkdir, rename, remove, chmod and utime outside the run
are blocked by Python audit hooks. Resolver paths are additionally checked.
Expected denial probes verify production DBs, traversal, direct SQLite, file
write, network and ATTACH. Unexpected guard events fail the harness.

Network is blocked, including localhost application services. The sole exception
is the thread-local internal loopback socket pair required by Windows asyncio;
it is allowed only during the standard socketpair call. No listener/server is
started for the application; requests use in-process TestClient.

These are test-process guards for trusted application code, not an OS security
boundary against malicious native extensions. Do not run arbitrary scripts or
invoke production app directly. Tests must run inside the guarded worker.

## Fixtures and baseline

Company A: 9000000001. Company B: 9000000002.
Each has ADMIN, MANAGER and USER with unique emails at sandbox.invalid.
Each Task has ADMIN as assigner, USER as receiver, MANAGER as collaborator.
A separate synthetic ADMIN in the default sandbox tenant exercises the existing
master identity behavior; no production identity is used. Passwords and signing
secret are random per process, never printed or persisted in reports.

Smoke tests cover login, dashboard, tasks page, logout and cleared browser session.
The baseline matrix covers own/cross-tenant Task visibility, USER/MANAGER master
operation denial, anonymous tasks/upload and mobile pages. These are selected
baseline cases, not proof that all audited security findings are absent.

`runtime_results.json` records expected versus actual behavior; existing security
and mobile failures are retained. Baseline failures do not make process exit
nonzero. Isolation/harness failures do. `integrity.json` records SHA-256, size and
mtime before/after for production DBs and sidecars, uploads, .env, companies.json
and seed.xlsx. Any change stops the runner, with no rollback. Reports do not
contain secrets or production record contents. `source_manifest.json` identifies
the Core Python snapshot. All generated artifacts are ignored by Git.

For later batches, rerun after source edits to obtain a fresh source snapshot.
Do not reuse an old run as evidence for newly edited code. Batch 1 does not change
production resolvers, policies or business logic.

## Batch 3D harness repair / SEC-05 validation

The approved ADMIN/giver/receiver/CC/unrelated action matrix is unchanged.
Suggested-code is fetched immediately before its CREATE case; the ID must not
exist in the synthetic tenant. Afterwards the row is queried by that exact ID.
Missing created/delegated rows record FAIL instead of indexing an empty list.
Non-JSON mutation responses record contract/permission FAIL, never PASS.

Each recorded business assertion persists runtime_results.json with complete=false.
Normal completion writes complete=true plus full run metadata. Partial reports
must not be treated as full acceptance. Business failures remain recorded and
do not abort later cases; infrastructure/isolation guards still fail closed.
Read result checks and integrity/preflight reports, not just the process exit code.
Production code, authorization expectations and fixtures are not changed by this
repair. Current SEC-03, collision, Task matrix and mobile results require a fresh
guarded run; historical counts cannot be used for the current snapshot.

## Batch 4B1 metadata foundation

Worker overrides FILE_REGISTRY_ROOT and FILE_REGISTRY_PATH into its fresh run's
private_metadata directory before config import. Import/constructor must not
create state; explicit test-only initialization creates the sidecar schema v1.
No production upload registration, scan, static gate, binding integration or
business DB schema change occurs. WAL is opt-in with explicit verified-local-disk
assertion; default journal mode remains SQLite's rollback journal.

REGISTRY checks cover state transitions, exact metadata/tenant/locator validation,
24h unbound expiry, shared bindings, rollback, corruption/version/unavailability,
and concurrency using independent FileRegistry instances and SQLite connections.
They use threads AND two independent guarded processes to exercise SQLite locks/
constraints with no process-local lock. Parent orchestration starts metadata-only
workers inside the same fresh run; no app/provider or production DB is opened.
Read-only failure is
injected because elevated Windows permission behavior is not reliably portable.
Corrupt/empty files are never deleted/reset. Busy timeout is measured and bounded.

Future 4B2 must prepare PENDING intent, commit business object, then revalidate
exact live binding/object and activate. Sidecar and tenant DB are NOT one atomic
transaction; registry primitives contain no business authorization or file serving.
Any gateway must still enforce tenant/actor/object ACL, expiry and UNKNOWN denial.
Foundation success does not close SEC-04. Production registry must remain absent.

## Batch 4B2 trusted upload/binding integration

Registry version is now **2**. Separate partial unique indexes reserve one PENDING
and one ACTIVE per tenant/object/field slot, allowing safe replacement. Incompatible
v1, newer versions or missing replacement constraints fail closed with no automatic
upgrade/reset. No business SQL schema change or production registry initialization.

NEW authenticated upload creates WRITING intent before exclusive physical open;
completed actual bytes/size/SHA-256 produce UNBOUND metadata with 24h expiry. The
compatible URL/name response is preserved with an additive opaque file_id. Tests
override the registry to the fresh run/private_metadata path. Uploader/tenant come
from server session and tenant-local actor lookup, never client ownership fields.

The authorized business caller uses FileBindingService for Task assignment/report,
Document links and trusted forward inheritance. It resolves only canonical local
upload URLs against trusted metadata. Other-uploader UNBOUND, expired/revoked,
UNKNOWN, foreign and newly introduced unregistered local references are denied.
Existing unchanged/inherited unregistered references, external URLs and local_docs
remain business references without registry ownership claims. There is no legacy scan.

PENDING is committed before the business callback. A bounded SQLite BEGIN IMMEDIATE
serializes business commit, exact persisted-object reload/field comparison and
registry activation. Only the exact previous slot is superseded; other shared
bindings and physical bytes survive. Exact retries are idempotent. Threads and two
guarded independent processes test reservation/replacement conflicts. SQLite locks
and constraints are authoritative; no process-local lock is used.

The sidecar and business DB are NOT atomically committed together. A post-business-
commit revalidation/activation failure can leave the new business reference saved,
while old ACTIVE remains and the new intent is revoked/non-ACTIVE. The API reports
failure, never a fabricated success. Future gateway must require exact CURRENT
object field + ACTIVE binding + object ACL; reconciliation is not implemented here.
Failed compensation/busy/crash may leave stale PENDING, which grants no read authority.
Authorization denials are separately checked for zero business/registry/byte/provider
mutation. No physical orphan cleanup/deletion is implemented.

SEC-05 positive attachment fixtures now use real synthetic authenticated uploads,
not invented local URLs. Its approved authorization expectations and 530 checks
remain unchanged. Prefixes split 4B2 evidence into UPLOAD, BIND, REPLACE, FAILURE,
CONCURRENCY and SCHEMA; REGISTRY/SEC05/SEC03/BUG10 retain regression counts.
New tests include fault injection for physical write, completion, reservation,
business commits, exact revalidation and activation; exact replacement/clear,
shared forward, Document legacy compatibility and sidecar v1/corrupt constraints.

Batch 4B2 does not implement a read gateway/static exclusion, UNBOUND download
enforcement or PWA protection. /static/uploads remains public; SEC-04 stays OPEN.
Reports must confirm production registry/upload creation NO and protected-data
hash/size/mtime equality. Historical/partial runs do not validate the current snapshot.

## Batch 2A SEC-03 regression

Local upload must reject anonymous/invalid sessions with 401, and allow existing
authenticated ADMIN/MANAGER/USER upload flows. Requests cannot switch identity
using client company/owner fields. Tests check that denied upload creates no file
and that extension validation remains in place.

All three rename endpoints require authentication, then fail closed with 403.
The current schema has no trusted Drive-file ownership/tenant mapping: editable
Task/Document URLs and a global service account do not prove ownership. An
authorized ALLOW integration test is therefore BLOCKED until that metadata and
policy are explicitly approved; tests do not fake ownership to claim success.
A recording Drive stub verifies that anonymous, cross-tenant, ordinary user and
ADMIN requests never execute a Drive mutation. Local upload and /static/uploads
storage behavior remains unchanged; private download protection is Batch 2B.

## Batch 4B3 private read gateway

The runner tests the actual application routing on a fresh synthetic snapshot.
The explicit GET/HEAD `/static/uploads/{storage_name:path}` route precedes the
public static mount. The parent mount separately refuses upload segments and
resolved upload paths, including aliases; public CSS/JS/manifest/service worker
requests must continue to work. Windows StaticFiles normalizes separators, so
request aliases and framework-produced path separators are distinguished.

`file_access_service` uses the existing signed session, tenant-local actor and
registry v2 read-only snapshot. UNBOUND requires its exact uploader, tenant and
unexpired 24-hour intent. BOUND requires a live supported Task/Document binding,
an exact current persisted URL and the current object READ predicate. Task READ
reuses `task_policy.can_view_task`; Document library and gateway share the existing
library query predicate, without widening department/manager/ADMIN/CEO rules.
PENDING, REVOKED, WRITING, UNKNOWN and unregistered physical files grant no read.
Multiple valid same-tenant bindings are a union; stale metadata grants nothing.

SQLite URI access is permitted by the guard only with exact `mode=ro` and a path
inside the fresh run. The gateway never initializes or repairs the registry.
Missing/corrupt/version/schema/busy/read failures deny uniformly, without static
fallback. A readonly transaction returns a coherent file/binding snapshot.

The physical locator is server-owned. Lexical and realpath confinement, regular
file/reparse checks and opened-handle final-path validation precede size/SHA-256
verification. Responses use the immutable verified bytes, rather than reopening
the pathname in FileResponse. GET/HEAD/Range/conditional requests authorize and
hash first; unauthorized requests expose no ETag/mtime/range/size or dashboard
redirect. Private response/error headers include `private, no-store`, Pragma,
Expires and nosniff. Content-Disposition uses sanitized presentation metadata.

Targeted prefixes: GATEWAY_AUTH, GATEWAY_UNBOUND, GATEWAY_TASK,
GATEWAY_DOCUMENT, GATEWAY_TENANT, GATEWAY_PATH, GATEWAY_STATIC_BYPASS,
GATEWAY_HTTP, GATEWAY_INTEGRITY, GATEWAY_LIVE_REVALIDATION,
GATEWAY_FAIL_CLOSED and GATEWAY_ZERO_MUTATION. Every gateway read fingerprints
synthetic business DB/registry/uploads and checks the provider mutation count.
Windows symlink/junction privilege limitations are explicitly recorded in
gateway_environment.json; injected opened-handle escape tests are not represented
as successful real OS symlink/junction creation.

This batch does NOT modify service worker Cache API behavior, purge caches,
onboard legacy files, migrate SQL/physical files or fix session architecture.
`no-store` alone does not prevent an explicit service-worker Cache API write.
SEC-04 remains OPEN; 4B4 and verified legacy resolution remain separate work.

## Batch 4B4 service-worker private cache protection

Existing Node22 is used without package installation. Standalone targeted command:
`python -B tests/runtime_sandbox.py --pwa-test`. It copies actual static/sw.js into
a fresh run directory and executes it in a Node VM with synthetic fetch,
CacheStorage, install/activate/fetch events and clients. No real browser profile,
provider/network request or production cache cleanup occurs. This establishes
deterministic SW logic and simulated cache lifecycle, NOT real-browser acceptance.

Full guarded runner retains all earlier gateway/security assertions, captures
actual synthetic FastAPI GET/HEAD/Range/conditional/denial responses and replays
them through the actual SW code in Node. pwa_gateway_fixtures.json contains only
synthetic response bodies/headers, no signed cookies or production data.
pwa_results.json is merged into runtime_results.json. The source manifest now
also fingerprints static/sw.js; changes during a run invalidate the snapshot.

qlcv-mobile-v1 changes to qlcv-mobile-v2. Private namespace uses same-origin parsed
pathname with relevant slash/case/encoding normalization before generic caching.
Private and non-public dynamic/HTML/API requests are network-only with cache:no-store
for all methods. No Cache API read/write or offline fallback is permitted there.
Cross-origin requests are not intercepted/cached. Public same-origin static and
manifest GETs retain network-first/cache fallback, scoped to the current app cache.
No-store/private, redirected, private final URL or HTML responses cannot enter it.

Authenticated /mobile HTML is removed from precache; only public CSS/manifest are
precached. Activation enumerates qlcv-mobile-v<number> caches, deletes private
entries without reading their bodies, removes prior authenticated HTML/API and
cross-origin entries, safely migrates vetted public entries, then deletes obsolete
QLCV versions. Unrelated cache names remain untouched. clients.claim occurs only
after cleanup. Offline public assets still work; missing public assets yield503
text, never a cached authenticated /mobile page. Offline private/dynamic fetch fails.

Categories: PWA_PRIVATE_CLASSIFICATION, PWA_NETWORK_ONLY, PWA_NO_PRIVATE_WRITE,
PWA_OLD_CACHE_PURGE, PWA_OFFLINE_PRIVATE, PWA_METHODS, PWA_PUBLIC_CACHE,
PWA_CROSS_ORIGIN, PWA_CACHE_VERSION, PWA_4B3_INTEGRATION, PWA_ZERO_MUTATION.
The worker fingerprints DB/registry/uploads/provider state around live integration;
the Node parent compares protected production inventory before/after simulation.

Real browser and production-client update status remain NOT RUN/NOT VERIFIED.
Guarantees apply after the new worker activates; do not claim copied-session
revocation, removal of downloaded/browser-memory content, arbitrary third-party
cache cleanup or production rollout. No logout/session business change is required.
Gateway no-store remains necessary but is not alone sufficient for Cache API.
SEC-04 stays OPEN;4B5 verified legacy resolution is not implemented.

## Batch 4B5A legacy provenance model

Fresh sidecars use schema v3: VERIFIED_UPLOADER requires a real nonempty
uploader, while LEGACY_VERIFIED_MAPPING requires NULL uploader, separate review
metadata and BOUND/REVOKED state. Normal registration cannot select legacy mode.
The isolated worker tests services/legacy_provenance.py offline reviewed permits,
exact synthetic object revalidation, atomic identity/multi-binding rollback and
actual gateway READ. No production candidate discovery or activation occurs.

v2 gateway reads deterministically retain VERIFIED_UPLOADER semantics for valid
PRIVATE/UNKNOWN records; malformed/ambiguous records fail closed. v2 mutations
and implicit upgrades are refused with an explicit sidecar migration error.
No production/synthetic migration helper is executed or implemented here.
Unknown/newer schema versions fail closed. Existing production sidecar is absent.

The offline primitive is not a route or security boundary against arbitrary Python
code already holding SQLite write authority. Future trusted tooling must authenticate
the custodian, verify independent provenance evidence and the complete conflict
inventory, then issue an explicit digest-bound reviewed permit. Public/API input,
ADMIN role or attachment URL alone never issues a permit. Reviewer is not uploader.

PROVENANCE_* and LEGACY_* results are the 4B5A group; prior REGISTRY/SEC03/SEC05/
BUG10/B4B2/GATEWAY/PWA assertions remain, with only schema-version expectations
updated to the explicitly authorized v3. Actual synthetic legacy responses are
replayed through the unchanged SW and tested offline using Node VM/CacheStorage
simulation; real browser remains NOT RUN. Normal gateway fixtures are unchanged.

## Resumed Batch 4B5 discovery and reviewed synthetic apply

`services/legacy_discovery.py` is an offline module with no startup/HTTP hook.
Discovery requires an explicit trusted tenant-to-database manifest. SQLite uses
`mode=ro&immutable=1` and query-only transactions; active WAL/journal sources,
missing schemas, source changes and escaping/reparse paths fail closed. It reads
only object IDs and attachment fields, fingerprints physical bytes, and detects
cross-tenant conflicts, physical aliases, missing objects, orphans and registry
conflicts. Personal references are inventoried but cannot acquire a new ACL.

Reference-only consistent candidates remain UNKNOWN, structurally reviewable but
UNAPPROVED. An independent custodian attestation/record must explicitly identify
the tenant and physical hash. Offline authority signs the exact candidate/evidence
with HMAC; reviewer is separate from NULL historical uploader. Key custody and
real custodian authentication are administrative responsibilities, not an HTTP
or ADMIN privilege inferred by this tool. Tests use ephemeral synthetic keys.

`apply_synthetic` refuses the production checkout: it requires the copied module
and every input/storage/database path inside one guarded `.test_runtime/run-*`.
It rescans references, conflicts and physical evidence before and within the
registry transaction, then uses the existing 4B5A legacy primitive. The optional
serialized callback inspects that same transaction and excludes only its own new
identity; exceptions roll back identity and all bindings. No business writes,
production apply command, registry migration or public fallback is added.

Apply also requires the complete authoritative master tenant inventory and all
existing resolver-convention tenant databases. Partial discovery cannot authorize
apply. Candidate digests include the entire source manifest, and completeness is
rechecked before and inside the transaction to prevent omission of a conflicting
tenant. Ambiguous/noncanonical master metadata or unregistered DB sources deny.

The read-only CLI is `venv\\Scripts\\python.exe -B -m services.legacy_discovery`
with explicit `--upload-root`, repeated `--tenant TENANT=DATABASE`, and optional
`--registry`. Default output is aggregate counts. Optional `--output` creates a
private raw JSON review artifact exclusively, never overwriting an existing file
or writing under static/uploads. There is no approve-all or production apply flag.

Resumed tests use `B4B5 LEGACY_*` labels, keeping 4B5A's original labels/counts
separate. Raw evidence includes `legacy_review_synthetic.json`,
`legacy_workflow_evidence.json`, runtime results and unchanged SW/cache simulation.
The sole human-readable batch report is the next immutable `audit_codex_vN.md`,
with its acceptance checklist embedded. Historical checklist files stay untouched.

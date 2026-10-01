"""Batch 1: run an unchanged Core snapshot, with synthetic data only.

Run: python -B tests/runtime_sandbox.py
Never import app from the production checkout. Reports contain no secrets.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import uuid

PROJECT = Path(__file__).resolve().parents[1]


def inventory():
    paths = list(PROJECT.glob('qlcv.db*')) + list((PROJECT / 'database').glob('master_system.db*'))
    paths += list((PROJECT / 'database/tenants').glob('*.db*'))
    paths += list((PROJECT / 'static/uploads').rglob('*'))
    paths += [PROJECT / '.env', PROJECT / 'companies.json', PROJECT / 'seed.xlsx']
    result = {}
    for p in paths:
        if p.is_file():
            stat = p.stat()
            result[str(p.relative_to(PROJECT))] = {
                'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns,
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
            }
    return result


def inside(path, root):
    p = Path(os.fsdecode(path)).resolve()
    if not p.is_relative_to(root.resolve()):
        raise RuntimeError('SANDBOX BLOCK: path outside sandbox')
    return p


def worker(root):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='backslashreplace')
    root = root.resolve()
    if not root.is_relative_to(PROJECT / '.test_runtime') or not root.name.startswith('run-'):
        raise RuntimeError('Worker root must be a dedicated .test_runtime/run-* directory')
    appdir = root / 'app'
    os.chdir(appdir)
    sys.path.insert(0, str(appdir))
    sys.dont_write_bytecode = True
    # Drop inherited application/provider configuration. Never load real .env.
    for key in list(os.environ):
        if any(x in key.upper() for x in ['SECRET', 'TOKEN', 'API_KEY', 'GOOGLE', 'SMTP', 'DATABASE', 'LOCAL_DOCS']):
            os.environ.pop(key, None)
    os.environ.update(APP_ENV='test', SECRET_KEY=uuid.uuid4().hex + uuid.uuid4().hex,
                      DATABASE_URL='sqlite:///' + (appdir / 'qlcv.db').as_posix(),
                      UPLOAD_DIR=str(appdir / 'static/uploads'), LOCAL_DOCS_DIR='',
                      FILE_REGISTRY_ROOT=str(root / 'private_metadata'),
                      FILE_REGISTRY_PATH=str(root / 'private_metadata/file_registry.sqlite3'),
                      GOOGLE_APPLICATION_CREDENTIALS=str(root / 'temp/missing-credentials.json'),
                      TEMP=str(root / 'temp'), TMP=str(root / 'temp'))
    import tempfile
    tempfile.tempdir = str(root / 'temp')
    # Windows platform detection otherwise launches cmd.exe; do not relax the guard.
    import platform
    if sys.platform == 'win32':
        platform._syscmd_ver = lambda *a, **k: ('Windows', '', '.'.join(map(str, sys.getwindowsversion()[:3])))
    violations = []
    import socket
    import threading
    pair_state = threading.local()
    real_socketpair = socket.socketpair

    def local_socketpair(*a, **k):
        # asyncio on Windows requires an internal loopback wakeup socket pair.
        pair_state.internal = True
        try:
            return real_socketpair(*a, **k)
        finally:
            pair_state.internal = False

    socket.socketpair = local_socketpair

    def block(message):
        violations.append(message)
        raise RuntimeError('SANDBOX BLOCK: ' + message)

    def check(path):
        try:
            return inside(path, root)
        except Exception:
            block('path outside sandbox')

    def sqlite_path(database):
        if isinstance(database,str) and database.startswith('file:'):
            from urllib.parse import urlsplit, unquote
            from urllib.request import url2pathname
            parsed=urlsplit(database)
            if parsed.netloc or parsed.query not in ('mode=ro','mode=ro&immutable=1') or parsed.fragment:
                block('Unsafe SQLite URI denied')
            return check(url2pathname(parsed.path))
        return check(database)

    def audit(event, args):
        if event == 'sqlite3.connect':
            sqlite_path(args[0])  # Confined read-only (optionally immutable) URIs, never production.
        elif event == 'open':
            path, mode, flags = args
            if isinstance(path, int):
                return
            if Path(os.fsdecode(path)).name == '.env':
                block('dotenv read denied')
            if (isinstance(mode, str) and any(x in mode for x in 'wax+')) or (flags and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)):
                check(path)
        elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.utime'):
            check(args[0])
        elif event in ('os.rename', 'os.link', 'os.symlink'):
            check(args[0]); check(args[1])
        elif event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.bind', 'socket.sendto', 'subprocess.Popen', 'os.system'):
            if event in ('socket.connect', 'socket.bind') and getattr(pair_state, 'internal', False) and args[1][0] in ('127.0.0.1', '::1'):
                return
            block('external network/process denied')

    sys.addaudithook(audit)
    import dotenv
    dotenv.load_dotenv = lambda *a, **k: False
    import sqlite3
    real_connect = sqlite3.connect

    def guarded_connect(database, *a, **k):
        sqlite_path(database)
        if k.get('uri') and not (isinstance(database,str) and database.startswith('file:')):
            block('SQLite URI denied')
        conn = real_connect(database, *a, **k)
        conn.set_authorizer(lambda action, *args: sqlite3.SQLITE_DENY
                            if action == sqlite3.SQLITE_ATTACH else sqlite3.SQLITE_OK)
        return conn

    sqlite3.connect = guarded_connect
    sqlite3.dbapi2.connect = guarded_connect
    # Offline provider stubs: no credentials, paid AI, discovery, or real Drive.
    # Also avoids importing the host's incompatible optional OpenSSL stack.
    import types
    discovery = types.ModuleType('googleapiclient.discovery')
    discovery.build = lambda *a, **k: block('Google Drive network denied')
    sys.modules['googleapiclient.discovery'] = discovery
    genai = types.ModuleType('google.generativeai')
    genai.configure = lambda *a, **k: block('paid AI denied')
    genai.GenerativeModel = lambda *a, **k: block('paid AI denied')
    sys.modules['google.generativeai'] = genai
    import sqlalchemy
    original_engine = sqlalchemy.create_engine

    def guarded_engine(url, *a, **k):
        parsed = sqlalchemy.engine.make_url(url)
        if parsed.drivername != 'sqlite' or not parsed.database or parsed.query:
            block('only sandbox file SQLite URLs are permitted')
        check(parsed.database)
        return original_engine(url, *a, **k)

    sqlalchemy.create_engine = guarded_engine
    # Import-only phase: no FastAPI lifespan/startup until assertions below pass.
    import app
    from database import connection, multi_tenant as mt
    from models.models import Employee, Task
    from models.master_models import MasterBase, MasterCompany, GlobalUserIndex
    from services.security_utils import hash_password
    from services.auth_service import AuthService
    from fastapi.testclient import TestClient

    original_path = mt.get_tenant_db_path

    def guarded_path(mst):
        return str(check(original_path(mst)))

    mt.get_tenant_db_path = guarded_path
    check(connection.engine.url.database)
    check(mt.master_engine.url.database)
    for mst in ['0312345678', 'default', '', '9000000001', '9000000002']:
        check(mt.get_tenant_db_path(mst))
    # Prove fail-closed checks; expected probes are removed from violation log.
    probes = []
    for target in [PROJECT / 'qlcv.db', PROJECT / 'database/master_system.db', PROJECT / 'database/tenants/probe.db']:
        try:
            guarded_engine('sqlite:///' + target.as_posix())
            raise AssertionError('guard allowed production DB')
        except RuntimeError:
            probes.append('production DB blocked')
    try:
        mt.get_tenant_db_path('../../../../escape')
        raise AssertionError('guard allowed traversal')
    except RuntimeError:
        probes.append('traversal blocked')
    for probe in [lambda: sqlite3.connect(str(PROJECT / 'qlcv.db')),
                  lambda: (PROJECT / 'qlcv.db').open('ab'),
                  lambda: socket.create_connection(('127.0.0.1', 9))]:
        try:
            probe()
            raise AssertionError('guard allowed forbidden operation')
        except RuntimeError:
            probes.append('direct DB/write/network blocked')
    probe_db = sqlite3.connect(str(root / 'temp/guard-probe.db'))
    try:
        probe_db.execute('ATTACH DATABASE ? AS forbidden', (str(PROJECT / 'qlcv.db'),))
        raise AssertionError('guard allowed ATTACH')
    except sqlite3.DatabaseError:
        probes.append('SQLite ATTACH blocked')
    finally:
        probe_db.close()
    violations.clear()
    # Fixture schema/data are entirely synthetic; production DBs are never copied.
    connection.Base.metadata.create_all(connection.engine)
    MasterBase.metadata.create_all(mt.master_engine)
    password = uuid.uuid4().hex
    db = connection.SessionLocal()
    db.add(Employee(ma_nv='ADMIN', ten_nv='Sandbox Master', mat_khau=hash_password(password),
                    email='master@sandbox.invalid', quyen='ADMIN'))
    db.commit(); db.close()
    actors = []
    master = mt.MasterSessionLocal()
    for label, mst in [('A', '9000000001'), ('B', '9000000002')]:
        engine = mt.get_tenant_engine(mst)
        connection.Base.metadata.create_all(engine)
        master.add(MasterCompany(tax_code=mst, name='Sandbox Company ' + label,
                                 db_path=mt.get_tenant_db_path(mst), status='ACTIVE'))
        tenant = mt.get_tenant_session(mst)
        for role in ['ADMIN', 'MANAGER', 'USER']:
            ma = label + '_' + role
            email = ma.lower() + '@sandbox.invalid'
            tenant.add(Employee(ma_nv=ma, ten_nv=ma, email=email,
                                mat_khau=hash_password(password), quyen=role))
            master.add(GlobalUserIndex(email=email, tax_code=mst, ma_nv=ma))
            actors.append({'company': label, 'mst': mst, 'actor': ma, 'role': role})
        tenant.add(Task(id_phan_cong=label + '-TASK', ma_cv=label + '-TASK', ten_cv='Synthetic ' + label,
                        nguoi_giao=label + '_ADMIN', nguoi_nhan=label + '_USER', nguoi_phoi_hop=label + '_MANAGER'))
        tenant.commit(); tenant.close()
    master.commit(); master.close()
    routers = ['auth', 'tasks', 'master', 'companies', 'documents', 'personal', 'ai', 'processes', 'jds', 'org_chart', 'mobile']
    def endpoints(routes):
        for route in routes:
            if getattr(route, 'endpoint', None):
                yield route.endpoint
            original = getattr(route, 'original_router', None)
            child = getattr(original, 'routes', None) if original else getattr(route, 'routes', None)
            if child:
                yield from endpoints(child)
    modules = {e.__module__ for e in endpoints(app.app.routes)}
    loaded = {name: 'routes.' + name in modules for name in routers}
    assert all(loaded.values()), 'Core router missing'
    for name, module in list(sys.modules.items()):
        if name == 'app' or name == 'config' or name.split('.')[0] in ['database', 'models', 'routes', 'services']:
            if getattr(module, '__file__', None):
                check(module.__file__)
    assert not violations, 'Isolation violation before startup'
    (root / 'preflight.json').write_text(json.dumps({
        'status': 'PASS', 'default_database': connection.engine.url.database,
        'master_database': mt.master_engine.url.database,
        'tenant_paths': [mt.get_tenant_db_path(x) for x in ['9000000001', '9000000002']],
        'guard_probes': probes, 'routers': loaded,
    }, indent=2), encoding='utf-8')
    results = []
    # SEC-03: a recording Drive stub detects any mutation on denied requests.
    from services.drive_service import DriveService
    drive_calls = []

    class DriveStub:
        def files(self):
            return self

        def update(self, **kwargs):
            drive_calls.append(kwargs)
            self.file_id = kwargs['fileId']
            return self

        def execute(self):
            return {'webViewLink': 'https://drive.google.com/open?id=' + self.file_id}

    drive_stub = DriveStub()
    DriveService.get_drive_service = staticmethod(lambda: drive_stub)
    rename_paths = ['/api/drive/rename-task-file', '/api/drive/rename-report-file', '/api/drive/rename-forward-file']

    def record(name, actual, expected):
        assert not violations, 'STOP: sandbox guard triggered'
        results.append({'test': name, 'actual': actual, 'expected': expected, 'pass': actual == expected})
        # Persist each business result so an unexpected later failure cannot
        # erase evidence. Isolation failures still raise and stop the worker.
        (root / 'runtime_results.json').write_text(json.dumps({
            'complete': False, 'isolation_preflight': 'PASS', 'routers': loaded,
            'results': results, 'unexpected_guard_violations': violations,
            'drive_mutation_calls': len(drive_calls),
        }, indent=2), encoding='utf-8')

    # Registry foundation is explicit/test-only: importing never initializes it.
    from services.file_registry import FileRegistry, RegistryError
    from config import Config
    from concurrent.futures import ThreadPoolExecutor
    from datetime import datetime, timedelta, timezone
    from unittest.mock import patch
    registry_path = check(Config.FILE_REGISTRY_PATH)
    record('REGISTRY lazy import no sidecar', registry_path.exists(), False)
    reg = FileRegistry()
    record('REGISTRY constructor no sidecar', registry_path.exists(), False)
    reg.initialize_registry()
    record('REGISTRY missing parent explicit initialization', registry_path.is_file(), True)
    reg.initialize_registry()
    record('REGISTRY schema version', reg.VERSION, 3)

    def rejected(name, operation):
        try:
            operation()
            record('REGISTRY ' + name, 'allowed', 'RegistryError')
        except RegistryError:
            record('REGISTRY ' + name, 'RegistryError', 'RegistryError')

    def writing(name, tenant='9000000001', classification='PRIVATE', registry=reg):
        return registry.register_writing(tenant, 'A_USER', 'LOCAL_UPLOADS', name, 'display.txt',
                                         classification=classification)

    def ready(name, classification='PRIVATE'):
        file_id = writing(name, classification=classification)
        reg.complete_unbound(file_id, '9000000001', 4, hashlib.sha256(b'test').hexdigest())
        return file_id

    first = writing('first.txt')
    record('REGISTRY WRITING intent', reg.get_file(first, '9000000001')['state'], 'WRITING')
    rejected('WRITING cannot bind', lambda: reg.create_pending_binding(first,'9000000001','TASK','one','assignment'))
    reg.complete_unbound(first,'9000000001',4,hashlib.sha256(b'test').hexdigest())
    row = reg.get_file(first,'9000000001')
    record('REGISTRY UNBOUND completion', row['state'], 'UNBOUND')
    hours = (datetime.fromisoformat(row['expires_at']) - datetime.fromisoformat(row['created_at'])).total_seconds()/3600
    record('REGISTRY expiry 24 hours', 24 <= hours < 24.01, True)
    record('REGISTRY expiry identifiable', reg.expired_unbound(row,datetime.now(timezone.utc)+timedelta(hours=25)), True)
    record('REGISTRY unexpired identifiable', reg.expired_unbound(row), False)
    record('REGISTRY tenant scoped lookup', reg.get_file(first,'9000000002'), None)
    record('REGISTRY storage lookup', reg.get_file_by_storage('9000000001','LOCAL_UPLOADS','first.txt')['file_id'], first)
    rejected('duplicate storage locator', lambda: writing('first.txt'))
    rejected('invalid completion transition', lambda: reg.complete_unbound(first,'9000000001',4,'a'*64))
    rejected('complete tenant mismatch', lambda: reg.complete_unbound(first,'9000000002',4,'a'*64))
    rejected('invalid hash', lambda: reg.complete_unbound(first,'9000000001',4,'invalid'))
    for name in ['', '../a.txt', '..\\a.txt', '/absolute.txt', 'C:\\a.txt', '\\\\server\\file', 'a/b.txt','a\\b.txt','bad\x00.txt']:
        rejected('invalid locator ' + repr(name), lambda name=name: writing(name))
    for fields in [('', 'user'), ('tenant','')]:
        rejected('empty identity ' + repr(fields), lambda fields=fields: reg.register_writing(*fields,'LOCAL','unique.txt','display'))
    rejected('invalid UUID', lambda: reg.register_writing('tenant','user','LOCAL','uuid.txt','display',file_id='not-uuid'))
    rejected('invalid classification', lambda: writing('classification.txt',classification='PUBLIC'))
    for path in [appdir/'static/registry.sqlite3', appdir/'static/uploads/registry.sqlite3', root/'outside.sqlite3']:
        rejected('FAILCLOSED invalid/public path ' + path.parent.name, lambda path=path: FileRegistry(path))
    local_docs = root/'private_metadata/local_docs'
    with patch.dict(os.environ, {'LOCAL_DOCS_DIR':str(local_docs)}):
        rejected('FAILCLOSED LOCAL_DOCS path', lambda: FileRegistry(local_docs/'registry.sqlite3'))
    rejected('FAILCLOSED WAL without local verification', lambda: FileRegistry(wal=True))

    binding = reg.create_pending_binding(first,'9000000001','TASK','one','assignment')
    record('REGISTRY PENDING not active', reg.list_active_bindings(first,'9000000001'), [])
    record('REGISTRY exact binding idempotent',reg.create_pending_binding(first,'9000000001','TASK','one','assignment'),binding)
    second = ready('second.txt')
    rejected('conflicting binding',lambda:reg.create_pending_binding(second,'9000000001','TASK','one','assignment'))
    rejected('generation conflict',lambda:reg.create_pending_binding(first,'9000000001','TASK','one','assignment',2))
    rejected('binding tenant mismatch',lambda:reg.create_pending_binding(first,'9000000002','TASK','other','assignment'))
    rejected('missing file binding',lambda:reg.create_pending_binding(str(uuid.uuid4()),'9000000001','TASK','none','assignment'))
    unknown = ready('unknown.txt','UNKNOWN')
    rejected('UNKNOWN cannot bind/activate',lambda:reg.create_pending_binding(unknown,'9000000001','TASK','unknown','assignment'))
    rejected('missing binding activate',lambda:reg.activate_binding('missing','9000000001'))
    rejected('activate tenant mismatch',lambda:reg.activate_binding(binding,'9000000002'))
    reg.activate_binding(binding,'9000000001')
    record('REGISTRY ACTIVE visible',len(reg.list_active_bindings(first,'9000000001')),1)
    record('REGISTRY BOUND state',reg.get_file(first,'9000000001')['state'],'BOUND')
    shared=reg.create_pending_binding(first,'9000000001','TASK','child','assignment')
    reg.activate_binding(shared,'9000000001')
    record('REGISTRY shared separate bindings',len(reg.list_active_bindings(first,'9000000001')),2)
    reg.revoke_binding(binding,'9000000001')
    record('REGISTRY revoked not active',len(reg.list_active_bindings(first,'9000000001')),1)
    rejected('revoked cannot activate',lambda:reg.activate_binding(binding,'9000000001'))
    reg.mark_revoked(first,'9000000001')
    record('REGISTRY file revoke hides all bindings',reg.list_active_bindings(first,'9000000001'),[])
    rejected('revoked file cannot bind',lambda:reg.create_pending_binding(first,'9000000001','TASK','more','assignment'))

    # Test rollback injection, expiry and corruption in synthetic sidecar only.
    before = reg.get_file(second,'9000000001')
    try:
        with reg._connection(mutation=True) as conn:
            conn.execute("UPDATE files SET state='REVOKED' WHERE file_id=?",(second,))
            raise RegistryError('injected rollback')
    except RegistryError:
        pass
    record('REGISTRY transaction rollback no partial mutation',reg.get_file(second,'9000000001'),before)
    with reg._connection(mutation=True) as conn:
        conn.execute('UPDATE files SET expires_at=? WHERE file_id=?',((datetime.now(timezone.utc)-timedelta(hours=1)).isoformat(),second))
    rejected('expired UNBOUND cannot bind',lambda:reg.create_pending_binding(second,'9000000001','TASK','expired','assignment'))
    pending_file=ready('expired-pending.txt')
    pending=reg.create_pending_binding(pending_file,'9000000001','TASK','expired-pending','assignment')
    with reg._connection(mutation=True) as conn:
        conn.execute('UPDATE files SET expires_at=? WHERE file_id=?',((datetime.now(timezone.utc)-timedelta(hours=1)).isoformat(),pending_file))
    rejected('expired PENDING cannot activate',lambda:reg.activate_binding(pending,'9000000001'))

    def race_reg(i):
        return writing('race-'+str(i)+'.txt',registry=FileRegistry())
    with ThreadPoolExecutor(max_workers=6) as pool:
        registered=list(pool.map(race_reg,range(12)))
    record('REGISTRY CONCURRENCY distinct registrations no loss',len({fid for fid in registered}),12)
    record('REGISTRY CONCURRENCY all registrations readable',all(reg.get_file(fid,'9000000001') for fid in registered),True)

    def race_result(operation):
        try:
            return operation()
        except RegistryError:
            return None
    with ThreadPoolExecutor(max_workers=6) as pool:
        duplicate=list(pool.map(lambda _:race_result(lambda:writing('same-race.txt',registry=FileRegistry())),range(6)))
    record('REGISTRY CONCURRENCY same locator one winner',len([v for v in duplicate if v]),1)
    race_file=ready('binding-race.txt')
    with ThreadPoolExecutor(max_workers=6) as pool:
        exact=list(pool.map(lambda _:FileRegistry().create_pending_binding(race_file,'9000000001','TASK','race','assignment'),range(6)))
    record('REGISTRY CONCURRENCY exact binding same ID',len(set(exact)),1)
    reg.activate_binding(exact[0],'9000000001')
    other_file=ready('binding-conflict-race.txt')
    def conflict(fid):
        registry=FileRegistry()
        bid=registry.create_pending_binding(fid,'9000000001','TASK','conflict-race','assignment')
        registry.activate_binding(bid,'9000000001')
        return bid
    with ThreadPoolExecutor(max_workers=2) as pool:
        conflicting=list(pool.map(lambda fid:race_result(lambda:conflict(fid)),[race_file,other_file]))
    record('REGISTRY CONCURRENCY conflicting slot one winner',len([v for v in conflicting if v]),1)
    record('REGISTRY CONCURRENCY no duplicate ACTIVE slot',sum(len([b for b in reg.list_active_bindings(fid,'9000000001') if b['object_id']=='conflict-race']) for fid in [race_file,other_file]),1)
    with reg._connection() as conn:
        record('REGISTRY CONCURRENCY integrity readable',conn.execute('PRAGMA quick_check').fetchone()[0],'ok')
        record('REGISTRY foreign keys enabled',conn.execute('PRAGMA foreign_keys').fetchone()[0],1)
        record('REGISTRY bounded busy timeout',conn.execute('PRAGMA busy_timeout').fetchone()[0],300)
    lock=sqlite3.connect(str(registry_path),isolation_level=None)
    lock.execute('BEGIN IMMEDIATE')
    try:
        import time
        start=time.monotonic()
        rejected('CONCURRENCY FAILCLOSED busy controlled',lambda:writing('locked.txt',registry=FileRegistry(busy_ms=80)))
        record('REGISTRY CONCURRENCY busy bounded',time.monotonic()-start < 2,True)
    finally:
        lock.rollback();lock.close()
    for label,content in [('corrupt',b'not a sqlite file'),('empty',b'')]:
        path=registry_path.parent/(label+'.sqlite3')
        path.write_bytes(content)
        rejected('FAILCLOSED '+label+' existing no reset',lambda path=path:FileRegistry(path).initialize_registry())
        record('REGISTRY FAILCLOSED '+label+' bytes preserved',path.read_bytes()==content,True)
    version_path=registry_path.parent/'version.sqlite3'
    version_reg=FileRegistry(version_path)
    version_reg.initialize_registry()
    db=sqlite3.connect(str(version_path));db.execute('PRAGMA user_version=999');db.commit();db.close()
    rejected('FAILCLOSED newer schema version',version_reg.initialize_registry)
    rejected('FAILCLOSED missing uninitialized sidecar',lambda:FileRegistry(registry_path.parent/'missing.sqlite3').get_file('id','tenant'))
    # Portable controlled unwritable simulation; real permission semantics differ
    # on elevated Windows accounts. Never chmod production or relax audit guards.
    with patch('services.file_registry.sqlite3.connect',side_effect=sqlite3.OperationalError('readonly')):
        rejected('FAILCLOSED read-only connection controlled',lambda:reg.get_file(first,'9000000001'))
    wal_reg=FileRegistry(registry_path.parent/'wal.sqlite3',verified_local_disk=True,wal=True)
    wal_reg.initialize_registry()
    with wal_reg._connection() as conn:
        record('REGISTRY verified local WAL opt in',conn.execute('PRAGMA journal_mode').fetchone()[0],'wal')
    process_file=ready('process-binding.txt')
    (root/'registry_process_fixture.json').write_text(json.dumps({'file_id':process_file}),encoding='utf-8')

    with TestClient(app.app, raise_server_exceptions=False) as client:
        record('GET /login', client.get('/login').status_code, 200)
        master_login = client.post('/api/auth/login', json={'username': 'ADMIN', 'password': password, 'tax_code': '0312345678'})
        record('synthetic master login', master_login.json().get('success'), True)
        for actor in actors:
            client.cookies.clear()
            login = client.post('/api/auth/login', json={'username': actor['actor'], 'password': password, 'tax_code': actor['mst']})
            record(actor['actor'] + ' login', login.json().get('success'), True)
            record(actor['actor'] + ' dashboard', client.get('/dashboard').status_code, 200)
            record(actor['actor'] + ' core page', client.get('/tasks').status_code, 200)
            own = actor['company'] + '-TASK'
            other = ('B' if actor['company'] == 'A' else 'A') + '-TASK'
            record(actor['actor'] + ' own tenant Task', client.get('/api/tasks/' + own).json().get('idPhanCong') == own, True)
            record(actor['actor'] + ' other tenant Task', client.get('/api/tasks/' + other).json().get('success'), False)
            if actor['role'] in ['USER', 'MANAGER']:
                record(actor['actor'] + ' master operation', client.post('/api/companies/switch-tenant', data={'tax_code': '9000000002'}).status_code, 403)
            upload = client.post('/api/drive/upload-local', files={'file': (actor['actor'] + '.txt', b'authenticated sandbox upload', 'text/plain')})
            record('SEC03 ' + actor['actor'] + ' upload status', upload.status_code, 200)
            record('SEC03 ' + actor['actor'] + ' upload success', upload.json().get('success'), True)
            upload_path = check(appdir / upload.json()['url'].lstrip('/'))
            record('SEC03 ' + actor['actor'] + ' upload content', upload_path.read_bytes() == b'authenticated sandbox upload', True)
            for path in rename_paths:
                before_calls = len(drive_calls)
                record('SEC03 ' + actor['actor'] + ' rename blocked ' + path, client.post(path, json={
                    'fileId': actor['company'] + '-DRIVE-FILE', 'maCV': own,
                }).status_code, 403)
                record('SEC03 ' + actor['actor'] + ' cross tenant rename ' + path, client.post(path, json={
                    'fileId': ('B' if actor['company'] == 'A' else 'A') + '-DRIVE-FILE',
                    'maCV': other, 'company_mst': '9000000002', 'owner': 'B_ADMIN', 'actor': 'B_ADMIN',
                }).status_code, 403)
                record('SEC03 denied rename never calls Drive ' + actor['actor'] + path, len(drive_calls), before_calls)
            record(actor['actor'] + ' logout', client.post('/api/auth/logout').status_code, 200)
            record(actor['actor'] + ' post logout', client.get('/api/auth/current-user').json().get('ma'), '')
        client.cookies.clear()
        record('anonymous private tasks', client.get('/api/tasks').json().get('success'), False)
        before_uploads = sorted(p.name for p in (appdir / 'static/uploads').iterdir())
        record('anonymous upload baseline', client.post('/api/drive/upload-local', files={'file': ('baseline.txt', b'sandbox only', 'text/plain')}).status_code, 401)
        record('SEC03 anonymous upload creates no file', sorted(p.name for p in (appdir / 'static/uploads').iterdir()), before_uploads)
        for path in rename_paths:
            record('SEC03 anonymous rename ' + path, client.post(path, json={'fileId': 'B-DRIVE-FILE', 'maCV': 'B-TASK'}).status_code, 401)
        invalid_cookie = {'Cookie': 'ams_session=invalid-signed-cookie'}
        record('SEC03 invalid cookie upload', client.post('/api/drive/upload-local', headers=invalid_cookie, files={'file': ('invalid.txt', b'blocked', 'text/plain')}).status_code, 401)
        for path in rename_paths:
            record('SEC03 invalid cookie rename ' + path, client.post(path, headers=invalid_cookie, json={'fileId': 'B-DRIVE-FILE'}).status_code, 401)
        client.cookies.clear()
        client.post('/api/auth/login', json={'username': 'A_USER', 'password': password, 'tax_code': '9000000001'})
        record('SEC03 forbidden extension still rejected', client.post('/api/drive/upload-local', files={
            'file': ('forbidden.html', b'<script>test only</script>', 'text/html')}).json().get('success'), False)
        spoof = client.post('/api/drive/upload-local', data={'company_mst': '9000000002', 'owner': 'B_ADMIN'},
                            files={'file': ('tenant-spoof.txt', b'test data', 'text/plain')})
        record('SEC03 upload ignores client tenant identity', spoof.json().get('success'), True)
        record('SEC03 upload does not change tenant session', client.get('/api/auth/current-user').json().get('company_mst'), '9000000001')
        record('SEC03 no Drive mutations on denied requests', len(drive_calls), 0)
        # BUG-10: API uploads keep original name but allocate independent files.
        from concurrent.futures import ThreadPoolExecutor
        from unittest.mock import patch
        from types import SimpleNamespace
        import re

        def local_upload(content, name='same-name.txt'):
            response = client.post('/api/drive/upload-local', files={'file': (name, content, 'application/octet-stream')})
            assert response.status_code == 200 and response.json().get('success'), 'Upload failed'
            data = response.json()
            assert data['name'] == name, 'Original UI filename changed'
            path = check(appdir / data['url'].lstrip('/'))
            assert path.parent == (appdir / 'static/uploads').resolve(), 'Upload escaped storage'
            assert path.read_bytes() == content, 'Upload content overwritten'
            return data['url'], path

        first_url, first_path = local_upload(b'file A')
        second_url, second_path = local_upload(b'file B')
        record('BUG10 same original name distinct paths', first_url != second_url, True)
        record('BUG10 first content survives second upload', first_path.read_bytes() == b'file A', True)
        rapid = [local_upload(('rapid-' + str(i)).encode()) for i in range(16)]
        record('BUG10 rapid upload unique paths', len({url for url, _ in rapid}), 16)

        barrier = threading.Barrier(8)

        def concurrent_upload(i):
            barrier.wait(timeout=20)
            content = ('concurrent-' + str(i)).encode()
            return local_upload(content), content

        with ThreadPoolExecutor(max_workers=8) as pool:
            concurrent = list(pool.map(concurrent_upload, range(8)))
        record('BUG10 concurrent upload unique paths', len({item[0][0] for item in concurrent}), 8)
        record('BUG10 concurrent contents remain intact', all(path.read_bytes() == content
               for (_, path), content in concurrent), True)
        record('BUG10 generated identity format', all(re.fullmatch(r'/static/uploads/[0-9a-f]{32}\.txt', url)
               for url, _ in [(first_url, first_path), (second_url, second_path), *rapid]), True)

        # Deterministic collision proves exclusive create and bounded retry,
        # rather than relying only on the statistical uniqueness of UUIDs.
        fixed = uuid.UUID(hex='0' * 32)
        occupied = appdir / 'static/uploads' / (fixed.hex + '.txt')
        occupied.write_bytes(b'existing sentinel')
        identifiers = iter([fixed, uuid.uuid4()])
        with patch('services.drive_service.uuid', SimpleNamespace(uuid4=lambda: next(identifiers))):
            retry_url, _ = local_upload(b'retry content')
        record('BUG10 repeated ID retries different path', retry_url != '/static/uploads/' + occupied.name, True)
        with patch('services.drive_service.uuid', SimpleNamespace(uuid4=lambda: fixed)):
            exhausted = client.post('/api/drive/upload-local', files={'file': ('same-name.txt', b'must not overwrite', 'text/plain')})
        record('BUG10 exhausted collisions fail closed', exhausted.json().get('success'), False)
        record('BUG10 existing file never overwritten', occupied.read_bytes() == b'existing sentinel', True)
        _, traversed = local_upload(b'traversal stays local', '../../nested/unsafe.txt')
        record('BUG10 traversal name confined', traversed.parent == (appdir / 'static/uploads').resolve(), True)
        record('BUG10 traversal basename not used as identity', 'unsafe' not in traversed.name, True)
        _, extension_path = local_upload(b'validated extension', 'report.PDF')
        record('BUG10 validated extension preserved', extension_path.suffix, '.PDF')
        record('BUG10 forbidden extension case insensitive', client.post('/api/drive/upload-local', files={
            'file': ('../../blocked.HTML', b'blocked', 'text/html')}).json().get('success'), False)
        # SEC-05: approved action matrix, synthetic roles/relationships only.
        tenant = mt.get_tenant_session('9000000001')
        extra_actors = []
        for role in ['USER', 'MANAGER', 'CEO']:
            for relationship in ['GIVER', 'RECEIVER', 'CC', 'OTHER']:
                ma = 'A_' + role + '_' + relationship
                tenant.add(Employee(ma_nv=ma, ten_nv=ma, quyen=role,
                                    mat_khau=hash_password(password)))
                extra_actors.append((ma, role, relationship))
        tenant.commit(); tenant.close()

        def task_state():
            state = {}
            for mst in ['9000000001', '9000000002']:
                db = mt.get_tenant_session(mst)
                state[mst] = sorted([tuple(getattr(t, col.name) for col in Task.__table__.columns)
                                     for t in db.query(Task).all()], key=lambda row: row[0])
                db.close()
            return state

        def file_state():
            return {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in (appdir / 'static/uploads').iterdir() if p.is_file()}

        def task_row(task_id, mst='9000000001'):
            db = mt.get_tenant_session(mst)
            t = db.query(Task).filter(Task.id_phan_cong == task_id).first()
            data = {c.name: getattr(t, c.name) for c in Task.__table__.columns} if t else None
            db.close()
            return data

        def seed_task(task_id, giver='A_ADMIN', receiver='A_USER', cc='A_MANAGER', mst='9000000001'):
            db = mt.get_tenant_session(mst)
            db.add(Task(id_phan_cong=task_id, ma_cv=task_id, ten_cv='SEC05 synthetic',
                        nguoi_giao=giver, nguoi_nhan=receiver, nguoi_phoi_hop=cc,
                        file_giao_viec='/static/uploads/synthetic-task.txt',
                        file_bao_cao='/static/uploads/synthetic-report.txt',
                        nhat_ky_bao_cao='existing report', noi_dung_nhac_nho='existing directive'))
            db.commit(); db.close()

        def task_login(ma, mst='9000000001'):
            client.cookies.clear()
            assert client.post('/api/auth/login', json={'username': ma, 'password': password,
                                                       'tax_code': mst}).json().get('success')

        def task_write(name, url, payload, allow):
            before_db, before_files, before_drive = task_state(), file_state(), len(drive_calls)
            with reg._connection() as conn:
                before_registry={t:[tuple(r) for r in conn.execute('SELECT * FROM '+t+' ORDER BY 1')] for t in ['files','bindings']}
            response = client.post(url, json=payload)
            record('SEC05 ' + name + ' contract', response.status_code, 200)
            try:
                data = response.json()
                if not isinstance(data, dict):
                    data = {}
            except ValueError:
                data = {}
            record('SEC05 ' + name + ' permission', data.get('success'), allow)
            if not allow:
                with reg._connection() as conn:
                    after_registry={t:[tuple(r) for r in conn.execute('SELECT * FROM '+t+' ORDER BY 1')] for t in ['files','bindings']}
                record('B4B2 BIND SEC05 denied '+name+' registry unchanged',after_registry==before_registry,True)
                record('SEC05 ' + name + ' DB unchanged', task_state(), before_db)
                record('SEC05 ' + name + ' files unchanged', file_state(), before_files)
                record('SEC05 ' + name + ' provider unchanged', len(drive_calls), before_drive)
                record('SEC05 ' + name + ' no sensitive payload', 'idPhanCong' not in data
                       and 'data' not in data, True)
            return data

        matrix_actors = [('A_ADMIN', 'ADMIN', 'OTHER'), *extra_actors]
        for ma, role, relationship in matrix_actors:
            task_login(ma)
            giver = ma if relationship == 'GIVER' else 'A_ADMIN'
            receiver = ma if relationship == 'RECEIVER' else 'A_USER'
            cc = ma if relationship == 'CC' else 'A_MANAGER'
            visible = role == 'ADMIN' or relationship != 'OTHER'
            edits = role == 'ADMIN' or relationship == 'GIVER'
            reports = role == 'ADMIN' or relationship == 'RECEIVER'
            prefix = ma + '-MATRIX'
            seed_task(prefix, giver, receiver, cc)
            edit_url, _ = local_upload(b'SEC05 trusted assignment')
            report_url, _ = local_upload(b'SEC05 trusted report')
            view = client.get('/api/tasks/' + prefix).json()
            record('SEC05 ' + ma + ' VIEW', view.get('idPhanCong') == prefix, visible)
            listing = client.get('/api/tasks').json()
            record('SEC05 ' + ma + ' LIST', any(t['idPhanCong'] == prefix for t in listing['data']), visible)
            task_write(ma + ' EDIT', '/api/tasks', {'idPhanCong': prefix, 'tenCV': 'edited',
                       'nguoiNhan': receiver, 'phoiHop': cc, 'link': edit_url}, edits)
            task_write(ma + ' DIRECT', '/api/tasks/' + prefix + '/remind',
                       {'message': 'directive', 'director': 'B_ADMIN'}, edits)
            if edits:
                record('SEC05 ' + ma + ' director identity', '[' + ma + ']' in
                       task_row(prefix)['noi_dung_nhac_nho'], True)
            task_write(ma + ' REPORT', '/api/tasks/' + prefix + '/report',
                       {'tienDo': 30, 'status': 'Đang thực hiện', 'giaiTrinh': 'report',
                        'linkBaoCao': report_url, 'reporter': 'B_ADMIN',
                        'nguoiGiao': 'B_ADMIN', 'tenCV': 'forged edit'}, reports)
            if reports:
                row = task_row(prefix)
                record('SEC05 ' + ma + ' reporter identity', '[' + ma + ']' in row['nhat_ky_bao_cao'], True)
                record('SEC05 ' + ma + ' REPORT not generic edit', row['nguoi_giao'], giver)
                record('SEC05 ' + ma + ' REPORT attachment', row['file_bao_cao'], report_url)
            forwarded = task_write(ma + ' DELEGATE', '/api/tasks/forward',
                       {'idPhanCongGoc': prefix, 'nguoiNhanUyQuyen': 'A_MANAGER',
                        'nguoiGiao': 'B_ADMIN', 'phoiHopMoi': 'A_USER'}, reports)
            if reports:
                row = task_row(forwarded.get('id')) if forwarded.get('id') else None
                record('SEC05 ' + ma + ' child giver canonical', row.get('nguoi_giao') if row else None, receiver)
                record('SEC05 ' + ma + ' inherited attachment', row.get('file_giao_viec') if row else None, task_row(prefix)['file_giao_viec'])

        task_login('A_USER')
        for label, identifier in [('blank', ''), ('automatic', 'TỰ ĐỘNG'), ('ascii automatic', 'TU DONG'),
                                  ('suggested', None),
                                  ('unused forged giver', 'SEC05-UNUSED')]:
            before_ids = {row[0] for row in task_state()['9000000001']}
            if label == 'suggested':
                # Acquire only when this case is ready: prior creates consume codes.
                suggested = client.get('/api/tasks/suggested-code?prefix=A_USER')
                record('SEC05 suggested authenticated contract', suggested.status_code, 200)
                identifier = suggested.json()
                record('SEC05 suggested authenticated code', isinstance(identifier, str), True)
                record('SEC05 suggested ID unused before CREATE',
                       isinstance(identifier, str) and identifier not in before_ids, True)
            task_write('CREATE ' + label, '/api/tasks', {'idPhanCong': identifier, 'nguoiGiao': 'B_ADMIN',
                       'nguoiNhan': 'A_MANAGER', 'phoiHop': 'A_ADMIN', 'tenCV': 'legitimate create'}, True)
            created = [row for row in task_state()['9000000001'] if row[0] not in before_ids]
            record('SEC05 CREATE ' + label + ' one new row', len(created), 1)
            if label in ('suggested', 'unused forged giver'):
                row = task_row(identifier) if isinstance(identifier, str) else None
            else:
                row = task_row(created[0][0]) if len(created) == 1 else None
            record('SEC05 CREATE ' + label + ' row exists after CREATE', row is not None, True)
            record('SEC05 CREATE ' + label + ' canonical giver', row.get('nguoi_giao') if row else None, 'A_USER')

        for action in ['edit', 'report', 'remind', 'forward']:
            if action == 'edit':
                url, payload = '/api/tasks', {'idPhanCong': 'SEC05-MISSING', 'operation': 'edit', 'nguoiNhan': 'A_USER'}
            elif action == 'forward':
                url, payload = '/api/tasks/forward', {'idPhanCongGoc': 'SEC05-MISSING', 'nguoiNhanUyQuyen': 'A_USER'}
            else:
                url, payload = '/api/tasks/SEC05-MISSING/' + action, {'tienDo': 20, 'message': 'test'}
            task_write('missing ' + action, url, payload, False)
        record('SEC05 missing VIEW denied', client.get('/api/tasks/SEC05-MISSING').json().get('success'), False)
        task_write('receiver forged privileges EDIT', '/api/tasks', {'idPhanCong': 'A-TASK',
                   'operation': 'edit', 'role': 'ADMIN', 'actor': 'A_ADMIN', 'company_mst': '9000000002',
                   'nguoiGiao': 'A_USER', 'nguoiNhan': 'A_USER', 'link': '/static/uploads/hijacked.txt'}, False)
        task_write('foreign-only existing EDIT', '/api/tasks', {'idPhanCong': 'B-TASK', 'operation': 'edit',
                   'nguoiNhan': 'A_USER'}, False)
        task_write('CREATE foreign receiver', '/api/tasks', {'idPhanCong': 'SEC05-FOREIGN',
                   'nguoiNhan': 'B_USER'}, False)
        task_write('CREATE foreign CC', '/api/tasks', {'idPhanCong': 'SEC05-FOREIGN-CC',
                   'nguoiNhan': 'A_USER', 'phoiHop': 'B_MANAGER'}, False)
        task_write('foreign-only REPORT', '/api/tasks/B-TASK/report', {'tienDo': 10, 'status': 'test'}, False)
        task_write('foreign-only DIRECT', '/api/tasks/B-TASK/remind', {'message': 'test'}, False)
        task_write('foreign-only DELEGATE', '/api/tasks/forward', {'idPhanCongGoc': 'B-TASK',
                   'nguoiNhanUyQuyen': 'A_USER'}, False)
        task_write('receiver DELEGATE foreign target', '/api/tasks/forward', {'idPhanCongGoc': 'A-TASK',
                   'nguoiNhanUyQuyen': 'B_USER'}, False)
        task_write('receiver DELEGATE foreign CC', '/api/tasks/forward', {'idPhanCongGoc': 'A-TASK',
                   'nguoiNhanUyQuyen': 'A_USER', 'phoiHopMoi': 'B_USER'}, False)
        seed_task('SEC05-PATH-OTHER')
        other_before = task_row('SEC05-PATH-OTHER')
        task_write('REPORT body cannot override path', '/api/tasks/A-TASK/report',
                   {'id': 'SEC05-PATH-OTHER', 'tienDo': 50, 'status': 'Đang thực hiện', 'giaiTrinh': 'valid'}, True)
        record('SEC05 REPORT body target unchanged', task_row('SEC05-PATH-OTHER'), other_before)

        task_login('A_ADMIN')
        task_write('ADMIN CREATE on behalf', '/api/tasks', {'idPhanCong': 'SEC05-ON-BEHALF',
                   'operation': 'create', 'nguoiGiao': 'A_MANAGER', 'nguoiNhan': 'A_USER', 'phoiHop': 'A_ADMIN'}, True)
        record('SEC05 ADMIN on-behalf giver', task_row('SEC05-ON-BEHALF')['nguoi_giao'], 'A_MANAGER')
        for target, values in [('giver', {'nguoiGiao': 'B_ADMIN', 'nguoiNhan': 'A_USER'}),
                               ('receiver', {'nguoiGiao': 'A_ADMIN', 'nguoiNhan': 'B_USER'}),
                               ('CC', {'nguoiGiao': 'A_ADMIN', 'nguoiNhan': 'A_USER', 'phoiHop': 'B_MANAGER'})]:
            task_write('ADMIN CREATE foreign ' + target, '/api/tasks', dict(idPhanCong='SEC05-FOREIGN-' + target, **values), False)
        for key in ['nhatKyBaoCao', 'noiDungNhacNho', 'file_bao_cao']:
            task_write('generic history/report binding denied ' + key, '/api/tasks',
                       {'idPhanCong': 'A-TASK', key: 'forged', 'nguoiNhan': 'A_USER'}, False)
        for fields in [{'nguoiNhan': 'B_USER'}, {'phoiHop': 'B_MANAGER'}]:
            task_write('EDIT foreign targets ' + str(list(fields)), '/api/tasks', dict(idPhanCong='A-TASK', **fields), False)
        seed_task('SEC05-SAME-ID')
        seed_task('SEC05-SAME-ID', giver='B_ADMIN', receiver='B_USER', cc='B_MANAGER', mst='9000000002')
        b_before = task_row('SEC05-SAME-ID', '9000000002')
        task_write('same ID cannot select client tenant', '/api/tasks', {'idPhanCong': 'SEC05-SAME-ID',
                   'tenCV': 'A-only update', 'company_mst': '9000000002', 'MST': '9000000002',
                   'database_path': 'foreign.db'}, True)
        record('SEC05 same ID B unchanged', task_row('SEC05-SAME-ID', '9000000002'), b_before)
        record('SEC05 same ID A changed', task_row('SEC05-SAME-ID')['ten_cv'], 'A-only update')
        task_write('explicit CREATE existing ID denied', '/api/tasks', {'idPhanCong': 'A-TASK', 'operation': 'create'}, False)
        task_write('unknown intent denied', '/api/tasks', {'idPhanCong': 'SEC05-NEW', 'operation': 'invalid'}, False)

        for kind in ['anonymous', 'invalid session']:
            client.cookies.clear()
            if kind == 'invalid session':
                client.cookies.set('ams_session', 'invalid-signed-cookie')
            for url in ['/api/tasks', '/api/tasks/A-TASK', '/api/tasks/suggested-code?prefix=A_USER']:
                record('SEC05 ' + kind + ' read denied ' + url, client.get(url).json().get('success'), False)
            for url, data in [('/api/tasks', {'idPhanCong': 'SEC05-ANON', 'nguoiNhan': 'A_USER'}),
                              ('/api/tasks/A-TASK/report', {'tienDo': 10}),
                              ('/api/tasks/A-TASK/remind', {'message': 'forged'}),
                              ('/api/tasks/forward', {'idPhanCongGoc': 'A-TASK', 'nguoiNhanUyQuyen': 'A_USER'})]:
                task_write(kind + ' write ' + url, url, data, False)
        task_login('A_USER')
        record('SEC05 no Drive calls', len(drive_calls), 0)
        # 4B2: actual uploads and tenant-local committed objects, never URL claims.
        from services.file_binding_service import FileBindingService
        from models.models import Document
        from sqlalchemy.orm import Session as SASession

        def registry_state():
            with reg._connection() as conn:
                return {table: [tuple(r) for r in conn.execute('SELECT * FROM '+table+' ORDER BY 1')]
                        for table in ['files','bindings']}

        def document_state():
            state={}
            for mst in ['9000000001','9000000002']:
                db=mt.get_tenant_session(mst)
                state[mst]=sorted([tuple(getattr(d,c.name) for c in Document.__table__.columns)
                                   for d in db.query(Document).all()],key=lambda r:r[0])
                db.close()
            return state

        def all_state():
            return (task_state(),document_state(),registry_state(),file_state(),len(drive_calls))

        def registered(url):
            return reg.get_storage_record(Config.UPLOAD_STORAGE_ROOT_ID,FileBindingService.local_name(url))

        def slots(object_id,field='file_giao_viec',kind='TASK'):
            return reg.slot_bindings('9000000001',kind,object_id,field)

        def bwrite(name,path,payload,allow=True):
            before=all_state()
            response=client.post(path,json=payload)
            try:
                data=response.json()
            except ValueError:
                data={}
            record('B4B2 BIND '+name+' success',data.get('success'),allow)
            if not allow:
                after=all_state()
                for i,label in enumerate(['Task A/B','Document A/B','registry','physical hashes','provider']):
                    record('B4B2 BIND '+name+' denied '+label,after[i]==before[i],True)
            return data

        def save_attachment(identifier,url,operation=None):
            body={'idPhanCong':identifier,'tenCV':'4B2 synthetic','nguoiNhan':'A_USER',
                  'phoiHop':'A_MANAGER','link':url}
            if operation:
                body['operation']=operation
            return body

        def synthetic_task(identifier,url):
            return bwrite(identifier,'/api/tasks',save_attachment(identifier,url,'create'))

        for role in ['ADMIN','MANAGER','USER']:
            task_login('A_'+role)
            content=('4B2-'+role).encode()
            url,path=local_upload(content)
            row=registered(url)
            for key,expected in [('tenant_id','9000000001'),('uploader_id','A_'+role),
                                 ('state','UNBOUND'),('classification','PRIVATE'),
                                 ('size',len(content)),('sha256',hashlib.sha256(content).hexdigest()),
                                 ('storage_root_id',Config.UPLOAD_STORAGE_ROOT_ID)]:
                record('B4B2 UPLOAD '+role+' '+key,row[key],expected)
            record('B4B2 UPLOAD '+role+' UUID locator',bool(re.fullmatch('[0-9a-f]{32}\\.txt',path.name)),True)
            record('B4B2 UPLOAD '+role+' expiry24h',
                   23.99 < (datetime.fromisoformat(row['expires_at'])-datetime.fromisoformat(row['created_at'])).total_seconds()/3600 < 24.01,True)
        client.cookies.clear()
        before=all_state()
        response=client.post('/api/drive/upload-local',files={'file':('anonymous.txt',b'no','text/plain')})
        record('B4B2 UPLOAD anonymous401',response.status_code,401)
        record('B4B2 UPLOAD anonymous zero mutation',all_state(),before)
        response=client.post('/api/drive/upload-local',headers=invalid_cookie,files={'file':('invalid.txt',b'no','text/plain')})
        record('B4B2 UPLOAD invalid401',response.status_code,401)
        record('B4B2 UPLOAD invalid zero mutation',all_state(),before)
        task_login('A_USER')
        spoof=client.post('/api/drive/upload-local',data={'tenant_id':'9000000002','uploader_id':'B_ADMIN',
                          'file_id':'forged','size':'999','sha256':'forged'},files={'file':('spoof.txt',b'actual','text/plain')}).json()
        spoof_row=registered(spoof['url'])
        record('B4B2 UPLOAD spoofed tenant ignored',spoof_row['tenant_id'],'9000000001')
        record('B4B2 UPLOAD spoofed uploader ignored',spoof_row['uploader_id'],'A_USER')
        record('B4B2 UPLOAD opaque identity additive',spoof.get('file_id'),spoof_row['file_id'])
        before=all_state()
        with patch.object(FileRegistry,'initialize_registry',side_effect=RegistryError('Injected unavailable')):
            response=client.post('/api/drive/upload-local',files={'file':('fail.txt',b'no','text/plain')})
        record('B4B2 FAILURE upload registry unavailable',response.json().get('success'),False)
        record('B4B2 FAILURE registry unavailable zero mutation',all_state(),before)
        real_open=open
        def broken_physical(path,mode='r',*args,**kwargs):
            if mode=='xb' and Path(path).resolve().parent==Path(Config.UPLOAD_DIR).resolve():
                raise OSError('Injected physical failure')
            return real_open(path,mode,*args,**kwargs)
        before_ids=set(r[0] for r in registry_state()['files'])
        before_bytes=file_state()
        with patch('builtins.open',side_effect=broken_physical):
            response=client.post('/api/drive/upload-local',files={'file':('physical.txt',b'no','text/plain')})
        record('B4B2 FAILURE physical upload unsuccessful',response.json().get('success'),False)
        records=[r for r in registry_state()['files'] if r[0] not in before_ids]
        record('B4B2 FAILURE physical failure no usable metadata',bool(records) and all(r[10] in ('WRITING','REVOKED') for r in records),True)
        record('B4B2 FAILURE physical failure bytes unchanged',file_state(),before_bytes)
        # Observe actual WRITING intent before exclusive physical open.
        observed=[]
        def observe_write(path,mode='r',*args,**kwargs):
            if mode=='xb' and Path(path).resolve().parent==Path(Config.UPLOAD_DIR).resolve():
                observed.append(reg.get_storage_record(Config.UPLOAD_STORAGE_ROOT_ID,Path(path).name)['state'])
            return real_open(path,mode,*args,**kwargs)
        with patch('builtins.open',side_effect=observe_write):
            ordered_url,_=local_upload(b'ordered lifecycle')
        record('B4B2 UPLOAD WRITING precedes physical open',observed,['WRITING'])
        record('B4B2 UPLOAD completes to UNBOUND',registered(ordered_url)['state'],'UNBOUND')
        before_ids=set(r[0] for r in registry_state()['files'])
        with patch.object(FileRegistry,'complete_unbound',side_effect=RegistryError('Injected completion')):
            response=client.post('/api/drive/upload-local',files={'file':('completion.txt',b'written but not usable','text/plain')})
        records=[r for r in registry_state()['files'] if r[0] not in before_ids]
        record('B4B2 FAILURE upload completion denied',response.json().get('success'),False)
        record('B4B2 FAILURE upload completion no usable authority',bool(records) and all(r[10] in ('WRITING','REVOKED') for r in records),True)

        # New Task binding, exact replacement, shared parent/child, clearing.
        task_login('A_USER')
        a_url,a_path=local_upload(b'4B2 assignment A')
        synthetic_task('B4B2-TASK',a_url)
        a=registered(a_url)
        active=slots('B4B2-TASK')
        record('B4B2 BIND Task exact committed field',task_row('B4B2-TASK')['file_giao_viec'],a_url)
        record('B4B2 BIND Task active',[(b['file_id'],b['state']) for b in active],[(a['file_id'],'ACTIVE')])
        record('B4B2 BIND file BOUND',registered(a_url)['state'],'BOUND')
        # Same actor is also receiver, so approved delegation is legitimate.
        child=bwrite('trusted forward','/api/tasks/forward',{'idPhanCongGoc':'B4B2-TASK','nguoiNhanUyQuyen':'A_MANAGER'})
        child_id=child.get('id','missing')
        record('B4B2 BIND child inherits same bytes',task_row(child_id)['file_giao_viec'] if task_row(child_id) else None,a_url)
        record('B4B2 BIND child independent ACTIVE',[(b['file_id'],b['state']) for b in slots(child_id)],[(a['file_id'],'ACTIVE')])
        record('B4B2 BIND parent remains ACTIVE',len(reg.list_active_bindings(a['file_id'],'9000000001')),2)
        b_url,_=local_upload(b'4B2 assignment B')
        b=registered(b_url)
        pending=reg.create_pending_binding(b['file_id'],'9000000001','TASK','B4B2-TASK','file_giao_viec',replacement=True)
        record('B4B2 REPLACE preparing B preserves A',reg.get_binding(active[0]['binding_id'],'9000000001')['state'],'ACTIVE')
        record('B4B2 REPLACE reserved B PENDING',reg.get_binding(pending,'9000000001')['state'],'PENDING')
        c_url,_=local_upload(b'4B2 contender C')
        try:
            reg.create_pending_binding(registered(c_url)['file_id'],'9000000001','TASK','B4B2-TASK','file_giao_viec',replacement=True)
            denied=False
        except RegistryError:
            denied=True
        record('B4B2 CONCURRENCY competing reservation denied',denied,True)
        record('B4B2 CONCURRENCY exact reservation retry',reg.create_pending_binding(b['file_id'],'9000000001','TASK','B4B2-TASK','file_giao_viec',replacement=True),pending)
        bwrite('replacement','/api/tasks',save_attachment('B4B2-TASK',b_url,'edit'))
        record('B4B2 REPLACE B ACTIVE',reg.get_binding(pending,'9000000001')['state'],'ACTIVE')
        record('B4B2 REPLACE A exact slot revoked',reg.get_binding(active[0]['binding_id'],'9000000001')['state'],'REVOKED')
        record('B4B2 REPLACE A child preserved',[(r['object_id'],r['state']) for r in reg.list_active_bindings(a['file_id'],'9000000001')],[(child_id,'ACTIVE')])
        before=registry_state()
        bwrite('exact retry','/api/tasks',save_attachment('B4B2-TASK',b_url,'edit'))
        record('B4B2 CONCURRENCY exact retry metadata unchanged',registry_state(),before)
        bwrite('clear assignment','/api/tasks',save_attachment('B4B2-TASK','','edit'))
        record('B4B2 REPLACE clear exact slot',slots('B4B2-TASK'),[])
        record('B4B2 REPLACE shared child remains',len(reg.list_active_bindings(a['file_id'],'9000000001')),1)
        record('B4B2 REPLACE physical A preserved',a_path.read_bytes()==b'4B2 assignment A',True)

        # Denial precedes business and sidecar mutations.
        for actor in ['A_USER_RECEIVER','A_USER_CC','A_USER_OTHER']:
            task_login(actor)
            seed_task('B4B2-DENIED-'+actor,giver='A_ADMIN',receiver='A_USER_RECEIVER',cc='A_USER_CC')
            url,_=local_upload(b'denied actor own upload')
            bwrite(actor+' EDIT','/api/tasks',save_attachment('B4B2-DENIED-'+actor,url,'edit'),False)
        task_login('B_USER','9000000002')
        foreign_url,_=local_upload(b'foreign')
        task_login('A_MANAGER')
        other_url,_=local_upload(b'other uploader')
        task_login('A_USER')
        expired_url,_=local_upload(b'expired')
        revoked_url,_=local_upload(b'revoked')
        unknown_url,_=local_upload(b'unknown')
        with reg._connection(mutation=True) as conn:
            conn.execute('UPDATE files SET expires_at=? WHERE storage_name=?',((datetime.now(timezone.utc)-timedelta(hours=1)).isoformat(),FileBindingService.local_name(expired_url)))
            conn.execute("UPDATE files SET classification='UNKNOWN' WHERE storage_name=?",(FileBindingService.local_name(unknown_url),))
        reg.mark_revoked(registered(revoked_url)['file_id'],'9000000001')
        invalid_urls={'foreign tenant':foreign_url,'other uploader':other_url,'expired':expired_url,
                      'revoked':revoked_url,'UNKNOWN':unknown_url,'unregistered':'/static/uploads/not-registered.txt',
                      'absolute alias':'https://example.invalid'+a_url,'encoded traversal':'/static/uploads/%2e%2e%2fsecret.txt',
                      'backslash':'/static/uploads/..\\secret.txt','slash alias':'/static/uploads/sub/file.txt',
                      'encoded prefix':'/%73tatic/uploads/file.txt','query alias':a_url+'?id=forged'}
        for label,url in invalid_urls.items():
            bwrite(label,'/api/tasks',save_attachment('B4B2-INVALID-'+label,url,'create'),False)
        task_login('A_ADMIN')
        bwrite('ADMIN no UNBOUND override','/api/tasks',save_attachment('B4B2-ADMIN-UNBOUND',spoof['url'],'create'),False)
        admin_url,_=local_upload(b'admin')
        synthetic_task('B4B2-ADMIN',admin_url)

        # Report field slot is distinct; reporter is the current receiver.
        task_login('A_USER')
        report_url,_=local_upload(b'4B2 report')
        bwrite('receiver report','/api/tasks/B4B2-ADMIN/report',{'tienDo':45,'linkBaoCao':report_url,'idPhanCong':'B4B2-TASK'})
        record('B4B2 BIND report exact path not body',task_row('B4B2-ADMIN')['file_bao_cao'],report_url)
        record('B4B2 BIND report separate field slot',[(r['field_slot'],r['state']) for r in slots('B4B2-ADMIN','file_bao_cao')],[('file_bao_cao','ACTIVE')])
        for actor in ['A_USER_GIVER','A_MANAGER','A_USER_OTHER']:
            task_login(actor)
            url,_=local_upload(b'forbidden report')
            # giver is explicitly the tested actor; CC is A_MANAGER.
            identifier='B4B2-REPORT-DENIED-'+actor
            seed_task(identifier,giver=actor if actor=='A_USER_GIVER' else 'A_ADMIN',receiver='A_USER',cc='A_MANAGER')
            bwrite(actor+' REPORT','/api/tasks/'+identifier+'/report',{'tienDo':40,'linkBaoCao':url},False)
        task_login('A_ADMIN')
        admin_report,_=local_upload(b'admin report')
        bwrite('ADMIN report','/api/tasks/B4B2-ADMIN/report',{'tienDo':60,'linkBaoCao':admin_report})
        record('B4B2 REPLACE report replaced once',len(slots('B4B2-ADMIN','file_bao_cao')),1)
        bwrite('clear report','/api/tasks/B4B2-ADMIN/report',{'tienDo':60,'linkBaoCao':''})
        record('B4B2 REPLACE report clear',slots('B4B2-ADMIN','file_bao_cao'),[])

        # DocumentService remains unchanged; route wraps commit and exact reload.
        doc_a,_=local_upload(b'document A')
        doc_payload={'maTL':'B4B2-DOC','tenTL':'synthetic document','loai':'test','linkFile':doc_a}
        bwrite('Document create','/api/documents',doc_payload)
        record('B4B2 BIND Document exact ACTIVE',[(r['file_id'],r['state']) for r in slots('B4B2-DOC','link_file','DOCUMENT')],[(registered(doc_a)['file_id'],'ACTIVE')])
        doc_b,_=local_upload(b'document B')
        bwrite('Document replace','/api/documents/update',{**doc_payload,'linkFile':doc_b})
        record('B4B2 REPLACE Document old revoked',reg.list_active_bindings(registered(doc_a)['file_id'],'9000000001'),[])
        record('B4B2 REPLACE Document new ACTIVE',len(slots('B4B2-DOC','link_file','DOCUMENT')),1)
        bwrite('Document foreign','/api/documents/update',{**doc_payload,'linkFile':foreign_url},False)
        bwrite('Document unregistered','/api/documents',{'maTL':'B4B2-LEGACY-DOC','tenTL':'unknown','linkFile':'/static/uploads/legacy-document.txt'},False)
        task_login('A_USER')
        bwrite('Document unauthorized','/api/documents/update',{**doc_payload,'linkFile':spoof['url']},False)
        task_login('A_ADMIN')
        bwrite('Document clear','/api/documents/update',{**doc_payload,'linkFile':''})
        record('B4B2 REPLACE Document cleared',slots('B4B2-DOC','link_file','DOCUMENT'),[])
        db=mt.get_tenant_session('9000000001')
        db.add(Document(ma_tl='B4B2-DOC-LEGACY',ten_tl='synthetic legacy',loai='test',link_file='/static/uploads/old-document.txt'))
        db.commit();db.close()
        before=registry_state()
        bwrite('Document unchanged legacy','/api/documents/update',{'maTL':'B4B2-DOC-LEGACY','tenTL':'synthetic legacy edited','linkFile':'/static/uploads/old-document.txt'})
        record('B4B2 BIND Document legacy no ownership claim',registry_state()==before,True)

        # External and LOCAL_DOCS remain business references without ownership.
        for label,url in [('external','https://example.invalid/document.pdf'),('local docs','/local_docs/manual.pdf')]:
            before=registry_state()
            synthetic_task('B4B2-'+label,url)
            record('B4B2 BIND '+label+' no ownership claim',registry_state(),before)
        seed_task('B4B2-LEGACY',giver='A_USER',receiver='A_USER')
        task_login('A_USER')
        before=registry_state()
        bwrite('unchanged legacy','/api/tasks',save_attachment('B4B2-LEGACY','/static/uploads/synthetic-task.txt','edit'))
        legacy_child=bwrite('legacy forward','/api/tasks/forward',{'idPhanCongGoc':'B4B2-LEGACY','nguoiNhanUyQuyen':'A_MANAGER'})
        record('B4B2 BIND legacy no registry claim',registry_state(),before)
        record('B4B2 BIND legacy child no trusted binding',slots(legacy_child.get('id','missing')),[])

        # Fault boundaries preserve previous ACTIVE; never fabricate success.
        fail_a,_=local_upload(b'failure original')
        synthetic_task('B4B2-FAILURE',fail_a)
        fail_active=slots('B4B2-FAILURE')[0]
        fail_b,_=local_upload(b'failure replacement')
        before_task=task_row('B4B2-FAILURE')
        with patch.object(SASession,'commit',side_effect=RuntimeError('Injected business commit')):
            result=client.post('/api/tasks',json=save_attachment('B4B2-FAILURE',fail_b,'edit')).json()
        record('B4B2 FAILURE commit response denied',result.get('success'),False)
        record('B4B2 FAILURE commit DB unchanged',task_row('B4B2-FAILURE'),before_task)
        record('B4B2 FAILURE commit old ACTIVE',reg.get_binding(fail_active['binding_id'],'9000000001')['state'],'ACTIVE')
        record('B4B2 FAILURE commit replacement never ACTIVE',reg.list_active_bindings(registered(fail_b)['file_id'],'9000000001'),[])
        original_reload=FileBindingService.reload
        def wrong_reload(service,model,identifier):
            row=original_reload(service,model,identifier)
            return SimpleNamespace(file_giao_viec='mismatch',link_file='mismatch') if identifier in ['B4B2-FAILURE','B4B2-DOC-FAIL'] else row
        with patch.object(FileBindingService,'reload',wrong_reload):
            result=client.post('/api/tasks',json=save_attachment('B4B2-FAILURE',fail_b,'edit')).json()
        record('B4B2 FAILURE revalidation response denied',result.get('success'),False)
        record('B4B2 FAILURE postcommit business remains committed',task_row('B4B2-FAILURE')['file_giao_viec'],fail_b)
        record('B4B2 FAILURE revalidation old ACTIVE',reg.get_binding(fail_active['binding_id'],'9000000001')['state'],'ACTIVE')
        record('B4B2 FAILURE revalidation replacement never ACTIVE',reg.list_active_bindings(registered(fail_b)['file_id'],'9000000001'),[])
        with patch.object(FileRegistry,'activate_binding',side_effect=RegistryError('Injected activation')):
            result=client.post('/api/tasks',json=save_attachment('B4B2-FAILURE',fail_b,'edit')).json()
        record('B4B2 FAILURE activation response denied',result.get('success'),False)
        record('B4B2 FAILURE activation old ACTIVE',reg.get_binding(fail_active['binding_id'],'9000000001')['state'],'ACTIVE')
        record('B4B2 FAILURE activation no replacement ACTIVE',reg.list_active_bindings(registered(fail_b)['file_id'],'9000000001'),[])
        before=all_state()
        with patch.object(FileRegistry,'create_pending_binding',side_effect=RegistryError('Injected reservation')):
            result=client.post('/api/tasks',json=save_attachment('B4B2-FAILURE',fail_b,'edit')).json()
        record('B4B2 FAILURE reservation response denied',result.get('success'),False)
        record('B4B2 FAILURE reservation zero mutation',all_state(),before)
        # A failed clear must not prematurely revoke existing authority.
        with patch.object(SASession,'commit',side_effect=RuntimeError('Injected clear commit')):
            result=client.post('/api/tasks',json=save_attachment('B4B2-FAILURE','','edit')).json()
        record('B4B2 FAILURE clear unsuccessful',result.get('success'),False)
        record('B4B2 FAILURE clear old ACTIVE preserved',reg.get_binding(fail_active['binding_id'],'9000000001')['state'],'ACTIVE')
        # Forward failure rolls back child and parent status; no child authority.
        before_tasks=task_state()
        before_active=len(reg.list_active_bindings(a['file_id'],'9000000001'))
        task_login('A_MANAGER')
        with patch.object(SASession,'commit',side_effect=RuntimeError('Injected child commit')):
            result=client.post('/api/tasks/forward',json={'idPhanCongGoc':child_id,'nguoiNhanUyQuyen':'A_USER'}).json()
        record('B4B2 FAILURE child unsuccessful',result.get('success'),False)
        record('B4B2 FAILURE child no business mutation',task_state(),before_tasks)
        record('B4B2 FAILURE child no new ACTIVE',len(reg.list_active_bindings(a['file_id'],'9000000001')),before_active)

        task_login('A_ADMIN')
        doc_fail,_=local_upload(b'document mismatch')
        before_documents=document_state()
        with patch.object(SASession,'commit',side_effect=RuntimeError('Injected document commit')):
            result=client.post('/api/documents',json={'maTL':'B4B2-DOC-FAIL','tenTL':'fail','linkFile':doc_fail}).json()
        record('B4B2 FAILURE Document commit denied',result.get('success'),False)
        record('B4B2 FAILURE Document commit business unchanged',document_state(),before_documents)
        record('B4B2 FAILURE Document commit no ACTIVE',reg.list_active_bindings(registered(doc_fail)['file_id'],'9000000001'),[])
        with patch.object(FileBindingService,'reload',wrong_reload):
            result=client.post('/api/documents',json={'maTL':'B4B2-DOC-FAIL','tenTL':'fail','linkFile':doc_fail}).json()
        record('B4B2 FAILURE Document revalidation denied',result.get('success'),False)
        record('B4B2 FAILURE Document no ACTIVE',reg.list_active_bindings(registered(doc_fail)['file_id'],'9000000001'),[])
        task_login('A_USER')
        report_fail,_=local_upload(b'report commit fails')
        before_report=task_row('B4B2-ADMIN')
        with patch.object(SASession,'commit',side_effect=RuntimeError('Injected report commit')):
            result=client.post('/api/tasks/B4B2-ADMIN/report',json={'tienDo':80,'linkBaoCao':report_fail}).json()
        record('B4B2 FAILURE report commit denied',result.get('success'),False)
        record('B4B2 FAILURE report commit business unchanged',task_row('B4B2-ADMIN'),before_report)
        record('B4B2 FAILURE report commit no ACTIVE',reg.list_active_bindings(registered(report_fail)['file_id'],'9000000001'),[])
        bwrite('report foreign tenant','/api/tasks/B4B2-ADMIN/report',{'tienDo':80,'linkBaoCao':foreign_url},False)

        # Concurrent different replacements use SQLite reservations, not a lock.
        task_login('A_USER')
        race_a,_=local_upload(b'race A')
        synthetic_task('B4B2-RACE',race_a)
        race_urls=[local_upload(b'race B')[0],local_upload(b'race C')[0]]
        race_barrier=threading.Barrier(2)
        def replace_race(url):
            race_barrier.wait(timeout=20)
            return client.post('/api/tasks',json=save_attachment('B4B2-RACE',url,'edit')).json().get('success')
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes=list(pool.map(replace_race,race_urls))
        live=slots('B4B2-RACE')
        record('B4B2 CONCURRENCY replacement at least one succeeds',any(outcomes),True)
        record('B4B2 CONCURRENCY replacement exactly one ACTIVE',len([r for r in live if r['state']=='ACTIVE']),1)
        active=[r for r in live if r['state']=='ACTIVE']
        record('B4B2 CONCURRENCY ACTIVE matches persisted URL',active[0]['file_id'] if active else None,registered(task_row('B4B2-RACE')['file_giao_viec'])['file_id'])
        record('B4B2 CONCURRENCY stale PENDING no authority',all(r['state']=='ACTIVE' for r in live),True)

        # Explicit v1 incompatibility: no destructive automatic upgrade.
        v1_path=Config.FILE_REGISTRY_ROOT/'v1-incompatible.sqlite3'
        v1=FileRegistry(v1_path);v1.initialize_registry()
        v1.register_writing('9000000001','A_USER','LOCAL_UPLOADS','v1-preserved.txt','v1 preserved')
        with v1._connection(mutation=True) as conn:
            conn.execute('PRAGMA user_version=1')
        before_v1=v1_path.read_bytes()
        try:
            v1.initialize_registry()
            version_denied=False
        except RegistryError as exc:
            version_denied='migration' in str(exc)
        record('B4B2 SCHEMA v1 explicit migration error',version_denied,True)
        record('B4B2 SCHEMA incompatible bytes preserved',v1_path.read_bytes()==before_v1,True)
        record('B4B2 SCHEMA current version',FileRegistry.VERSION,3)
        broken_path=Config.FILE_REGISTRY_ROOT/'missing-constraint.sqlite3'
        broken=FileRegistry(broken_path);broken.initialize_registry()
        with broken._connection(mutation=True) as conn:
            conn.execute('DROP INDEX binding_slot_pending')
        original_bytes=broken_path.read_bytes()
        try:
            broken.initialize_registry()
            constraints_denied=False
        except RegistryError:
            constraints_denied=True
        record('B4B2 SCHEMA missing replacement constraint denied',constraints_denied,True)
        record('B4B2 SCHEMA missing constraint no reset',broken_path.read_bytes()==original_bytes,True)
        record('B4B2 BIND no provider mutation',len(drive_calls),0)
        # 4B3 online private gateway acceptance, never PWA/legacy onboarding.
        import services.file_access_service as access
        def read_fingerprints():
            paths=list((appdir/'database').rglob('*.db*'))+[appdir/'qlcv.db',reg.path]
            paths+=list((appdir/'static/uploads').iterdir())
            return {str(p): (p.stat().st_size,p.stat().st_mtime_ns,hashlib.sha256(p.read_bytes()).hexdigest())
                    for p in paths if p.is_file() and not p.is_symlink()}

        def gread(category,name,url,expected,*,method='GET',headers=None):
            before=read_fingerprints()
            calls=len(drive_calls)
            response=client.request(method,url,headers=headers or {},follow_redirects=False)
            record(category+' '+name+' status',response.status_code,expected)
            record('GATEWAY_ZERO_MUTATION '+name+' fingerprints',read_fingerprints()==before,True)
            record('GATEWAY_ZERO_MUTATION '+name+' provider',len(drive_calls)==calls,True)
            if expected in (401,404):
                record(category+' '+name+' no private metadata',not any(h in response.headers for h in
                       ['etag','last-modified','content-range','location']),True)
                record(category+' '+name+' uniform error',response.content in (b'',access.denied(expected).body),True)
            record(category+' '+name+' no-store',response.headers.get('cache-control'),'private, no-store')
            return response

        task_login('A_USER')
        gateway_url,gateway_path=local_upload(b'0123456789 gateway private sentinel')
        gateway_row=registered(gateway_url)
        gread('GATEWAY_UNBOUND','uploader',gateway_url,200)
        client.cookies.clear()
        gread('GATEWAY_AUTH','anonymous',gateway_url,401)
        gread('GATEWAY_AUTH','invalid',gateway_url,401,headers=invalid_cookie)
        gread('GATEWAY_AUTH','missing anonymous', '/static/uploads/missing.txt',401)
        task_login('A_ADMIN')
        gread('GATEWAY_UNBOUND','ADMIN no override',gateway_url,404)
        task_login('A_MANAGER')
        gread('GATEWAY_UNBOUND','other actor',gateway_url,404)
        task_login('B_USER','9000000002')
        gread('GATEWAY_TENANT','foreign UNBOUND',gateway_url,404)
        # Same canonical actor code in A/B still cannot read A's blob.
        db=mt.get_tenant_session('9000000002')
        db.add(Employee(ma_nv='A_USER',ten_nv='synthetic duplicate',quyen='USER',mat_khau=hash_password(password)))
        db.commit();db.close()
        task_login('A_USER','9000000002')
        gread('GATEWAY_TENANT','same employee foreign tenant',gateway_url,404)
        gread('GATEWAY_TENANT','forged tenant query',gateway_url+'?tenant=9000000001&MST=9000000001&role=ADMIN&actor=A_USER',404)
        task_login('A_USER')
        for label,url in [('expired',expired_url),('revoked',revoked_url),('UNKNOWN',unknown_url)]:
            gread('GATEWAY_UNBOUND',label,url,404)
        task_login('A_ADMIN')
        gread('GATEWAY_UNBOUND','ADMIN UNKNOWN',unknown_url,404)
        writing=reg.register_writing('9000000001','A_ADMIN','LOCAL_UPLOADS','gateway-writing.txt','writing')
        (appdir/'static/uploads/gateway-writing.txt').write_bytes(b'writing private')
        gread('GATEWAY_UNBOUND','WRITING','/static/uploads/gateway-writing.txt',404)
        legacy_path=appdir/'static/uploads/gateway-legacy.txt'
        legacy_path.write_bytes(b'legacy private')
        gread('GATEWAY_FAIL_CLOSED','unregistered physical','/static/uploads/gateway-legacy.txt',404)
        gread('GATEWAY_FAIL_CLOSED','missing physical reference','/static/uploads/missing.txt',404)
        task_login('A_USER')
        # Exact route precedence must be demonstrated by real response.
        response=gread('GATEWAY_STATIC_BYPASS','canonical gateway wins',gateway_url,200)
        record('GATEWAY_STATIC_BYPASS gateway marker',response.headers.get('x-qlcv-file-gateway'),'1')
        # Content comparison is boolean (JSON report never contains raw bytes).
        record('GATEWAY_STATIC_BYPASS actual sentinel',response.content==b'0123456789 gateway private sentinel',True)
        client.cookies.clear()
        name=gateway_url.rsplit('/',1)[1]
        variants=['/static//uploads/'+name,'/static/uploads//'+name,'/static/./uploads/'+name,
                  '/static/uploads/../uploads/'+name,'/static/%75ploads/'+name,
                  '/static/UPLOADS/'+name,'/static/uploads%2f'+name,'/static/uploads%5c'+name,
                  '/static/uploads/%2e%2e%2f'+name,'/static/uploads/%252e%252e%252f'+name,
                  '/static/uploads/..%5c'+name,'/static/uploads/C:%5c'+name,
                  '/static/uploads/%2f'+name,'/static/uploads/%00'+name,
                  '/static/uploads/file:%2f%2f'+name,'/static/uploads/%5c%5cserver%5c'+name]
        for i,url in enumerate(variants):
            before=read_fingerprints()
            result=client.get(url,follow_redirects=False)
            record('GATEWAY_STATIC_BYPASS alias '+str(i)+' denied',result.status_code in (401,404),True)
            record('GATEWAY_STATIC_BYPASS alias '+str(i)+' no sentinel',b'gateway private sentinel' not in result.content,True)
            record('GATEWAY_ZERO_MUTATION alias '+str(i),read_fingerprints()==before,True)
        # Direct parent app invocation also excludes uploads, independent of route order.
        import asyncio
        parent=next(r.app for r in app.app.routes if getattr(r,'path',None)=='/static')
        result=asyncio.run(parent.get_response('uploads/'+name,{'type':'http','method':'GET','path':gateway_url,'headers':[]}))
        record('GATEWAY_STATIC_BYPASS direct parent denied',result.status_code,404)
        task_login('A_USER')
        for invalid_name in ['', '.', '..','a/b','a\\b','C:\\file','\\\\server\\file','%252e%252e','a\x00b','file://test','/absolute']:
            record('GATEWAY_PATH basename '+repr(invalid_name),access.storage_basename(invalid_name),False)
        # Real ASGI raw path with alias must be denied even if decoded path looks canonical.
        from starlette.requests import Request as StarletteRequest
        cookie=client.cookies.get('ams_session')
        request=StarletteRequest({'type':'http','method':'GET','path':gateway_url,'raw_path':('/static/%75ploads/'+name).encode(),
                                 'query_string':b'','headers':[(b'cookie',('ams_session='+cookie).encode())]})
        db=mt.get_tenant_session('9000000001')
        record('GATEWAY_PATH raw encoded alias denied',access.gateway(request,name,db).status_code,404)
        db.close()

        # Bound Task READ matrix for BOTH exact slots; no uploader override for BOUND.
        task_login('A_ADMIN')
        task_urls={}
        for slot in ['file_giao_viec','file_bao_cao']:
            url,_=local_upload(('task gateway '+slot).encode())
            identifier='GATEWAY-'+slot
            seed_task(identifier,giver='A_USER_GIVER',receiver='A_USER_RECEIVER',cc='A_USER_CC')
            db=mt.get_tenant_session('9000000001');obj=db.get(Task,identifier);setattr(obj,slot,url);db.commit();db.close()
            binding=reg.create_pending_binding(registered(url)['file_id'],'9000000001','TASK',identifier,slot)
            reg.activate_binding(binding,'9000000001')
            task_urls[slot]=(url,identifier,binding)
            for actor,expected in [('A_ADMIN',200),('A_USER_GIVER',200),('A_USER_RECEIVER',200),('A_USER_CC',200),('A_USER_OTHER',404)]:
                task_login(actor);gread('GATEWAY_TASK',slot+' '+actor,url,expected)
        task_login('B_ADMIN','9000000002')
        gread('GATEWAY_TENANT','foreign BOUND',task_urls['file_giao_viec'][0],404)
        task_login('A_USER_OTHER')
        gread('GATEWAY_TENANT','forged ADMIN headers',task_urls['file_giao_viec'][0]+'?role=ADMIN',404,
              headers={'X-Tenant':'9000000001','X-Actor':'A_ADMIN','X-Role':'ADMIN'})
        task_login('A_USER_GIVER')
        url,identifier,binding=task_urls['file_giao_viec']
        db=mt.get_tenant_session('9000000001');obj=db.get(Task,identifier);obj.file_giao_viec='https://example.invalid/changed';db.commit();db.close()
        gread('GATEWAY_LIVE_REVALIDATION','Task changed field',url,404)
        db=mt.get_tenant_session('9000000001');obj=db.get(Task,identifier);obj.file_giao_viec=url;obj.nguoi_giao='A_ADMIN';db.commit();db.close()
        gread('GATEWAY_LIVE_REVALIDATION','Task relationship lost',url,404)
        task_login('A_ADMIN')
        db=mt.get_tenant_session('9000000001');db.delete(db.get(Task,identifier));db.commit();db.close()
        gread('GATEWAY_LIVE_REVALIDATION','Task deleted',url,404)
        task_login('A_USER_RECEIVER')
        report_url,report_task,_=task_urls['file_bao_cao']
        db=mt.get_tenant_session('9000000001');db.get(Task,report_task).file_bao_cao='https://example.invalid/replaced';db.commit();db.close()
        gread('GATEWAY_LIVE_REVALIDATION','report field changed',report_url,404)
        # Real trusted forward union: A_USER can read parent, A_MANAGER child.
        for actor,expected in [('A_USER',200),('A_MANAGER',200),('A_USER_OTHER',404)]:
            task_login(actor);gread('GATEWAY_TASK','forward union '+actor,a_url,expected)
        # file A now only child binding: add a denied parent binding for union proof.
        task_login('A_ADMIN')
        seed_task('GATEWAY-UNION-DENIED',giver='A_ADMIN',receiver='A_USER_RECEIVER',cc='')
        db=mt.get_tenant_session('9000000001');obj=db.get(Task,'GATEWAY-UNION-DENIED');obj.file_giao_viec=a_url;db.commit();db.close()
        extra=reg.create_pending_binding(registered(a_url)['file_id'],'9000000001','TASK','GATEWAY-UNION-DENIED','file_giao_viec')
        reg.activate_binding(extra,'9000000001')
        task_login('A_MANAGER');gread('GATEWAY_TASK','denied A allowed child union',a_url,200)
        task_login('A_USER_RECEIVER');gread('GATEWAY_TASK','parent only union',a_url,200)
        task_login('A_ADMIN');gread('GATEWAY_TASK','both parent child union',a_url,200)
        task_login('A_USER_OTHER');gread('GATEWAY_TASK','both bindings denied',a_url,404)
        # PENDING/unsupported/revoked never grants BOUND authority.
        task_login('A_ADMIN')
        no_acl_url,_=local_upload(b'no object authority')
        fid=registered(no_acl_url)['file_id']
        pending=reg.create_pending_binding(fid,'9000000001','TASK','missing-object','file_giao_viec')
        with reg._connection(mutation=True) as conn:
            conn.execute("UPDATE files SET state='BOUND' WHERE file_id=?",(fid,))
        gread('GATEWAY_TASK','PENDING alone',no_acl_url,404)
        reg.activate_binding(pending,'9000000001')
        gread('GATEWAY_LIVE_REVALIDATION','missing live Task',no_acl_url,404)
        reg.revoke_binding(pending,'9000000001')
        gread('GATEWAY_TASK','revoked binding',no_acl_url,404)

        # Current Document department/manager/subordinate rules, unchanged.
        db=mt.get_tenant_session('9000000001')
        for actor,dept in [('A_USER','D1'),('A_MANAGER','D2'),('A_USER_OTHER','D3')]:
            db.get(Employee,actor).phong_ban=dept
        db.get(Employee,'A_USER').nguoi_ql='A_MANAGER'
        db.commit();db.close()
        document_url,_=local_upload(b'document gateway')
        doc_create=client.post('/api/documents',json={'maTL':'GATEWAY-DOC','tenTL':'Gateway synthetic','phongBan':'D1','linkFile':document_url}).json()
        record('GATEWAY_DOCUMENT trusted create',doc_create.get('success'),True)
        for actor,expected in [('A_ADMIN',200),('A_CEO_OTHER',200),('A_USER',200),('A_MANAGER',200),('A_USER_OTHER',404)]:
            task_login(actor);gread('GATEWAY_DOCUMENT',actor,document_url,expected)
            library=client.get('/api/documents/library').json()
            record('GATEWAY_DOCUMENT library predicate aligned '+actor,any(d['maTL']=='GATEWAY-DOC' for d in library['data']),expected==200)
        task_login('B_ADMIN','9000000002');gread('GATEWAY_TENANT','foreign Document',document_url,404)
        task_login('A_USER')
        db=mt.get_tenant_session('9000000001');db.get(Employee,'A_USER').phong_ban='D4';db.commit();db.close()
        gread('GATEWAY_LIVE_REVALIDATION','Document department permission lost',document_url,404)
        task_login('A_ADMIN')
        db=mt.get_tenant_session('9000000001');db.get(Document,'GATEWAY-DOC').link_file='https://example.invalid/changed';db.commit();db.close()
        gread('GATEWAY_LIVE_REVALIDATION','Document changed link',document_url,404)
        db=mt.get_tenant_session('9000000001');db.delete(db.get(Document,'GATEWAY-DOC'));db.commit();db.close()
        gread('GATEWAY_LIVE_REVALIDATION','Document deleted',document_url,404)
        # General and manager-own department behavior uses the exact library predicate.
        task_login('A_ADMIN')
        doc_policy_url,_=local_upload(b'document department policy')
        result=client.post('/api/documents',json={'maTL':'GATEWAY-DOC-POLICY','tenTL':'Policy synthetic','phongBan':'D2','linkFile':doc_policy_url}).json()
        record('GATEWAY_DOCUMENT department fixture',result.get('success'),True)
        task_login('A_MANAGER');gread('GATEWAY_DOCUMENT','manager own department',doc_policy_url,200)
        for department in [None,'','Tất cả']:
            db=mt.get_tenant_session('9000000001');db.get(Document,'GATEWAY-DOC-POLICY').phong_ban=department;db.commit();db.close()
            task_login('A_USER_OTHER');gread('GATEWAY_DOCUMENT','general department '+repr(department),doc_policy_url,200)
        doc_binding=reg.list_active_bindings(registered(doc_policy_url)['file_id'],'9000000001')[0]
        reg.revoke_binding(doc_binding['binding_id'],'9000000001')
        task_login('A_ADMIN');gread('GATEWAY_DOCUMENT','revoked Document binding',doc_policy_url,404)

        task_login('A_USER')
        etag=gread('GATEWAY_HTTP','GET',gateway_url,200).headers.get('etag')
        full=client.get(gateway_url)
        gread('GATEWAY_HTTP','HEAD',gateway_url,200,method='HEAD')
        part=gread('GATEWAY_HTTP','Range',gateway_url,206,headers={'Range':'bytes=0-3'})
        record('GATEWAY_HTTP range exact bytes',part.content==b'0123',True)
        gread('GATEWAY_HTTP','invalid Range',gateway_url,416,headers={'Range':'bytes=99999-'})
        gread('GATEWAY_HTTP','ETag304',gateway_url,304,headers={'If-None-Match':etag})
        gread('GATEWAY_HTTP','date304',gateway_url,304,headers={'If-Modified-Since':full.headers['last-modified']})
        gread('GATEWAY_HTTP','inline',gateway_url,200)
        download=gread('GATEWAY_HTTP','download',gateway_url+'?download=1',200)
        record('GATEWAY_HTTP download disposition',download.headers['content-disposition'].startswith('attachment'),True)
        client.cookies.clear()
        for method,headers in [('HEAD',{}),('GET',{'Range':'bytes=99999-'}),('GET',{'If-None-Match':etag}),('GET',{'If-Modified-Since':full.headers['last-modified']})]:
            gread('GATEWAY_HTTP','anonymous '+method+str(headers.keys()),gateway_url,401,method=method,headers=headers)
        task_login('A_ADMIN')
        for method,headers in [('HEAD',{}),('GET',{'Range':'bytes=99999-'}),('GET',{'If-None-Match':etag})]:
            gread('GATEWAY_HTTP','unauthorized '+method+str(headers.keys()),gateway_url,404,method=method,headers=headers)
        task_login('A_USER')
        original=gateway_path.read_bytes()
        gateway_path.write_bytes(b'X'*len(original))
        gread('GATEWAY_INTEGRITY','hash mismatch',gateway_url,404)
        gread('GATEWAY_INTEGRITY','hash mismatch HEAD',gateway_url,404,method='HEAD')
        gread('GATEWAY_INTEGRITY','hash mismatch conditional',gateway_url,404,headers={'If-None-Match':etag})
        gateway_path.write_bytes(original+b'x')
        gread('GATEWAY_INTEGRITY','size mismatch',gateway_url,404)
        gateway_path.unlink()
        gread('GATEWAY_INTEGRITY','missing bytes',gateway_url,404)
        gateway_path.mkdir()
        gread('GATEWAY_INTEGRITY','directory',gateway_url,404)
        gateway_path.rmdir();gateway_path.write_bytes(original)
        outside=root/'temp/outside-private.txt';outside.write_bytes(original)
        gateway_path.unlink()
        try:
            gateway_path.symlink_to(outside)
        except OSError:
            report_link='NOT FULLY TESTABLE: Windows symlink privilege unavailable'
            # Confinement remains tested via actual resolved-path substitution.
            gateway_path.write_bytes(original)
            with patch.object(access,'handle_realpath',return_value=outside):
                gread('GATEWAY_PATH','opened handle escape',gateway_url,404)
        else:
            report_link='file symlink escape PASS; directory junction NOT FULLY TESTABLE'
            gread('GATEWAY_PATH','actual symlink escape',gateway_url,404)
            gateway_path.unlink();gateway_path.write_bytes(original)
        (root/'gateway_environment.json').write_text(json.dumps({'links':report_link,'junction':'NOT FULLY TESTABLE',
            'production_nginx':'NOT VERIFIED','source_nginx':'NONE FOUND','pwa':'NOT MODIFIED'}))
        for label in ['missing','corrupt','version','schema','busy','read error']:
            before=reg.path.read_bytes()
            if label=='missing':
                alternative=Config.FILE_REGISTRY_ROOT/'absent.sqlite3'
            elif label=='corrupt':
                alternative=Config.FILE_REGISTRY_ROOT/'corrupt-gateway.sqlite3';alternative.write_bytes(b'not SQLite')
            elif label in ['version','schema']:
                alternative=Config.FILE_REGISTRY_ROOT/('gateway-'+label+'.sqlite3')
                alt=FileRegistry(alternative);alt.initialize_registry()
                with alt._connection(mutation=True) as conn:
                    conn.execute('PRAGMA user_version=999' if label=='version' else 'DROP INDEX binding_slot_active')
            else:
                alternative=reg.path
            if label=='busy':
                lock=sqlite3.connect(str(reg.path));lock.execute('BEGIN EXCLUSIVE')
                try:
                    # Snapshot fingerprint uses bytes only; no SQLite read is performed.
                    gread('GATEWAY_FAIL_CLOSED',label,gateway_url,404)
                finally:
                    lock.rollback();lock.close()
            elif label=='read error':
                with patch.object(FileRegistry,'access_snapshot',side_effect=RegistryError('injected read')):
                    gread('GATEWAY_FAIL_CLOSED',label,gateway_url,404)
            else:
                with patch.object(Config,'FILE_REGISTRY_PATH',alternative):
                    gread('GATEWAY_FAIL_CLOSED',label,gateway_url,404)
            record('GATEWAY_FAIL_CLOSED '+label+' main registry unchanged',reg.path.read_bytes()==before,True)
        for asset in ['/static/css/mobile.css','/static/manifest.json','/sw.js','/manifest.json']:
            response=client.get(asset)
            record('GATEWAY_STATIC_BYPASS public asset '+asset,response.status_code,200)
        for folder in ['js','images']:
            existing=next((appdir/'static'/folder).glob('*'),None) if (appdir/'static'/folder).exists() else None
            if existing and existing.is_file():
                record('GATEWAY_STATIC_BYPASS public representative '+folder,client.get('/static/'+folder+'/'+existing.name).status_code,200)
        # Actual synthetic gateway responses for parent-only Node SW replay.
        fixtures=[]
        task_login('A_USER')
        gateway_etag=client.get(gateway_url).headers['etag']
        for name,actor,tenant,path,method,headers,expected in [
            ('authorized','A_USER','9000000001',gateway_url,'GET',{},200),
            ('HEAD','A_USER','9000000001',gateway_url,'HEAD',{},200),
            ('Range','A_USER','9000000001',gateway_url,'GET',{'Range':'bytes=0-3'},206),
            ('conditional','A_USER','9000000001',gateway_url,'GET',{'If-None-Match':gateway_etag},304),
            ('unauthorized','A_ADMIN','9000000001',gateway_url,'GET',{},404),
            ('tenant switch','B_ADMIN','9000000002',gateway_url,'GET',{},404),
            ('unregistered','A_USER','9000000001','/static/uploads/gateway-legacy.txt','GET',{},404),
            ('anonymous',None,None,gateway_url,'GET',{},401),
            ('logout',None,None,gateway_url,'GET',{},401)]:
            if actor:
                task_login(actor,tenant)
            else:
                client.cookies.clear()
            before=read_fingerprints();calls=len(drive_calls)
            reply=client.request(method,path,headers=headers,follow_redirects=False)
            record('PWA_4B3_INTEGRATION live '+name+' status',reply.status_code,expected)
            record('PWA_4B3_INTEGRATION live '+name+' no-store',reply.headers.get('cache-control'),'private, no-store')
            record('PWA_ZERO_MUTATION live '+name+' DB/registry/uploads',read_fingerprints(),before)
            record('PWA_ZERO_MUTATION live '+name+' provider',len(drive_calls),calls)
            fixtures.append({'name':name,'path':path,'method':method,'request_headers':headers,
                'status':reply.status_code,'headers':dict(reply.headers),'body':reply.content.decode('utf-8')})
        # 4B5A provenance model: only synthetic, explicitly reviewed offline calls.
        from services.legacy_provenance import approve_mapping, mapping_digest, register_verified_legacy
        from unittest.mock import patch
        def pcheck(category,name,actual,expected=True):
            record(category+' '+name,actual,expected)
        def preject(category,name,operation):
            before=read_fingerprints(); calls=len(drive_calls)
            try:
                operation(); denied=False
            except (RegistryError,TypeError,ValueError):
                denied=True
            pcheck(category,name,denied)
            pcheck('PROVENANCE_ZERO_MUTATION',name+' bytes/DB/registry',read_fingerprints()==before)
            pcheck('PROVENANCE_ZERO_MUTATION',name+' provider',len(drive_calls)==calls)
        def pread(category,name,url,status,actor='A_USER',tenant='9000000001'):
            if actor: task_login(actor,tenant)
            else: client.cookies.clear()
            before=read_fingerprints(); calls=len(drive_calls)
            reply=client.get(url,follow_redirects=False)
            pcheck(category,name,reply.status_code,status)
            pcheck(category,name+' no-store',reply.headers.get('cache-control'),'private, no-store')
            if status!=200:
                pcheck(category,name+' metadata hidden',not any(h in reply.headers for h in ['etag','last-modified','content-range','location']))
            pcheck('PROVENANCE_ZERO_MUTATION',name+' read fingerprints',read_fingerprints()==before)
            pcheck('PROVENANCE_ZERO_MUTATION',name+' read provider',len(drive_calls)==calls)
            return reply
        pcheck('PROVENANCE_MODEL','explicit schema version',reg.VERSION,3)
        pcheck('PROVENANCE_MODEL','normal provenance',gateway_row['provenance_type'],'VERIFIED_UPLOADER')
        for bad in [None,'','   ']:
            preject('NORMAL_UPLOADER_REQUIRED',repr(bad),lambda bad=bad:reg.register_writing('9000000001',bad,'LOCAL_UPLOADS','bad-normal.txt','display'))
        for kwargs in [{'legacy':True},{'provenance_type':'LEGACY_VERIFIED_MAPPING'},{'classification':'VERIFIED_LEGACY'}]:
            preject('PROVENANCE_ATTACKS',str(kwargs),lambda kwargs=kwargs:reg.register_writing('9000000001','A_USER','LOCAL_UPLOADS','fake-normal.txt','display',**kwargs))
        task_login('A_USER')
        forged=client.post('/api/drive/upload-local',data={'legacy':'true','provenance_type':'LEGACY_VERIFIED_MAPPING',
            'uploader':'','uploader_id':'B_ADMIN','tenant':'9000000002'},files={'file':('form.txt',b'normal provenance')}).json()
        forged_row=registered(forged['url'])
        pcheck('NORMAL_UPLOADER_REQUIRED','real upload succeeds',forged.get('success'))
        pcheck('PROVENANCE_ATTACKS','form actual uploader',forged_row['uploader_id'],'A_USER')
        pcheck('PROVENANCE_ATTACKS','form cannot select legacy',forged_row['provenance_type'],'VERIFIED_UPLOADER')
        before=read_fingerprints()
        response=client.post('/api/drive/upload-local',json={'legacy':True,'uploader':None,'provenance_type':'LEGACY_VERIFIED_MAPPING'})
        pcheck('PROVENANCE_ATTACKS','JSON without file cannot create legacy',response.status_code,422)
        pcheck('PROVENANCE_ZERO_MUTATION','JSON attack no mutation',read_fingerprints()==before)
        pread('PROVENANCE_BACKWARD_COMPAT','normal unbound unchanged',forged['url'],200)
        pread('PROVENANCE_BACKWARD_COMPAT','normal ADMIN not uploader',forged['url'],404,'A_ADMIN')
        for public_path in ['/api/files/register-verified-legacy','/api/legacy/register']:
            reply=client.post(public_path,json={'legacy':True,'provenance_type':'LEGACY_VERIFIED_MAPPING','uploader':None},follow_redirects=False)
            pcheck('LEGACY_CREATION_AUTHORITY',public_path+' not exposed',reply.status_code in (404,405))
        preject('LEGACY_CREATION_AUTHORITY','raw dict no permit',lambda:register_verified_legacy(reg,{},lambda m:True))
        def legacy_case(label,kind='TASK',slot='file_giao_viec'):
            name='provenance-'+label+'.txt'; path=Path(Config.UPLOAD_DIR)/name
            content=('legacy '+label).encode(); path.write_bytes(content)
            oid='PROV-'+label; url='/static/uploads/'+name
            db=mt.get_tenant_session('9000000001')
            if kind=='TASK':
                obj=Task(id_phan_cong=oid,ten_cv='synthetic legacy',nguoi_giao='A_ADMIN',nguoi_nhan='A_USER',file_giao_viec=url)
                if slot=='file_bao_cao': obj.file_giao_viec='';obj.file_bao_cao=url
            else:
                obj=Document(ma_tl=oid,ten_tl='synthetic legacy',loai='synthetic',phong_ban='B',link_file=url)
            db.add(obj);db.commit();db.close()
            mapping={'tenant_id':'9000000001','storage_name':name,'size':len(content),'sha256':hashlib.sha256(content).hexdigest(),
                     'bindings':[{'object_kind':kind,'object_id':oid,'field_slot':slot}]}
            return mapping,url,path
        def reviewed(mapping):
            return approve_mapping(mapping,{'decision':'APPROVED','mapping_digest':mapping_digest(mapping),
                 'review_id':'review-'+mapping['storage_name'],'reviewer':'synthetic-custodian','evidence':'synthetic independent custodian provenance evidence'})
        def revalidate(mapping):
            # Trusted synthetic administrative callback: exact tenant/object/field.
            if mapping['tenant_id']!='9000000001': return False
            db=mt.get_tenant_session(mapping['tenant_id'])
            try:
                for b in mapping['bindings']:
                    model=Task if b['object_kind']=='TASK' else Document
                    key=Task.id_phan_cong if model is Task else Document.ma_tl
                    obj=db.query(model).filter(key==b['object_id']).first()
                    if not obj or getattr(obj,b['field_slot'])!='/static/uploads/'+mapping['storage_name']: return False
                return True
            finally: db.close()
        lm,lu,lp=legacy_case('task')
        pread('LEGACY_UNKNOWN_DENY','unregistered legacy ADMIN',lu,404,'A_ADMIN')
        pread('LEGACY_UNKNOWN_DENY','unregistered legacy anonymous',lu,401,None)
        for approval in [{},{'decision':'UNAPPROVED'},{'decision':'APPROVED','mapping_digest':'*'},
                          {'decision':'APPROVED','mapping_digest':mapping_digest(lm),'review_id':'r','reviewer':'ADMIN','evidence':''}]:
            preject('LEGACY_CREATION_AUTHORITY','unapproved '+str(approval),lambda approval=approval:approve_mapping(lm,approval))
        fid=register_verified_legacy(reg,reviewed(lm),revalidate)
        lr=reg.get_file(fid,'9000000001')
        pcheck('PROVENANCE_MODEL','legacy explicit',lr['provenance_type'],'LEGACY_VERIFIED_MAPPING')
        pcheck('PROVENANCE_MODEL','legacy uploader truly absent',lr['uploader_id'],None)
        pcheck('PROVENANCE_MODEL','reviewer separate',lr['reviewed_by'],'synthetic-custodian')
        pcheck('LEGACY_BINDING_REQUIRED','atomic BOUND',lr['state'],'BOUND')
        pcheck('LEGACY_BINDING_REQUIRED','one ACTIVE',len(reg.list_active_bindings(fid,'9000000001')),1)
        preject('LEGACY_TENANT_ISOLATION','foreign binding creation',lambda:reg.create_pending_binding(fid,'9000000002','TASK','foreign','file_giao_viec'))
        preject('LEGACY_NO_UPLOADER_FALLBACK','legacy UNBOUND SQL transition rejected',lambda:reg.complete_unbound(fid,'9000000001',lm['size'],lm['sha256']))
        for actor,status in [('A_ADMIN',200),('A_USER',200),('A_MANAGER',404),('A_USER_OTHER',404)]:
            pread('LEGACY_TASK_ACL','legacy Task '+actor,lu,status,actor)
        pread('LEGACY_TENANT_ISOLATION','foreign tenant',lu,404,'B_ADMIN','9000000002')
        pread('LEGACY_TENANT_ISOLATION','same actor foreign tenant',lu,404,'A_USER','9000000002')
        pread('PROVENANCE_ATTACKS','forged query authority',lu+'?role=ADMIN&tenant=9000000001&company_mst=9000000001',404,'B_ADMIN','9000000002')
        # Gateway's live field and ACL checks remain mandatory, not cached in registry.
        db=mt.get_tenant_session('9000000001');obj=db.get(Task,lm['bindings'][0]['object_id']);obj.nguoi_nhan='A_MANAGER';db.commit();db.close()
        pread('LEGACY_TASK_ACL','relationship removed',lu,404)
        db=mt.get_tenant_session('9000000001');obj=db.get(Task,lm['bindings'][0]['object_id']);obj.nguoi_nhan='A_USER';db.commit();db.close()
        dm,du,dp=legacy_case('document','DOCUMENT','link_file')
        df=register_verified_legacy(reg,reviewed(dm),revalidate)
        pread('LEGACY_DOCUMENT_ACL','ADMIN',du,200,'A_ADMIN')
        # Existing department B document excludes A_USER department A.
        pread('LEGACY_DOCUMENT_ACL','different department',du,404,'A_USER')
        db=mt.get_tenant_session('9000000001');obj=db.get(Document,dm['bindings'][0]['object_id']);obj.phong_ban=None;db.commit();db.close()
        pread('LEGACY_DOCUMENT_ACL','general document',du,200)
        db=mt.get_tenant_session('9000000001');obj=db.get(Document,dm['bindings'][0]['object_id']);db.delete(obj);db.commit();db.close()
        pread('LEGACY_DOCUMENT_ACL','deleted Document',du,404,'A_ADMIN')
        pread('LEGACY_UNKNOWN_DENY','UNKNOWN ADMIN unchanged',unknown_url,404,'A_ADMIN')
        # Model corruption is denied even when constraints are bypassed by trusted DB access.
        for label,changes in [('legacy UNBOUND',{'state':'UNBOUND'}),('fake legacy uploader',{'uploader_id':'A_USER'}),
                ('malformed',{'provenance_type':'fake'}),('case alias',{'provenance_type':'legacy_verified_mapping'}),
                ('missing',{'provenance_type':None}),('unknown enum',{'provenance_type':'UNKNOWN'})]:
            with reg._connection(mutation=True) as conn:
                conn.execute('PRAGMA ignore_check_constraints=ON')
                for key,value in changes.items():
                    # NULL cannot bypass NOT NULL: test empty missing provenance instead.
                    conn.execute('UPDATE files SET '+key+'=? WHERE file_id=?',('' if key=='provenance_type' and value is None else value,fid))
            pread('LEGACY_NO_UPLOADER_FALLBACK' if 'UNBOUND' in label or 'uploader' in label else 'PROVENANCE_MALFORMED_DENY',label,lu,404,'A_ADMIN')
            with reg._connection(mutation=True) as conn:
                conn.execute("UPDATE files SET state='BOUND',uploader_id=NULL,provenance_type='LEGACY_VERIFIED_MAPPING' WHERE file_id=?",(fid,))
        lp.write_bytes(b'x'*lm['size'])
        pread('PROVENANCE_PATH_INTEGRITY','hash mismatch',lu,404,'A_ADMIN')
        lp.write_bytes(b'too long corrupted content')
        pread('PROVENANCE_PATH_INTEGRITY','size mismatch',lu,404,'A_ADMIN')
        lp.write_bytes(b'legacy task')
        pread('PROVENANCE_PATH_INTEGRITY','traversal', '/static/uploads/..%5c'+lm['storage_name'],404,'A_ADMIN')
        # Atomic failure after first insert and after first binding leaves nothing trusted.
        am,au,ap=legacy_case('atomic')
        count=[0]
        def fail_second(mapping): count[0]+=1;return count[0]==1
        preject('PROVENANCE_ATOMICITY','post-insert callback failure',lambda:register_verified_legacy(reg,reviewed(am),fail_second))
        pcheck('PROVENANCE_ATOMICITY','no partial identity',reg.get_storage_record('LOCAL_UPLOADS',am['storage_name']),None)
        preject('PROVENANCE_ATOMICITY','pre-insert stale review',lambda:register_verified_legacy(reg,reviewed(am),lambda m:False))
        conflict={**am,'bindings':am['bindings']+lm['bindings']}
        preject('PROVENANCE_ATOMICITY','second binding conflict rolls back identity and first binding',lambda:register_verified_legacy(reg,reviewed(conflict),lambda m:True))
        pcheck('PROVENANCE_ATOMICITY','failed multi binding has no identity',reg.get_storage_record('LOCAL_UPLOADS',am['storage_name']),None)
        preject('PROVENANCE_PATH_INTEGRITY','changed approved bytes',lambda:register_verified_legacy(reg,reviewed({**am,'sha256':'0'*64}),revalidate))
        # A valid legacy row with all bindings revoked cannot use reviewer/uploader fallback.
        for b in reg.list_active_bindings(fid,'9000000001'):reg.revoke_binding(b['binding_id'],'9000000001')
        pread('LEGACY_BINDING_REQUIRED','no ACTIVE binding ADMIN',lu,404,'A_ADMIN')
        pread('LEGACY_NO_UPLOADER_FALLBACK','no ACTIVE binding user',lu,404)
        # Unsupported object kind contributes no authority, even after DB corruption.
        with reg._connection(mutation=True) as conn:
            conn.execute("UPDATE bindings SET state='ACTIVE',object_kind='PERSONAL' WHERE file_id=?",(fid,))
        pread('LEGACY_BINDING_REQUIRED','unsupported binding',lu,404,'A_ADMIN')
        with reg._connection(mutation=True) as conn:
            conn.execute("UPDATE bindings SET object_kind='TASK' WHERE file_id=?",(fid,))
        # Actual approved legacy response is replayed through unchanged SW network-only logic.
        reply=pread('PROVENANCE_PWA_INTEGRATION','legacy server no-store',lu,200)
        fixtures.append({'name':'LEGACY approved','path':lu,'method':'GET','request_headers':{},'status':reply.status_code,
                         'headers':dict(reply.headers),'body':reply.content.decode('utf-8')})
        db=mt.get_tenant_session('9000000001');obj=db.get(Task,lm['bindings'][0]['object_id']);db.delete(obj);db.commit();db.close()
        pread('LEGACY_TASK_ACL','deleted Task ADMIN',lu,404,'A_ADMIN')
        # Explicit read-only v2 compatibility: no implicit mutation/migration.
        old_path=Config.FILE_REGISTRY_ROOT/'provenance-v2.sqlite3'
        old=sqlite3.connect(old_path)
        old.execute('CREATE TABLE files (file_id TEXT PRIMARY KEY,tenant_id TEXT,uploader_id TEXT,storage_root_id TEXT,storage_name TEXT,original_name TEXT,created_at TEXT,size INTEGER,sha256 TEXT,classification TEXT,state TEXT,expires_at TEXT,version INTEGER)')
        with reg._connection() as conn:
            for sql, in conn.execute("SELECT sql FROM sqlite_master WHERE (type='table' AND name='bindings') OR (type='index' AND name IN ('binding_slot_active','binding_slot_pending')) ORDER BY CASE type WHEN 'table' THEN 0 ELSE 1 END"):
                old.execute(sql)
        normal=reg.get_file(forged_row['file_id'],'9000000001')
        old.execute('INSERT INTO files VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)',tuple(normal[k] for k in FileRegistry.FILE_COLUMNS[:-4]))
        old.execute('PRAGMA user_version=2');old.commit();old.close()
        old_bytes=old_path.read_bytes()
        with patch.object(Config,'FILE_REGISTRY_PATH',old_path):
            pread('PROVENANCE_BACKWARD_COMPAT','v2 normal uploader read',forged['url'],200)
            pread('PROVENANCE_BACKWARD_COMPAT','v2 normal ADMIN denied',forged['url'],404,'A_ADMIN')
            oldreg=FileRegistry()
            preject('PROVENANCE_BACKWARD_COMPAT','v2 mutation requires explicit migration',lambda:oldreg.register_writing('9000000001','A_USER','LOCAL_UPLOADS','v2-new.txt','name'))
        pcheck('PROVENANCE_BACKWARD_COMPAT','v2 bytes unchanged',old_path.read_bytes()==old_bytes)
        # Resumed4B5 offline workflow; separate labels preserve234 prior assertions.
        from services.legacy_discovery import (LegacyDiscovery,LegacyAuditError,CustodianAuthority,
             normalize_reference,approve_candidate,apply_synthetic,canonical_json,digest)
        authority=CustodianAuthority('synthetic-independent-custodian',os.urandom(32))
        sources={t:Path(mt.get_tenant_db_path(t)) for t in ['9000000001','9000000002','0312345678']}
        discovery=LegacyDiscovery(Config.UPLOAD_DIR,sources,reg.path)
        def lcheck(category,name,actual,expected=True):record('B4B5 '+category+' '+name,actual,expected)
        def lreject(category,name,operation):
            before=read_fingerprints();calls=len(drive_calls)
            try:operation();blocked=False
            except (LegacyAuditError,RegistryError,TypeError,ValueError):blocked=True
            lcheck(category,name,blocked)
            lcheck('LEGACY_ZERO_MUTATION',name+' no partial authority/bytes/DB',read_fingerprints()==before)
            lcheck('LEGACY_ZERO_MUTATION',name+' provider',len(drive_calls)==calls)
        def candidate_for(url,artifact=None):
            artifact=artifact or discovery.discover()
            name=url.removeprefix('/static/uploads/')
            return next((c for c in artifact['candidates'] if c['storage_name']==name),None)
        def lfixture(label,kind='TASK',tenant='9000000001',file=True,url=None):
            storage='legacy-flow-'+label+'.txt'; path=Path(Config.UPLOAD_DIR)/storage
            if url is None:
                url='/static/uploads/'+storage
                if file:path.write_bytes(('synthetic legacy flow '+label).encode())
            oid='LF-'+label
            db=mt.get_tenant_session(tenant)
            if kind=='TASK':obj=Task(id_phan_cong=oid,ten_cv='synthetic review task',nguoi_giao='A_USER_OTHER',nguoi_nhan='A_USER',file_giao_viec=url)
            elif kind=='DOCUMENT':obj=Document(ma_tl=oid,ten_tl='synthetic review doc',loai='synthetic',phong_ban='D4',link_file=url)
            else:
                from models.models import PersonalTask
                obj=PersonalTask(user_id='A_USER',ten_cv='synthetic personal',file_dinh_kem=url)
            db.add(obj);db.commit();db.close()
            return url,path,oid
        def lapproval(candidate):
            return approve_candidate(candidate,authority,{'source_kind':'CUSTODIAN_ATTESTATION',
                'source_id':'synthetic independent evidence '+candidate['candidate_id'],
                'statement':'Synthetic custodian verifies tenant/blob/object mapping independently of URLs; not uploader.',
                'tenant_id':candidate['tenant_candidate'],'sha256':candidate['physical'].get('sha256')})
        def lread(category,name,url,status,actor='A_USER',tenant='9000000001'):
            if actor:task_login(actor,tenant)
            else:client.cookies.clear()
            before=read_fingerprints();calls=len(drive_calls)
            response=client.get(url,follow_redirects=False)
            lcheck(category,name+' status',response.status_code,status)
            lcheck(category,name+' no-store',response.headers.get('cache-control'),'private, no-store')
            if status!=200:lcheck(category,name+' no metadata/raw redirect',not any(h in response.headers for h in ['etag','last-modified','content-range','location']))
            lcheck('LEGACY_ZERO_MUTATION',name+' READ',read_fingerprints()==before)
            lcheck('LEGACY_ZERO_MUTATION',name+' provider',len(drive_calls)==calls)
            return response
        for value,expected in [('/static/uploads/name.txt','LOCAL_UPLOAD'),('/static/uploads/name.txt?x=1','INVALID_PATH'),
             ('/static/uploads/name.txt#x','INVALID_PATH'),('/static/uploads/%6eame.txt','INVALID_PATH'),
             ('/static/uploads/%252e%252e','INVALID_PATH'),('/static//uploads/name.txt','INVALID_PATH'),
             ('/static/./uploads/name.txt','INVALID_PATH'),('/static/uploads/../secret','INVALID_PATH'),
             ('/static/uploads/..%5csecret','INVALID_PATH'),('/static/uploads/a%2fb','INVALID_PATH'),
             ('/static/uploads/a\\b','INVALID_PATH'),('C:\\private','INVALID_PATH'),
             ('/STATIC/UPLOADS/name.txt','INVALID_PATH'),('https://same.invalid/static/uploads/name.txt','EXTERNAL_REFERENCE'),
             ('https://foreign.invalid/a','EXTERNAL_REFERENCE'),('/local_docs/a.pdf','PUBLIC_NON_UPLOAD'),
             ('/static/uploads2/a','PUBLIC_NON_UPLOAD'),('/foo/static/uploads/a','PUBLIC_NON_UPLOAD'),
             ('/static/upload/a','PUBLIC_NON_UPLOAD'),('/static/css/x.css?hint=/static/uploads/a','PUBLIC_NON_UPLOAD'),
             ('/static/uploads/a\x00b','INVALID_PATH')]:
            lcheck('LEGACY_NORMALIZATION',repr(value),normalize_reference(value)[0],expected)
        lcheck('LEGACY_NORMALIZATION','accepted locator agrees binding parser',normalize_reference('/static/uploads/name.txt')[1],FileBindingService.local_name('/static/uploads/name.txt'))
        task_url,task_path,task_id=lfixture('task')
        doc_url,doc_path,doc_id=lfixture('document','DOCUMENT')
        multi_url,multi_path,multi_id=lfixture('multi')
        _,_,multi_doc=lfixture('multi-doc','DOCUMENT',url=multi_url)
        _,_,multi_task=lfixture('multi-task',url=multi_url)
        cross_url,cross_path,cross_id=lfixture('cross')
        lfixture('cross-B',tenant='9000000002',url=cross_url)
        orphan_path=Path(Config.UPLOAD_DIR)/'legacy-flow-orphan.txt';orphan_path.write_bytes(b'orphan unknown')
        missing_url,_,_=lfixture('missing',file=False)
        lfixture('external','DOCUMENT',url='https://example.invalid/legacy.pdf')
        lfixture('invalid',url='/static/uploads/..%2fsecret')
        personal_url,_,_=lfixture('personal','PERSONAL')
        alias_url,alias_path,_=lfixture('alias')
        alias_other=Path(Config.UPLOAD_DIR)/'legacy-flow-alias-second.txt'
        os.link(alias_path,alias_other)
        lfixture('alias-second',url='/static/uploads/'+alias_other.name)
        parent_url,parent_path,parent_id=lfixture('parent')
        task_login('A_USER')
        child_result=client.post('/api/tasks/forward',json={'idPhanCongGoc':parent_id,'nguoiNhanUyQuyen':'A_MANAGER'}).json()
        lcheck('LEGACY_MULTI_BINDING','actual forward flow succeeds',child_result.get('success'),True)
        child_id=child_result.get('id')
        artifact_before=read_fingerprints();artifact=discovery.discover()
        lcheck('LEGACY_DISCOVERY','discovery reads all supported source classes',all(any(x['kind']==k and x['status']=='INVENTORIED' for x in artifact['reference_classes']) for k in ['TASK','DOCUMENT','PERSONAL']))
        lcheck('LEGACY_ZERO_MUTATION','discovery no writes',read_fingerprints()==artifact_before)
        lcheck('LEGACY_REVIEW_ARTIFACT','deterministic repeated snapshot',canonical_json(discovery.discover()),canonical_json(artifact))
        lcheck('LEGACY_REVIEW_ARTIFACT','all default UNAPPROVED',all(c['approval_status']=='UNAPPROVED' and c['review_id'] is None for c in artifact['candidates']))
        (root/'legacy_review_synthetic.json').write_text(json.dumps(artifact,sort_keys=True,indent=2),encoding='utf-8')
        tc=candidate_for(task_url,artifact);dc=candidate_for(doc_url,artifact);mc=candidate_for(multi_url,artifact)
        lcheck('LEGACY_DISCOVERY','Task exact binding',tc['object_bindings'],[{'object_kind':'TASK','object_id':task_id,'field_slot':'file_giao_viec'}])
        lcheck('LEGACY_DISCOVERY','Document exact binding',dc['object_bindings'],[{'object_kind':'DOCUMENT','object_id':doc_id,'field_slot':'link_file'}])
        lcheck('LEGACY_CLASSIFICATION','references do not establish provenance',tc['classification'],'UNKNOWN')
        lcheck('LEGACY_CLASSIFICATION','structural review eligibility only',tc['eligible_for_review'])
        lcheck('LEGACY_CLASSIFICATION','unsupported Personal ACL stays UNKNOWN',candidate_for(personal_url,artifact)['classification'],'UNKNOWN')
        lcheck('LEGACY_CLASSIFICATION','unsupported Personal not eligible',candidate_for(personal_url,artifact)['eligible_for_review'],False)
        lcheck('LEGACY_CLASSIFICATION','same physical identity aliases ambiguous',candidate_for(alias_url,artifact)['classification'],'AMBIGUOUS')
        lcheck('LEGACY_CROSS_TENANT','cross tenant conflict',candidate_for(cross_url,artifact)['classification'],'CROSS_TENANT_CONFLICT')
        lcheck('LEGACY_ORPHAN','physical orphan',candidate_for('/static/uploads/'+orphan_path.name,artifact)['classification'],'ORPHAN')
        lcheck('LEGACY_MISSING_PHYSICAL','missing bytes',candidate_for(missing_url,artifact)['classification'],'MISSING_PHYSICAL')
        lcheck('LEGACY_EXTERNAL_REFERENCE','external excluded',any(r['normalization']=='EXTERNAL_REFERENCE' and r['object_id']=='LF-external' for r in artifact['excluded_references']))
        lcheck('LEGACY_NORMALIZATION','traversal excluded',any(r['normalization']=='INVALID_PATH' and r['object_id']=='LF-invalid' for r in artifact['excluded_references']))
        lcheck('LEGACY_CLASSIFICATION','existing valid registered identity',candidate_for(forged['url'],artifact)['classification'],'ALREADY_REGISTERED')
        # Existing ACTIVE binding with missing object is inventory evidence, not ACL.
        lcheck('LEGACY_MISSING_OBJECT','4B5A deleted Task binding identified',candidate_for(lu,artifact)['classification'],'MISSING_OBJECT')
        conflict_url,conflict_path=local_upload(b'conflict bytes')
        conflict_path.write_bytes(b'mismatch bytes')
        lcheck('LEGACY_CONFLICT','registry size/hash conflict',candidate_for(conflict_url)['classification'],'CONFLICT')
        conflict_path.write_bytes(b'conflict bytes')
        for name,url in [('UNKNOWN A',task_url),('UNKNOWN B',doc_url),('orphan','/static/uploads/'+orphan_path.name)]:
            lread('LEGACY_UNKNOWN_DENY',name+' anonymous',url,401,None)
            lread('LEGACY_UNKNOWN_DENY',name+' ADMIN',url,404,'A_ADMIN')
            lread('LEGACY_UNKNOWN_DENY',name+' authenticated',url,404)
        lreject('LEGACY_APPROVAL_REQUIRED','no authority',lambda:approve_candidate(tc,{},{}))
        lreject('LEGACY_APPROVAL_REQUIRED','reference alone no independent evidence',lambda:approve_candidate(tc,authority,{}))
        lreject('LEGACY_CROSS_TENANT','cannot approve cross-tenant conflict',lambda:lapproval(candidate_for(cross_url)))
        lreject('LEGACY_ORPHAN','cannot approve orphan',lambda:lapproval(candidate_for('/static/uploads/'+orphan_path.name)))
        lreject('LEGACY_MISSING_PHYSICAL','cannot approve missing bytes',lambda:lapproval(candidate_for(missing_url)))
        lreject('LEGACY_CLASSIFICATION','cannot approve unsupported Personal',lambda:lapproval(candidate_for(personal_url)))
        lreject('LEGACY_CLASSIFICATION','cannot approve ambiguous aliases',lambda:lapproval(candidate_for(alias_url)))
        approval=lapproval(tc)
        lcheck('LEGACY_CUSTODIAN_BINDING','review becomes eligible VERIFIED_CANDIDATE only with independent evidence',approval['reviewed_classification'],'VERIFIED_CANDIDATE')
        lcheck('LEGACY_CUSTODIAN_BINDING','attributable custodian',approval['custodian_id'],authority.custodian_id)
        lcheck('LEGACY_CUSTODIAN_BINDING','approval bound to exact digest',approval['candidate_digest'],tc['evidence_digest'])
        lreject('LEGACY_APPROVAL_REQUIRED','UNAPPROVED artifact cannot apply',lambda:apply_synthetic(discovery,tc,tc,authority,root))
        lreject('LEGACY_CUSTODIAN_BINDING','fake reviewer/client unsigned approval',lambda:apply_synthetic(discovery,tc,{**approval,'custodian_id':'ADMIN','signature':'0'*64},authority,root))
        lreject('LEGACY_CUSTODIAN_BINDING','evidence digest tamper',lambda:apply_synthetic(discovery,tc,{**approval,'candidate_digest':'0'*64},authority,root))
        lreject('LEGACY_CUSTODIAN_BINDING','independent evidence tamper',lambda:apply_synthetic(discovery,tc,{**approval,'independent_evidence':{'tenant_id':'9000000002'}},authority,root))
        lreject('LEGACY_ZERO_MUTATION','production/root apply rejected',lambda:apply_synthetic(discovery,tc,approval,authority,appdir))
        partial=LegacyDiscovery(Config.UPLOAD_DIR,{'9000000001':sources['9000000001']},reg.path)
        partial_candidate=candidate_for(task_url,partial.discover())
        lreject('LEGACY_CROSS_TENANT','incomplete tenant inventory cannot apply',
                lambda:apply_synthetic(partial,partial_candidate,lapproval(partial_candidate),authority,root))
        # Material changes invalidate exact signed review, even if only one tenant.
        for label in ['hash','size','removed bytes','removed reference','deleted object','new tenant conflict']:
            stale_url,stale_path,stale_id=lfixture('stale-'+label.replace(' ','-'))
            candidate=candidate_for(stale_url);decision=lapproval(candidate)
            if label=='hash':stale_path.write_bytes(b'x'*candidate['physical']['size'])
            elif label=='size':stale_path.write_bytes(b'changed size')
            elif label=='removed bytes':stale_path.unlink()
            elif label=='new tenant conflict':lfixture('new-cross-ref',tenant='9000000002',url=stale_url)
            else:
                db=mt.get_tenant_session('9000000001');obj=db.get(Task,stale_id)
                if label=='deleted object':db.delete(obj)
                else:obj.file_giao_viec=''
                db.commit();db.close()
            lreject('LEGACY_STALE_REVIEW',label+' must re-review',lambda candidate=candidate,decision=decision:apply_synthetic(discovery,candidate,decision,authority,root))
        # ApprovedA only; unapprovedB remains denied even toADMIN.
        tc=candidate_for(task_url);approval=lapproval(tc)
        fid=apply_synthetic(discovery,tc,approval,authority,root)
        lr=reg.get_file(fid,'9000000001')
        lcheck('LEGACY_ATOMIC_APPLY','identity BOUND',lr['state'],'BOUND')
        lcheck('LEGACY_PROVENANCE_INTEGRATION','4B5A provenance exact',lr['provenance_type'],'LEGACY_VERIFIED_MAPPING')
        lcheck('LEGACY_PROVENANCE_INTEGRATION','uploader never fabricated',lr['uploader_id'],None)
        lcheck('LEGACY_CUSTODIAN_BINDING','reviewer separate from uploader',lr['reviewed_by'],authority.custodian_id)
        lread('LEGACY_APPROVED_ACCESS','authorized receiver',task_url,200)
        lread('LEGACY_APPROVED_ACCESS','authorized giver',task_url,200,'A_USER_OTHER')
        lread('LEGACY_APPROVED_ACCESS','unrelated denied',task_url,404,'A_MANAGER')
        lread('LEGACY_APPROVED_ACCESS','foreign tenant denied',task_url,404,'B_ADMIN','9000000002')
        lread('LEGACY_UNKNOWN_DENY','B remains denied afterA approved',doc_url,404,'A_ADMIN')
        dc=candidate_for(doc_url);dfid=apply_synthetic(discovery,dc,lapproval(dc),authority,root)
        lread('LEGACY_APPROVED_ACCESS','authorized Document department',doc_url,200)
        lread('LEGACY_APPROVED_ACCESS','unauthorized Document department',doc_url,404,'A_USER_OTHER')
        mc=candidate_for(multi_url)
        lcheck('LEGACY_MULTI_BINDING','Task+Document+Task references',len(mc['object_bindings']),3)
        mfid=apply_synthetic(discovery,mc,lapproval(mc),authority,root)
        lcheck('LEGACY_MULTI_BINDING','one identity three vetted bindings',len(reg.list_active_bindings(mfid,'9000000001')),3)
        lread('LEGACY_MULTI_BINDING','union actor authorized viaTask',multi_url,200)
        pc=candidate_for(parent_url)
        lcheck('LEGACY_MULTI_BINDING','parent/actual forward child references',len(pc['object_bindings']),2)
        pfid=apply_synthetic(discovery,pc,lapproval(pc),authority,root)
        lcheck('LEGACY_MULTI_BINDING','parent child one physical identity',len(reg.list_active_bindings(pfid,'9000000001')),2)
        lread('LEGACY_MULTI_BINDING','parent-only actor',parent_url,200,'A_USER_OTHER')
        lread('LEGACY_MULTI_BINDING','child-only actor',parent_url,200,'A_MANAGER')
        # Failure AFTER registry inserts must roll back identity + all bindings.
        atomic_url,atomic_path,atomic_id=lfixture('atomic-rollback')
        ac=candidate_for(atomic_url);aa=lapproval(ac)
        original=LegacyDiscovery.discover; seen=[0]
        def injected(self,**kwargs):
            if kwargs.get('registry_connection') is not None:
                seen[0]+=1
                if seen[0]==2:raise LegacyAuditError('Injected post-insert revalidation')
            return original(self,**kwargs)
        with patch.object(LegacyDiscovery,'discover',injected):
            lreject('LEGACY_ATOMIC_APPLY','post-insert failure rollback',lambda:apply_synthetic(discovery,ac,aa,authority,root))
        lcheck('LEGACY_ATOMIC_APPLY','failed identity absent',reg.get_storage_record('LOCAL_UPLOADS',ac['storage_name']),None)
        lread('LEGACY_UNKNOWN_DENY','failed apply remains denied',atomic_url,404,'A_ADMIN')
        lreject('LEGACY_REVALIDATION','already applied receipt cannot create duplicate identity',lambda:apply_synthetic(discovery,tc,approval,authority,root))
        # Corrupt legacy provenance still cannot bypass the unchanged gateway.
        with reg._connection(mutation=True) as conn:
            conn.execute('PRAGMA ignore_check_constraints=ON');conn.execute("UPDATE files SET provenance_type='FAKE' WHERE file_id=?",(fid,))
        lread('LEGACY_PROVENANCE_INTEGRATION','malformed provenance denied',task_url,404,'A_ADMIN')
        with reg._connection(mutation=True) as conn:conn.execute("UPDATE files SET provenance_type='LEGACY_VERIFIED_MAPPING' WHERE file_id=?",(fid,))
        response=lread('LEGACY_PWA_INTEGRATION','actual approved bytes network-only',task_url,200)
        fixtures.append({'name':'B4B5 approved legacy','path':task_url,'method':'GET','request_headers':{},'status':response.status_code,
                         'headers':dict(response.headers),'body':response.content.decode('utf-8')})
        (root/'legacy_workflow_evidence.json').write_text(json.dumps({'complete':True,'discovery':'legacy_review_synthetic.json',
            'approval':approval,'production_apply':'FORBIDDEN','independent_evidence':'SYNTHETIC ONLY'},indent=2),encoding='utf-8')
        (root/'pwa_gateway_fixtures.json').write_text(json.dumps(fixtures,indent=2),encoding='utf-8')
        task_login('A_USER')
        record('mobile dashboard baseline', client.get('/mobile').status_code, 200)
        record('mobile tasks baseline', client.get('/mobile/tasks').status_code, 200)
    assert not violations, 'Sandbox guard triggered during runtime'
    for engine in [connection.engine, mt.master_engine, *mt._tenant_engines.values()]:
        engine.dispose()
    report = {'complete': True, 'isolation_preflight': 'PASS', 'guard_probes': probes, 'routers': loaded,
              'actors': actors, 'master_actor': {'mst': '0312345678', 'actor': 'ADMIN', 'synthetic': True},
              'results': results, 'unexpected_guard_violations': violations,
              'sec03_blocked': {'operations': rename_paths,
                               'authorized_allow_test': 'BLOCKED: no trusted Drive ownership metadata; no schema changes permitted'},
              'drive_mutation_calls': len(drive_calls)}
    (root / 'runtime_results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('Runtime completed; baseline failures:', sum(not r['pass'] for r in results))


def registry_process(root, index):
    """Independent guarded metadata worker; never imports/runs the production app."""
    root=root.resolve()
    if not root.is_relative_to(PROJECT/'.test_runtime') or not root.name.startswith('run-'):
        raise RuntimeError('Invalid registry worker root')
    os.chdir(root/'app')
    sys.path.insert(0,str(root/'app'))
    sys.dont_write_bytecode=True
    os.environ.update(APP_ENV='test', SECRET_KEY=uuid.uuid4().hex,
        UPLOAD_DIR=str(root/'app/static/uploads'), LOCAL_DOCS_DIR='',
        FILE_REGISTRY_ROOT=str(root/'private_metadata'),
        FILE_REGISTRY_PATH=str(root/'private_metadata/file_registry.sqlite3'))

    def audit(event,args):
        if event=='sqlite3.connect':
            inside(args[0],root)
        elif event=='open':
            path,mode,flags=args
            if not isinstance(path,int):
                if Path(os.fsdecode(path)).name=='.env':
                    raise RuntimeError('Registry worker dotenv denied')
                if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                    inside(path,root)
        elif event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.utime'):
            inside(args[0],root)
        elif event in ('os.rename','os.link','os.symlink'):
            inside(args[0],root);inside(args[1],root)
        elif event.startswith('socket.') or event in ('subprocess.Popen','os.system'):
            raise RuntimeError('Registry worker external action denied')
    sys.addaudithook(audit)
    import dotenv
    dotenv.load_dotenv=lambda *a,**k:False
    from services.file_registry import FileRegistry, RegistryError
    reg=FileRegistry(busy_ms=2000)
    fixture=json.loads((root/'registry_process_fixture.json').read_text())
    # Both processes reach ready before either starts the race.
    (root/('process-ready-'+index)).write_text('ready')
    import time
    deadline=time.monotonic()+10
    while not all((root/('process-ready-'+str(i))).exists() for i in range(2)):
        if time.monotonic()>deadline:
            raise RuntimeError('Registry process barrier timeout')
        time.sleep(.01)
    distinct=[reg.register_writing('9000000001','A_USER','LOCAL_UPLOADS',
              'process-'+index+'-'+str(i)+'.txt','display') for i in range(8)]
    try:
        same=reg.register_writing('9000000001','A_USER','LOCAL_UPLOADS','process-same.txt','display')
    except RegistryError:
        same=None
    exact=reg.create_pending_binding(fixture['file_id'],'9000000001','TASK','process-exact','assignment')
    reg.activate_binding(exact,'9000000001')
    own=reg.register_writing('9000000001','A_USER','LOCAL_UPLOADS','process-conflict-'+index+'.txt','display')
    reg.complete_unbound(own,'9000000001',4,hashlib.sha256(b'test').hexdigest())
    try:
        conflict=reg.create_pending_binding(own,'9000000001','TASK','process-conflict','assignment')
        reg.activate_binding(conflict,'9000000001')
    except RegistryError:
        conflict=None
    old=reg.create_pending_binding(fixture['file_id'],'9000000001','TASK','process-replacement','assignment')
    reg.activate_binding(old,'9000000001')
    (root/('replacement-ready-'+index)).write_text('ready')
    deadline=time.monotonic()+10
    while not all((root/('replacement-ready-'+str(i))).exists() for i in range(2)):
        if time.monotonic()>deadline:
            raise RuntimeError('Replacement process barrier timeout')
        time.sleep(.01)
    try:
        replacement=reg.create_pending_binding(own,'9000000001','TASK','process-replacement','assignment',replacement=True)
    except RegistryError:
        replacement=None
    (root/('replacement-reserved-'+index)).write_text('reserved')
    deadline=time.monotonic()+10
    while not all((root/('replacement-reserved-'+str(i))).exists() for i in range(2)):
        if time.monotonic()>deadline:
            raise RuntimeError('Replacement reservation barrier timeout')
        time.sleep(.01)
    old_preserved=reg.get_binding(old,'9000000001')['state']=='ACTIVE' if replacement else True
    if replacement:
        receipt=reg.get_binding(replacement,'9000000001')
        reg.activate_binding(replacement,'9000000001',expected_generation=receipt['generation'])
        exact_retry=reg.create_pending_binding(own,'9000000001','TASK','process-replacement','assignment',replacement=True)==replacement
    else:
        exact_retry=True
    with reg._connection() as conn:
        readable=conn.execute('PRAGMA quick_check').fetchone()[0]=='ok'
    (root/('registry_process_'+index+'.json')).write_text(json.dumps({
        'distinct':distinct,'same':same,'exact':exact,'conflict':conflict,'readable':readable,
        'replacement':replacement,'old_preserved':old_preserved,'retry':exact_retry}),encoding='utf-8')


PWA_TEST_JS = r"""
// Execute the actual SW in a Node VM. CacheStorage/fetch/clients are synthetic;
// this is deterministic event/cache simulation, NOT real browser verification.
const fs=require('fs'), vm=require('vm');
const source=fs.readFileSync(process.argv[1],'utf8');
const fixtures=process.argv[2] ? JSON.parse(fs.readFileSync(process.argv[2],'utf8')) : [];
const origin='https://qlcv.test';
const results=[];
function check(category,name,actual,expected=true) {
  results.push({test:category+' '+name,actual,expected,pass:actual===expected});
}
function response(body='NETWORK',status=200,url=origin+'/static/css/mobile.css',headers={}) {
  const r=new Response([204,205,304].includes(status)?null:body,{status,headers});
  Object.defineProperty(r,'url',{value:url});
  return r;
}
function copy(r) {
  const clone=r.clone();Object.defineProperty(clone,'url',{value:r.url});
  Object.defineProperty(clone,'redirected',{value:r.redirected});return clone;
}
function key(r) {return typeof r==='string'?new URL(r,origin).href:r.url;}
function environment() {
  const stores=new Map(), cacheOps=[], network=[], handlers={};
  let networkBehavior=async req=>response('NETWORK',200,key(req));
  let claimed=false, skipped=false;
  function storage(name) {
    if(!stores.has(name))stores.set(name,new Map());
    const entries=stores.get(name);
    return {
      async keys(){cacheOps.push(['keys',name]);return [...entries.keys()].map(x=>new Request(x));},
      async match(req){cacheOps.push(['match',name,key(req)]);const r=entries.get(key(req));return r?copy(r):undefined;},
      async put(req,r){cacheOps.push(['put',name,key(req)]);entries.set(key(req),copy(r));},
      async delete(req){cacheOps.push(['entry-delete',name,key(req)]);return entries.delete(key(req));},
      async add(req){cacheOps.push(['add',name,key(req)]);throw new Error('Unexpected cache.add');},
      async addAll(req){cacheOps.push(['addAll',name]);throw new Error('Unexpected cache.addAll');}
    };
  }
  const caches={
    async open(name){cacheOps.push(['open',name]);return storage(name);},
    async keys(){cacheOps.push(['cache-keys']);return [...stores.keys()];},
    async delete(name){cacheOps.push(['cache-delete',name]);return stores.delete(name);},
    async match(req){cacheOps.push(['global-match',key(req)]);for(const s of stores.values()){if(s.has(key(req)))return copy(s.get(key(req)));}}
  };
  const fetch=async(req,options)=>{network.push({url:key(req),method:req.method||'GET',headers:Object.fromEntries(req.headers||[]),options});return networkBehavior(req,options);};
  const self={location:{origin},addEventListener:(name,handler)=>handlers[name]=handler,
    skipWaiting:async()=>{skipped=true;},clients:{claim:async()=>{claimed=true;}}};
  const context=vm.createContext({self,caches,fetch,URL,Request,Response,Promise});
  vm.runInContext(source,context,{filename:'static/sw.js'});
  return {stores,cacheOps,network,context,handlers,
    seed(name,path,body='OLD PRIVATE',headers={}){storage(name);stores.get(name).set(new URL(path,origin).href,response(body,200,new URL(path,origin).href,headers));},
    behavior(fn){networkBehavior=fn;},claimed:()=>claimed,skipped:()=>skipped,
    async lifecycle(name){const waits=[];handlers[name]({waitUntil:p=>waits.push(p)});await Promise.all(waits);},
    async request(path,method='GET',headers={}){
      const req=new Request(new URL(path,origin),{method,headers});
      const waits=[];let promise,intercepted=false;
      handlers.fetch({request:req,respondWith:p=>{intercepted=true;promise=p;},waitUntil:p=>waits.push(p)});
      try {const r=await(intercepted?promise:fetch(req));await Promise.all(waits);return {r,intercepted};}
      catch(error){await Promise.allSettled(waits);return {error,intercepted};}
    }
  };
}
(async()=>{
  const e=environment();
  check('PWA_CACHE_VERSION','new deterministic cache',vm.runInContext('CACHE_NAME',e.context),'qlcv-mobile-v2');
  const precache=Array.from(vm.runInContext('ASSETS_TO_CACHE',e.context));
  check('PWA_NO_PRIVATE_WRITE','public-only precache',precache.every(p=>vm.runInContext('isPublicAsset(new URL('+JSON.stringify(p)+',self.location.origin))',e.context)));
  check('PWA_NO_PRIVATE_WRITE','no authenticated mobile precache',!precache.includes('/mobile'));
  const privatePaths=['/static/uploads/file','/static/uploads/file-b','/static/uploads/file?x=1','/static/uploads/file#fragment',
    '/static//uploads/file','/static/./uploads/file','/static/UPLOADS/file','/static/%75ploads/file',
    '/static/uploads%2ffile','/static/uploads%5cfile','/static/%2575ploads/file',
    '/static/uploads/%252e%252e%252fsecret','/static/uploads//file','/static/uploads'];
  for(const p of privatePaths) check('PWA_PRIVATE_CLASSIFICATION',p,vm.runInContext('isPrivateUpload(new URL('+JSON.stringify(p)+',self.location.origin))',e.context));
  for(const p of ['/static/uploads2/file','/static/upload/file','/foo/static/uploads/file','/static/css/a.css?x=/static/uploads/file','https://other.test/static/uploads/file'])
    check('PWA_PRIVATE_CLASSIFICATION','lookalike '+p,vm.runInContext('isPrivateUpload(new URL('+JSON.stringify(p)+',self.location.origin))',e.context),false);
  await e.lifecycle('install');
  check('PWA_PUBLIC_CACHE','install public shell count',e.stores.get('qlcv-mobile-v2').size,2);
  check('PWA_CACHE_VERSION','skipWaiting after install',e.skipped());
  check('PWA_NO_PRIVATE_WRITE','install no add/addAll',!e.cacheOps.some(x=>['add','addAll'].includes(x[0])));
  for(const cache of ['qlcv-mobile-v1','qlcv-mobile-v0','qlcv-mobile-v2','qlcv-mobile-v12']) {
    e.seed(cache,'/static/css/mobile.css','PUBLIC CSS');
    e.seed(cache,'/static/js/public.js','PUBLIC JS');
    e.seed(cache,'/manifest.json','PUBLIC MANIFEST');
    e.seed(cache,'/static/other-public.css','OTHER PUBLIC');
    for(const path of privatePaths)e.seed(cache,path);
    e.seed(cache,'/mobile','OLD USER HTML');e.seed(cache,'/api/tasks','OLD TASK DATA');
    e.seed(cache,'https://other.test/static/private','OLD CROSS ORIGIN');
  }
  for(const cache of ['third-party-cache','qlcv-mobile-vendor'])e.seed(cache,'/static/uploads/file','UNRELATED CACHE');
  const untouched=[...e.stores.entries()].filter(([n])=>!/^qlcv-mobile-v[0-9]+$/.test(n)).map(([n,s])=>[n,[...s.keys()]]);
  e.cacheOps.length=0;await e.lifecycle('activate');
  for(const p of privatePaths)check('PWA_OLD_CACHE_PURGE',p,[...e.stores.entries()].filter(([n])=>/^qlcv-mobile-v[0-9]+$/.test(n)).every(([,s])=>!s.has(new URL(p,origin).href)));
  check('PWA_OLD_CACHE_PURGE','no private cache read during purge',!e.cacheOps.some(x=>x[0]==='match'&&x[2]&&privatePaths.some(p=>new URL(p,origin).href===x[2])));
  check('PWA_OLD_CACHE_PURGE','all obsolete QLCV versions removed',!['qlcv-mobile-v1','qlcv-mobile-v0','qlcv-mobile-v12'].some(n=>e.stores.has(n)));
  check('PWA_OLD_CACHE_PURGE','only app-owned versions deleted',e.cacheOps.filter(x=>x[0]==='cache-delete').every(x=>/^qlcv-mobile-v[0-9]+$/.test(x[1])));
  check('PWA_OLD_CACHE_PURGE','unrelated caches untouched',untouched.every(([n,keys])=>JSON.stringify([...e.stores.get(n).keys()])===JSON.stringify(keys)));
  check('PWA_OLD_CACHE_PURGE','authenticated HTML/API/crossorigin purged',!['/mobile','/api/tasks','https://other.test/static/private'].some(p=>e.stores.get('qlcv-mobile-v2').has(new URL(p,origin).href)));
  check('PWA_CACHE_VERSION','claim after purge',e.claimed());
  for(const p of ['/static/css/mobile.css','/static/js/public.js','/manifest.json','/static/other-public.css'])
    check('PWA_PUBLIC_CACHE','public migration '+p,e.stores.get('qlcv-mobile-v2').has(new URL(p,origin).href));
  async function privateCase(name,status=200,method='GET',headers={},offline=false) {
    e.seed('qlcv-mobile-v2','/static/uploads/file','OLD PRIVATE');
    e.seed('qlcv-mobile-v1','/static/uploads/file','OLD PRIVATE');
    e.behavior(async req=>{if(offline)throw new Error('OFFLINE');return response('GATEWAY '+name,status,key(req),{'Cache-Control':'private, no-store'});});
    const start=e.cacheOps.length, calls=e.network.length;
    const result=await e.request('/static/uploads/file',method,headers);
    check('PWA_NETWORK_ONLY',name+' one network request',e.network.length-calls,1);
    check('PWA_NETWORK_ONLY',name+' no HTTP-cache use',e.network.at(-1).options?.cache,'no-store');
    check('PWA_NO_PRIVATE_WRITE',name+' no Cache API read/write',e.cacheOps.length-start,0);
    check('PWA_METHODS',name+' original method',e.network.at(-1).method,method);
    if(offline)check('PWA_OFFLINE_PRIVATE',name+' rejects no cached bytes',!!result.error);
    else check('PWA_NETWORK_ONLY',name+' gateway status preserved',result.r.status,status);
    if(result.r&&![204,205,304].includes(status))check('PWA_NETWORK_ONLY',name+' not old cached body',!(await result.r.text()).includes('OLD PRIVATE'));
    check('PWA_ZERO_MUTATION',name+' existing fixture bytes untouched',await e.stores.get('qlcv-mobile-v1').get(origin+'/static/uploads/file').clone().text(),'OLD PRIVATE');
  }
  for(const [name,status] of [['authorized',200],['anonymous',401],['unauthorized',403],['missing',404],['UNKNOWN',404],['unregistered',404],['server error',500],['user switch',401],['tenant switch',404],['logout',401]])await privateCase(name,status);
  for(const method of ['HEAD','POST','PUT','PATCH','DELETE','OPTIONS'])await privateCase(method,method==='HEAD'?200:405,method);
  await privateCase('Range',206,'GET',{'Range':'bytes=0-3'});
  check('PWA_METHODS','Range header forwarded',e.network.at(-1).headers.range,'bytes=0-3');
  await privateCase('conditional',304,'GET',{'If-None-Match':'synthetic'});
  check('PWA_METHODS','conditional header forwarded',e.network.at(-1).headers['if-none-match'],'synthetic');
  for(const name of ['offline','offline logout','offline tenant switch'])await privateCase(name,200,'GET',{},true);
  // Each alias receives network-only even with an old cached success present.
  for(const path of privatePaths){
    e.seed('qlcv-mobile-v2',path);const start=e.cacheOps.length;
    e.behavior(async()=>{throw new Error('OFFLINE');});const result=await e.request(path);
    check('PWA_OFFLINE_PRIVATE','alias rejects '+path,!!result.error);
    check('PWA_NO_PRIVATE_WRITE','alias no cache '+path,e.cacheOps.length-start,0);
  }
  // Dynamic HTML/API must not fall back to historical authenticated mobile HTML.
  for(const path of ['/mobile','/dashboard','/api/tasks','/api/documents/library','/logout']){
    e.seed('qlcv-mobile-v2',path,'OLD USER HTML');const start=e.cacheOps.length;
    e.behavior(async()=>{throw new Error('OFFLINE');});const result=await e.request(path);
    check('PWA_OFFLINE_PRIVATE','dynamic private '+path,!!result.error);
    check('PWA_NO_PRIVATE_WRITE','dynamic no cache '+path,e.cacheOps.length-start,0);
  }
  for(const path of ['https://other.test/static/uploads/file','https://other.test/static/style.css']){
    const start=e.cacheOps.length;e.behavior(async()=>response());const result=await e.request(path);
    check('PWA_CROSS_ORIGIN','no interception '+path,result.intercepted,false);
    check('PWA_CROSS_ORIGIN','no Cache API '+path,e.cacheOps.length-start,0);
  }
  e.behavior(async req=>response('PUBLIC NETWORK',200,key(req)));
  await e.request('/static/css/new.css?x=/static/uploads/file');
  check('PWA_PUBLIC_CACHE','query string not private',e.stores.get('qlcv-mobile-v2').has(origin+'/static/css/new.css?x=/static/uploads/file'));
  e.behavior(async()=>{throw new Error('OFFLINE');});
  const offline=await e.request('/static/js/public.js');
  check('PWA_PUBLIC_CACHE','public offline body',await offline.r.text(),'PUBLIC JS');
  const missing=await e.request('/static/js/absent.js');
  check('PWA_PUBLIC_CACHE','no private HTML offline fallback',missing.r.status,503);
  // Public URL cannot smuggle a redirected private/no-store response into cache.
  for(const [name,headers,url,redirected] of [['no-store',{'Cache-Control':'private, no-store'},origin+'/static/css/no-store.css',false],
    ['private final URL',{},origin+'/static/uploads/file',false],['redirect',{},origin+'/static/css/redirect.css',true],
    ['HTML',{'Content-Type':'text/html'},origin+'/static/css/html.css',false]]){
    const requestPath='/static/css/unsafe-'+name.replaceAll(' ','-')+'.css';
    e.behavior(async()=>{const r=response('PRIVATE RESPONSE',200,url,headers);Object.defineProperty(r,'redirected',{value:redirected});return r;});
    await e.request(requestPath);
    check('PWA_NO_PRIVATE_WRITE','unsafe public response '+name,!e.stores.get('qlcv-mobile-v2').has(origin+requestPath));
  }
  // Full-run integration replays actual synthetic FastAPI gateway responses,
  // including successful bytes, 401/404/HEAD/206/304. No real provider/network.
  for(const fixture of fixtures){
    const category=fixture.name.startsWith('B4B5 ')?'B4B5 LEGACY_PWA_INTEGRATION':fixture.name.startsWith('LEGACY ')?'PROVENANCE_PWA_INTEGRATION':'PWA_4B3_INTEGRATION';
    e.seed('qlcv-mobile-v2',fixture.path,'OLD PRIVATE');const start=e.cacheOps.length;
    e.behavior(async req=>response(fixture.body,fixture.status,key(req),fixture.headers));
    const result=await e.request(fixture.path,fixture.method,fixture.request_headers||{});
    check(category,fixture.name+' actual gateway status',result.r.status,fixture.status);
    check(category,fixture.name+' no Cache API',e.cacheOps.length-start,0);
    check(category,fixture.name+' server no-store',result.r.headers.get('Cache-Control'),'private, no-store');
    if(!['HEAD'].includes(fixture.method)&&fixture.status!==304)check(category,fixture.name+' exact actual gateway body',await result.r.text(),fixture.body);
    if(category==='PROVENANCE_PWA_INTEGRATION'||category==='B4B5 LEGACY_PWA_INTEGRATION'){
      e.behavior(async()=>{throw new Error('OFFLINE');});
      const offlineLegacy=await e.request(fixture.path);
      check(category,fixture.name+' offline never cached',offlineLegacy.error && offlineLegacy.error.message,'OFFLINE');
    }
  }
  process.stdout.write(JSON.stringify({complete:true,real_browser:'NOT RUN',kind:'Node VM actual SW / synthetic CacheStorage and network',results}));
})().catch(error=>{process.stderr.write(error.stack);process.exitCode=1;});
"""


def run_pwa_tests(run, sw_path, fixtures=None):
    """Parent-only Node VM; no browser profiles, real fetch or production writes."""
    before=inventory()
    args=[shutil.which('node') or 'node','--eval',PWA_TEST_JS,str(sw_path)]
    if fixtures:
        args.append(str(fixtures))
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf-8',timeout=60)
    if result.returncode:
        (run/'pwa_infrastructure_error.txt').write_text(result.stderr,encoding='utf-8')
        raise RuntimeError('PWA test infrastructure failed; see isolated report')
    report=json.loads(result.stdout)
    after=inventory()
    report['results'].append({'test':'PWA_ZERO_MUTATION protected production inventory','actual':before==after,'expected':True,'pass':before==after})
    (run/'pwa_results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    if before!=after:
        raise RuntimeError('STOP: PWA production integrity modified; no rollback')
    return report


def pwa_targeted():
    run=PROJECT/'.test_runtime'/('run-'+uuid.uuid4().hex)
    run.mkdir(parents=True)
    source=PROJECT/'static/sw.js'
    digest=hashlib.sha256(source.read_bytes()).hexdigest()
    snapshot=run/'sw.js';shutil.copyfile(source,snapshot)
    report=run_pwa_tests(run,snapshot)
    (run/'pwa_source_manifest.json').write_text(json.dumps({'static/sw.js':digest}),encoding='utf-8')
    print('PWA targeted report:',run.relative_to(PROJECT))
    print('PWA PASS/FAIL:',sum(r['pass'] for r in report['results']),sum(not r['pass'] for r in report['results']))
    if hashlib.sha256(source.read_bytes()).hexdigest()!=digest:
        raise SystemExit('STOP: SW source changed during targeted test')
    raise SystemExit(1 if any(not r['pass'] for r in report['results']) else 0)


def main():
    before = inventory()
    run = PROJECT / '.test_runtime' / ('run-' + uuid.uuid4().hex)
    appdir = run / 'app'
    appdir.mkdir(parents=True)
    (run / 'temp').mkdir()
    manifest = {}
    for folder in ['database', 'models', 'routes', 'services']:
        (appdir / folder).mkdir()
        for src in (PROJECT / folder).glob('*.py'):
            if 'khach_hang' not in src.name:
                shutil.copyfile(src, appdir / folder / src.name)
                manifest[str(src.relative_to(PROJECT))] = hashlib.sha256(src.read_bytes()).hexdigest()
    for name in ['app.py', 'config.py']:
        shutil.copyfile(PROJECT / name, appdir / name)
        manifest[name] = hashlib.sha256((PROJECT / name).read_bytes()).hexdigest()
    shutil.copytree(PROJECT / 'templates', appdir / 'templates', ignore=shutil.ignore_patterns('crm*'))
    shutil.copytree(PROJECT / 'static', appdir / 'static', ignore=shutil.ignore_patterns('uploads', '*.html'))
    manifest['static/sw.js']=hashlib.sha256((PROJECT/'static/sw.js').read_bytes()).hexdigest()
    (appdir / 'static/uploads').mkdir()
    (run / 'source_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (run / 'integrity_before.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
    completed = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), '--worker', str(run)], cwd=appdir)
    if completed.returncode==0:
        # Parent orchestrates independent workers; their own guards forbid any
        # DB/write/network access outside this run. Existing worker guard unchanged.
        workers=[subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),
                 '--registry-process',str(run),str(i)],cwd=appdir) for i in range(2)]
        exits=[p.wait(timeout=30) for p in workers]
        if any(exits):
            raise RuntimeError('Registry process test infrastructure failure')
        process_results=[json.loads((run/('registry_process_'+str(i)+'.json')).read_text()) for i in range(2)]
        report_path=run/'runtime_results.json'
        report=json.loads(report_path.read_text())
        checks=[('distinct no lost updates',len({fid for p in process_results for fid in p['distinct']}),16),
                ('same locator one winner',sum(p['same'] is not None for p in process_results),1),
                ('exact binding idempotent',len({p['exact'] for p in process_results}),1),
                ('conflicting slot one winner',sum(p['conflict'] is not None for p in process_results),1),
                ('database remains readable',all(p['readable'] for p in process_results),True)]
        report['results'].extend({'test':'REGISTRY CONCURRENCY PROCESS '+name,'actual':actual,
            'expected':expected,'pass':actual==expected} for name,actual,expected in checks)
        # Inspect test sidecar read-only after both guarded replacement workers exit.
        metadata=sqlite3.connect((run/'private_metadata/file_registry.sqlite3').as_uri()+'?mode=ro',uri=True)
        live=metadata.execute("SELECT state FROM bindings WHERE object_id='process-replacement' AND state='ACTIVE'").fetchall()
        shared=metadata.execute("SELECT state FROM bindings WHERE object_id='process-exact' AND state='ACTIVE'").fetchall()
        metadata.close()
        replacements=[('one reservation winner',sum(p['replacement'] is not None for p in process_results),1),
                      ('old ACTIVE preserved until activation',all(p['old_preserved'] for p in process_results),True),
                      ('one final ACTIVE generation',len(live),1),
                      ('exact retry idempotent',all(p['retry'] for p in process_results),True),
                      ('other shared binding preserved',len(shared),1)]
        report['results'].extend({'test':'B4B2 CONCURRENCY PROCESS '+name,'actual':actual,
            'expected':expected,'pass':actual==expected} for name,actual,expected in replacements)
        pwa=run_pwa_tests(run,appdir/'static/sw.js',run/'pwa_gateway_fixtures.json')
        report['results'].extend(pwa['results'])
        report['pwa_evidence']={'kind':pwa['kind'],'real_browser':'NOT RUN','report':'pwa_results.json'}
        report_path.write_text(json.dumps(report,indent=2),encoding='utf-8')
    after = inventory()
    unchanged = before == after
    source_unchanged = all(hashlib.sha256((PROJECT / name).read_bytes()).hexdigest() == digest for name, digest in manifest.items())
    (run / 'integrity.json').write_text(json.dumps({'before': before, 'after': after, 'production_data_modified': not unchanged}, indent=2), encoding='utf-8')
    print('Report directory:', run.relative_to(PROJECT))
    print('PRODUCTION DB/DATA MODIFIED =', 'NO' if unchanged else 'YES')
    if not unchanged:
        raise SystemExit('STOP: production integrity changed; no rollback attempted')
    if not source_unchanged:
        raise SystemExit('STOP: source changed while snapshot was tested; rerun on fresh snapshot')
    raise SystemExit(completed.returncode)


if __name__ == '__main__':
    if len(sys.argv)==2 and sys.argv[1]=='--pwa-test':
        pwa_targeted()
    elif len(sys.argv)==4 and sys.argv[1]=='--registry-process':
        registry_process(Path(sys.argv[2]),sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[1] == '--worker':
        worker(Path(sys.argv[2]))
    else:
        main()

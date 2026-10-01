"""Lazy private metadata primitives; no business ACL, HTTP or physical-file writes.

Only explicitly initialize a NEW sidecar. Existing invalid state is never reset.
SQLite is authoritative across workers; business DB commits are NOT atomic here.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
import re
import sqlite3
import uuid


class RegistryError(RuntimeError):
    """Controlled fail-closed metadata error; no internal path in message."""


def _text(value):
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise RegistryError("Invalid metadata identity")
    return value.strip()


def _now():
    return datetime.now(timezone.utc).isoformat()


class FileRegistry:
    VERSION = 3
    FILE_COLUMNS = ('file_id tenant_id uploader_id storage_root_id storage_name original_name '
                    'created_at size sha256 classification state expires_at version '
                    'provenance_type review_id reviewed_by review_evidence').split()
    BINDING_COLUMNS = ('binding_id file_id tenant_id object_kind object_id field_slot generation '
                       'state created_at updated_at').split()

    def __init__(self, path=None, *, busy_ms=300, verified_local_disk=False, wal=False):
        from config import Config
        self.root = Config.FILE_REGISTRY_ROOT.resolve()
        self.path = Path(path or Config.FILE_REGISTRY_PATH).resolve()
        self.forbidden = [Path(__file__).resolve().parents[1] / 'static',
                          Path(Config.UPLOAD_DIR).resolve()]
        import os
        local_docs = os.getenv('LOCAL_DOCS_DIR', '').strip()
        if local_docs:
            self.forbidden.append(Path(local_docs).resolve())
        if not isinstance(busy_ms, int) or not 1 <= busy_ms <= 5000 or (wal and not verified_local_disk):
            raise RegistryError("Invalid registry configuration")
        self.busy_ms, self.wal = busy_ms, wal
        self._check_path()

    def _check_path(self):
        resolved = self.path.resolve()
        if resolved != self.path or not resolved.is_relative_to(self.root) or resolved == self.root:
            raise RegistryError("Registry path confinement failed")
        if any(resolved.is_relative_to(p.resolve()) or self.root.is_relative_to(p.resolve())
               for p in self.forbidden):
            raise RegistryError("Registry path is public")

    def _validate(self, conn, *, allow_v2=False):
        version=conn.execute('PRAGMA user_version').fetchone()[0]
        if version != self.VERSION and not (allow_v2 and version==2):
            raise RegistryError("Unsupported registry schema; explicit sidecar migration required")
        for table, columns in [('files', self.FILE_COLUMNS if version==3 else self.FILE_COLUMNS[:-4]), ('bindings', self.BINDING_COLUMNS)]:
            if [r[1] for r in conn.execute('PRAGMA table_info(' + table + ')')] != columns:
                raise RegistryError("Invalid registry schema")
        indexes={r[1]:r for r in conn.execute('PRAGMA index_list(bindings)')}
        for name,state in [('binding_slot_active','ACTIVE'),('binding_slot_pending','PENDING')]:
            entry=indexes.get(name)
            sql=conn.execute('SELECT sql FROM sqlite_master WHERE type=\'index\' AND name=?',(name,)).fetchone()
            columns=[r[2] for r in conn.execute('PRAGMA index_info('+name+')')]
            if (not entry or entry[2]!=1 or entry[4]!=1 or not sql
                    or "WHERE state='"+state+"'" not in sql[0]
                    or columns!=['tenant_id','object_kind','object_id','field_slot']):
                raise RegistryError("Invalid registry replacement constraints")

    @staticmethod
    def valid_provenance(row):
        if row.get('provenance_type')=='VERIFIED_UPLOADER':
            return bool(isinstance(row.get('uploader_id'),str) and row['uploader_id'].strip()
                        and row['classification'] in ('PRIVATE','UNKNOWN')
                        and not any(row.get(k) for k in ('review_id','reviewed_by','review_evidence')))
        if row.get('provenance_type')=='LEGACY_VERIFIED_MAPPING':
            return bool(row.get('uploader_id') is None and row['classification']=='VERIFIED_LEGACY'
                        and row['state'] in ('BOUND','REVOKED') and row.get('expires_at') is None
                        and all(isinstance(row.get(k),str) and row[k].strip() for k in ('review_id','reviewed_by'))
                        and isinstance(row.get('review_evidence'),str)
                        and re.fullmatch('[0-9a-f]{64}',row['review_evidence']))
        return False

    @contextmanager
    def _connection(self, mutation=False, new=False):
        conn = None
        self._check_path()
        if not self.path.is_file() or (not new and self.path.stat().st_size == 0):
            raise RegistryError("Registry unavailable")
        try:
            conn = sqlite3.connect(str(self.path), timeout=self.busy_ms / 1000, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('PRAGMA busy_timeout=' + str(self.busy_ms))
            if not new:
                self._validate(conn)
            if mutation:
                conn.execute('BEGIN IMMEDIATE')
            yield conn
            if mutation:
                conn.commit()
        except (sqlite3.Error, OSError) as exc:
            raise RegistryError("Registry operation failed") from exc
        finally:
            if conn:
                if conn.in_transaction:
                    conn.rollback()
                conn.close()

    def initialize_registry(self):
        self._check_path()
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._check_path()
            try:
                with self.path.open('xb'):
                    pass
            except FileExistsError:
                with self._connection() as conn:
                    if conn.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                        raise RegistryError("Registry corrupt")
                return
            with self._connection(mutation=True, new=True) as conn:
                conn.execute("""CREATE TABLE files (
                    file_id TEXT PRIMARY KEY, tenant_id TEXT NOT NULL, uploader_id TEXT,
                    storage_root_id TEXT NOT NULL, storage_name TEXT NOT NULL, original_name TEXT NOT NULL,
                    created_at TEXT NOT NULL, size INTEGER, sha256 TEXT,
                    classification TEXT NOT NULL CHECK(classification IN ('PRIVATE','UNKNOWN','VERIFIED_LEGACY')),
                    state TEXT NOT NULL CHECK(state IN ('WRITING','UNBOUND','BOUND','REVOKED')),
                    expires_at TEXT, version INTEGER NOT NULL CHECK(version > 0),
                    provenance_type TEXT NOT NULL CHECK(provenance_type IN ('VERIFIED_UPLOADER','LEGACY_VERIFIED_MAPPING')),
                    review_id TEXT, reviewed_by TEXT, review_evidence TEXT,
                    CHECK((provenance_type='VERIFIED_UPLOADER' AND uploader_id IS NOT NULL AND length(trim(uploader_id))>0
                           AND classification IN ('PRIVATE','UNKNOWN') AND review_id IS NULL AND reviewed_by IS NULL AND review_evidence IS NULL)
                       OR (provenance_type='LEGACY_VERIFIED_MAPPING' AND uploader_id IS NULL AND classification='VERIFIED_LEGACY'
                           AND state IN ('BOUND','REVOKED') AND expires_at IS NULL AND review_id IS NOT NULL
                           AND reviewed_by IS NOT NULL AND review_evidence IS NOT NULL)),
                    UNIQUE(storage_root_id,storage_name), UNIQUE(file_id,tenant_id))""")
                conn.execute("""CREATE TABLE bindings (
                    binding_id TEXT PRIMARY KEY, file_id TEXT NOT NULL, tenant_id TEXT NOT NULL,
                    object_kind TEXT NOT NULL, object_id TEXT NOT NULL, field_slot TEXT NOT NULL,
                    generation INTEGER NOT NULL CHECK(generation > 0),
                    state TEXT NOT NULL CHECK(state IN ('PENDING','ACTIVE','REVOKED')),
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                    FOREIGN KEY(file_id,tenant_id) REFERENCES files(file_id,tenant_id))""")
                conn.execute("CREATE UNIQUE INDEX binding_slot_active ON bindings(tenant_id,object_kind,object_id,field_slot) WHERE state='ACTIVE'")
                conn.execute("CREATE UNIQUE INDEX binding_slot_pending ON bindings(tenant_id,object_kind,object_id,field_slot) WHERE state='PENDING'")
                conn.execute('CREATE INDEX file_tenant ON files(tenant_id,state)')
                conn.execute('CREATE INDEX binding_file ON bindings(file_id,tenant_id,state)')
                conn.execute('PRAGMA user_version=3')
            if self.wal:
                with self._connection() as conn:
                    if conn.execute('PRAGMA journal_mode=WAL').fetchone()[0] != 'wal':
                        raise RegistryError("Registry WAL unavailable")
        except OSError as exc:
            raise RegistryError("Registry initialization failed") from exc

    def register_writing(self, tenant_id, uploader_id, storage_root_id, storage_name,
                         original_name, *, classification='PRIVATE', file_id=None):
        tenant_id, uploader_id, storage_root_id = map(_text, (tenant_id, uploader_id, storage_root_id))
        storage_name = _text(storage_name)
        if storage_name in ('.', '..') or any(c in storage_name for c in '/\\:%'):
            raise RegistryError("Invalid storage basename")
        original_name = _text(original_name)
        if classification not in ('PRIVATE', 'UNKNOWN'):
            raise RegistryError("Invalid classification")
        file_id = file_id or str(uuid.uuid4())
        try:
            if str(uuid.UUID(file_id)) != file_id:
                raise ValueError()
        except (ValueError, TypeError, AttributeError) as exc:
            raise RegistryError("Invalid file ID") from exc
        with self._connection(mutation=True) as conn:
            conn.execute('INSERT INTO files VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (file_id, tenant_id, uploader_id, storage_root_id, storage_name, original_name,
                 _now(), None, None, classification, 'WRITING', None, 1,
                 'VERIFIED_UPLOADER',None,None,None))
        return file_id

    def complete_unbound(self, file_id, tenant_id, size, sha256):
        if isinstance(size, bool) or not isinstance(size, int) or size < 0 or not isinstance(sha256, str) or not re.fullmatch('[0-9a-f]{64}', sha256):
            raise RegistryError("Invalid file completion")
        expires = (datetime.now(timezone.utc) + timedelta(hours=24)).isoformat()
        with self._connection(mutation=True) as conn:
            if conn.execute("UPDATE files SET state='UNBOUND',size=?,sha256=?,expires_at=?,version=version+1 WHERE file_id=? AND tenant_id=? AND state='WRITING'", (size, sha256, expires, file_id, tenant_id)).rowcount != 1:
                raise RegistryError("Invalid file transition")

    def get_file(self, file_id, tenant_id):
        with self._connection() as conn:
            row = conn.execute('SELECT * FROM files WHERE file_id=? AND tenant_id=?', (file_id, tenant_id)).fetchone()
            return dict(row) if row else None

    def get_file_by_storage(self, tenant_id, storage_root_id, storage_name):
        with self._connection() as conn:
            row = conn.execute('SELECT * FROM files WHERE tenant_id=? AND storage_root_id=? AND storage_name=?', (tenant_id, storage_root_id, storage_name)).fetchone()
            return dict(row) if row else None

    @staticmethod
    def expired_unbound(record, now=None):
        return bool(record and record['state'] == 'UNBOUND' and record['expires_at'] and
                    datetime.fromisoformat(record['expires_at']) <= (now or datetime.now(timezone.utc)))

    def create_pending_binding(self, file_id, tenant_id, object_kind, object_id, field_slot, generation=1, *, replacement=False):
        tenant_id, object_id, field_slot = map(_text, (tenant_id, object_id, field_slot))
        if object_kind not in ('TASK', 'DOCUMENT', 'PERSONAL') or isinstance(generation, bool) or not isinstance(generation, int) or generation < 1:
            raise RegistryError("Invalid binding")
        with self._connection(mutation=True) as conn:
            file = conn.execute('SELECT * FROM files WHERE file_id=? AND tenant_id=?', (file_id, tenant_id)).fetchone()
            if not file or not self.valid_provenance(dict(file)) or file['classification'] == 'UNKNOWN' or file['state'] not in ('UNBOUND','BOUND') or self.expired_unbound(dict(file)):
                raise RegistryError("File cannot be bound")
            old = conn.execute("SELECT * FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=? AND state IN ('PENDING','ACTIVE') ORDER BY CASE state WHEN 'PENDING' THEN 0 ELSE 1 END", (tenant_id, object_kind, object_id, field_slot)).fetchone()
            if old:
                if old['file_id'] == file_id and (replacement or old['generation'] == generation):
                    return old['binding_id']
                if old['state']=='PENDING' or not replacement:
                    raise RegistryError("Binding conflict")
            if replacement:
                last=conn.execute('SELECT COALESCE(MAX(generation),0) FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=?',(tenant_id,object_kind,object_id,field_slot)).fetchone()[0]
                generation=last+1
            binding = str(uuid.uuid4())
            now = _now()
            conn.execute('INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?,?,?)',
                         (binding,file_id,tenant_id,object_kind,object_id,field_slot,generation,'PENDING',now,now))
            return binding

    def activate_binding(self, binding_id, tenant_id, *, expected_generation=None, connection=None):
        if connection is None:
            with self._connection(mutation=True) as conn:
                return self.activate_binding(binding_id,tenant_id,expected_generation=expected_generation,connection=conn)
        conn=connection
        binding = conn.execute('SELECT * FROM bindings WHERE binding_id=? AND tenant_id=?', (binding_id,tenant_id)).fetchone()
        if not binding or binding['state'] not in ('PENDING','ACTIVE') or (expected_generation is not None and binding['generation']!=expected_generation):
            raise RegistryError("Invalid binding transition")
        file = conn.execute('SELECT * FROM files WHERE file_id=? AND tenant_id=?', (binding['file_id'],tenant_id)).fetchone()
        if not file or not self.valid_provenance(dict(file)) or file['classification']=='UNKNOWN' or file['state'] not in ('UNBOUND','BOUND') or self.expired_unbound(dict(file)):
            raise RegistryError("File cannot activate")
        if binding['state']=='ACTIVE':
            return
        old=conn.execute("SELECT * FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=? AND state='ACTIVE'",(tenant_id,binding['object_kind'],binding['object_id'],binding['field_slot'])).fetchone()
        if old and old['generation']>=binding['generation']:
            raise RegistryError("Stale binding generation")
        if old:
            conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE binding_id=?",(_now(),old['binding_id']))
        conn.execute("UPDATE bindings SET state='ACTIVE',updated_at=? WHERE binding_id=?", (_now(),binding_id))
        conn.execute("UPDATE files SET state='BOUND',version=version+1 WHERE file_id=?", (file['file_id'],))

    def slot_bindings(self, tenant_id, object_kind, object_id, field_slot, *, connection=None):
        if connection is None:
            with self._connection() as conn:
                return self.slot_bindings(tenant_id,object_kind,object_id,field_slot,connection=conn)
        return [dict(r) for r in connection.execute("SELECT * FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=? AND state IN ('PENDING','ACTIVE')",(tenant_id,object_kind,object_id,field_slot))]

    def get_storage_record(self, storage_root_id, storage_name):
        with self._connection() as conn:
            row=conn.execute('SELECT * FROM files WHERE storage_root_id=? AND storage_name=?',(storage_root_id,storage_name)).fetchone()
            return dict(row) if row else None

    def access_snapshot(self, tenant_id, storage_root_id, storage_name):
        """Read-only coherent metadata snapshot; never initialize/recover/reset."""
        self._check_path()
        if not self.path.is_file():
            raise RegistryError('Registry unavailable')
        try:
            conn=sqlite3.connect(self.path.as_uri()+'?mode=ro',uri=True,
                                timeout=self.busy_ms/1000,isolation_level=None)
            try:
                conn.row_factory=sqlite3.Row
                conn.execute('PRAGMA foreign_keys=ON')
                conn.execute('PRAGMA query_only=ON')
                conn.execute('PRAGMA busy_timeout='+str(self.busy_ms))
                conn.execute('BEGIN')
                self._validate(conn,allow_v2=True)
                row=conn.execute('SELECT * FROM files WHERE tenant_id=? AND storage_root_id=? AND storage_name=?',
                                 (tenant_id,storage_root_id,storage_name)).fetchone()
                bindings=[] if row is None else [dict(b) for b in conn.execute(
                    "SELECT * FROM bindings WHERE file_id=? AND tenant_id=? AND state='ACTIVE'",
                    (row['file_id'],tenant_id))]
                record=dict(row) if row else None
                if record and 'provenance_type' not in record:
                    # v2 is READ ONLY; no schema upgrade or inferred legacy trust.
                    record.update(provenance_type='VERIFIED_UPLOADER',review_id=None,reviewed_by=None,review_evidence=None)
                if record and not self.valid_provenance(record):
                    raise RegistryError('Invalid file provenance')
                return record,bindings
            finally:
                conn.rollback()
                conn.close()
        except (sqlite3.Error,OSError) as exc:
            raise RegistryError('Registry read unavailable') from exc

    def get_binding(self, binding_id, tenant_id):
        with self._connection() as conn:
            row=conn.execute('SELECT * FROM bindings WHERE binding_id=? AND tenant_id=?',(binding_id,tenant_id)).fetchone()
            return dict(row) if row else None

    def revoke_pending(self, binding_id, tenant_id):
        # Compensation never revokes an ACTIVE retry or someone else's slot.
        with self._connection(mutation=True) as conn:
            conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE binding_id=? AND tenant_id=? AND state='PENDING'",(_now(),binding_id,tenant_id))

    def revoke_binding(self, binding_id, tenant_id):
        with self._connection(mutation=True) as conn:
            if conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE binding_id=? AND tenant_id=?", (_now(),binding_id,tenant_id)).rowcount != 1:
                raise RegistryError("Binding unavailable")

    def list_active_bindings(self, file_id, tenant_id):
        with self._connection() as conn:
            return [dict(r) for r in conn.execute("SELECT b.* FROM bindings b JOIN files f ON f.file_id=b.file_id AND f.tenant_id=b.tenant_id WHERE b.file_id=? AND b.tenant_id=? AND b.state='ACTIVE' AND f.state='BOUND' AND f.classification!='UNKNOWN'", (file_id,tenant_id))]

    def mark_revoked(self, file_id, tenant_id):
        with self._connection(mutation=True) as conn:
            if conn.execute("UPDATE files SET state='REVOKED',version=version+1 WHERE file_id=? AND tenant_id=?", (file_id,tenant_id)).rowcount != 1:
                raise RegistryError("File unavailable")
            conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE file_id=? AND tenant_id=?", (_now(),file_id,tenant_id))

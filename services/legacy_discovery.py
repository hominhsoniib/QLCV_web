"""Offline read-only discovery and signed custodian review; no app startup import.

References are observations, NEVER ownership. Structurally consistent observations
remain UNKNOWN until independent custodian evidence is explicitly approved.
The only apply entry point in this slice is confined to a guarded synthetic run.
No configuration/app imports during discovery; no production initialization/apply.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import hmac
import json
import os
import re
import sqlite3
import stat
import uuid


class LegacyAuditError(RuntimeError):
    """Controlled discovery/review denial without customer or filesystem details."""


SOURCES={'TASK':('tasks','id_phan_cong',('file_giao_viec','file_bao_cao')),
         'DOCUMENT':('documents','ma_tl',('link_file',)),
         'PERSONAL':('personal_tasks','id',('file_dinh_kem',))}
SUPPORTED={('TASK','file_giao_viec'),('TASK','file_bao_cao'),('DOCUMENT','link_file')}
CLASSES=('VERIFIED_CANDIDATE','AMBIGUOUS','CONFLICT','CROSS_TENANT_CONFLICT','ORPHAN',
         'MISSING_PHYSICAL','MISSING_OBJECT','INVALID_PATH','EXTERNAL_REFERENCE',
         'PUBLIC_NON_UPLOAD','ALREADY_REGISTERED','UNKNOWN')


def canonical_json(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True)


def digest(value):
    return hashlib.sha256(canonical_json(value).encode()).hexdigest()


def basename(name):
    return bool(isinstance(name,str) and name and name not in ('.','..') and name==name.strip()
                and not name.endswith('.') and not any(c in name for c in '/\\:%?#')
                and not any(ord(c)<32 or ord(c)==127 for c in name))


def normalize_reference(value):
    """Only literal gateway/binding-compatible persisted URLs qualify.

    Query/fragment/encoded aliases cannot prove exact live persisted-field match.
    Absolute URLs (even same-origin) were not supported by binding flow, so remain
    external references. Public lookalikes/query text never identify local blobs.
    """
    if not isinstance(value,str) or value!=value.strip() or any(ord(c)<32 or ord(c)==127 for c in value):
        return 'INVALID_PATH',None
    try:
        parsed=urlsplit(value)
    except ValueError:
        return 'INVALID_PATH',None
    if re.match(r'^[A-Za-z]:',value) or '\\' in value:
        return 'INVALID_PATH',None
    if parsed.scheme or parsed.netloc:
        return 'EXTERNAL_REFERENCE',None
    prefix='/static/uploads/'
    if value.startswith(prefix):
        name=value[len(prefix):]
        if parsed.query or parsed.fragment or not basename(name):
            return 'INVALID_PATH',None
        return 'LOCAL_UPLOAD',name
    # Alias detection affects denial/classification only, never normalization into
    # an accepted binding. No raw substring matching of query strings.
    parts=[p for p in parsed.path.lower().split('/') if p and p!='.']
    if '%' in parsed.path or (parts[:2]==['static','uploads']):
        return 'INVALID_PATH',None
    return 'PUBLIC_NON_UPLOAD',None


def fingerprint(path):
    path=Path(path)
    before=path.stat()
    value={'size':before.st_size,'mtime_ns':before.st_mtime_ns,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise LegacyAuditError('Inventory source changed')
    return value


@contextmanager
def readonly_database(path):
    """Immutable read avoids journal/SHM writes; refuse active WAL/journal sources.

    Administrator must provide quiescent files; changing sources fail closed.
    No fallback to writable connections, DB creation, startup or migration.
    """
    path=Path(path).absolute()
    if path.resolve()!=path or not path.is_file():
        raise LegacyAuditError('Read-only inventory source unavailable')
    for suffix in ('-wal','-journal'):
        side=Path(str(path)+suffix)
        if side.exists() and side.stat().st_size:
            raise LegacyAuditError('Active database journal; inventory unavailable')
    before=fingerprint(path)
    conn=None
    try:
        conn=sqlite3.connect(path.as_uri()+'?mode=ro&immutable=1',uri=True,timeout=.3,isolation_level=None)
        conn.row_factory=sqlite3.Row
        conn.execute('PRAGMA query_only=ON')
        conn.execute('PRAGMA busy_timeout=300')
        conn.execute('BEGIN')
        yield conn
    except sqlite3.Error as exc:
        raise LegacyAuditError('Read-only inventory database invalid') from exc
    finally:
        if conn:
            conn.rollback();conn.close()
    if fingerprint(path)!=before:
        raise LegacyAuditError('Inventory source changed')


def physical_metadata(root,name):
    root=Path(root).absolute()
    if root.resolve()!=root or not root.is_dir() or not basename(name):
        return {'exists':False,'valid':False,'reason':'INVALID_PATH'}
    path=root/name
    if not path.exists() and not path.is_symlink():
        return {'exists':False,'valid':True,'canonical_path':str(path)}
    try:
        before=path.lstat()
        if (path.resolve()!=path or path.resolve().parent!=root or not stat.S_ISREG(before.st_mode)
                or getattr(before,'st_file_attributes',0)&0x400):
            return {'exists':True,'valid':False,'reason':'INVALID_PATH'}
        fd=os.open(path,os.O_RDONLY|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0))
        with os.fdopen(fd,'rb') as stream:
            opened=os.fstat(stream.fileno())
            if (opened.st_dev,opened.st_ino)!=(before.st_dev,before.st_ino):
                raise LegacyAuditError('Physical identity changed')
            sha=hashlib.sha256()
            for chunk in iter(lambda:stream.read(1024*1024),b''):sha.update(chunk)
            after=os.fstat(stream.fileno())
        if ((opened.st_size,opened.st_mtime_ns)!=(after.st_size,after.st_mtime_ns)
                or path.resolve()!=path or path.lstat().st_ino!=opened.st_ino):
            raise LegacyAuditError('Physical identity changed')
        return {'exists':True,'valid':True,'canonical_path':str(path),'size':after.st_size,
                'sha256':sha.hexdigest(),'mtime_ns':after.st_mtime_ns,'physical_identity':[after.st_dev,after.st_ino]}
    except OSError as exc:
        raise LegacyAuditError('Physical inventory unavailable') from exc


class LegacyDiscovery:
    def __init__(self, upload_root, tenant_databases, registry_path=None):
        self.root=Path(upload_root).absolute()
        if self.root.resolve()!=self.root or not self.root.is_dir() or not isinstance(tenant_databases,dict) or not tenant_databases:
            raise LegacyAuditError('Invalid inventory scope')
        self.databases={str(k):Path(v).absolute() for k,v in sorted(tenant_databases.items())}
        if any(not k.strip() for k in self.databases) or len(set(self.databases.values()))!=len(self.databases):
            raise LegacyAuditError('Ambiguous tenant source')
        self.registry=Path(registry_path).absolute() if registry_path else None

    def validate_complete_scope(self, master_path):
        """Reviewed apply requires every registered/current tenant source.

        Use current resolver's path convention without importing its startup
        module. Partial discovery may inform review, never authorize apply.
        Unknown/unregistered DB sources require review rather than omission.
        """
        master=Path(master_path).absolute()
        expected={}
        with readonly_database(master) as conn:
            for row in conn.execute('SELECT tax_code FROM master_companies ORDER BY tax_code'):
                tenant=str(row[0]).strip()
                if not re.fullmatch(r'[0-9]+',tenant) or tenant in expected:
                    raise LegacyAuditError('Ambiguous authoritative tenant inventory')
                expected[tenant]=(master.parent.parent/'qlcv.db' if tenant=='0312345678'
                                  else master.parent/'tenants'/(tenant+'.db'))
        actual=set((master.parent/'tenants').glob('*.db'))|{master.parent.parent/'qlcv.db'}
        if self.databases!=expected or actual!=set(expected.values()) or not all(p.is_file() for p in expected.values()):
            raise LegacyAuditError('Complete authoritative tenant inventory required')

    def _references(self):
        refs=[]; objects={}; classes=[]
        for tenant,path in self.databases.items():
            objects[tenant]={}
            with readonly_database(path) as conn:
                tables={r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                for kind,(table,key,fields) in SOURCES.items():
                    if table not in tables:
                        classes.append({'tenant':tenant,'kind':kind,'status':'TABLE_ABSENT'});continue
                    columns={r[1] for r in conn.execute('PRAGMA table_info('+table+')')}
                    if key not in columns or not all(f in columns for f in fields):
                        raise LegacyAuditError('Unsupported reference schema')
                    classes.append({'tenant':tenant,'kind':kind,'status':'INVENTORIED'})
                    for row in conn.execute('SELECT '+','.join([key,*fields])+' FROM '+table+' ORDER BY '+key):
                        oid=str(row[key]); objects[tenant][(kind,oid)]={field:row[field] or '' for field in fields}
                        for field in fields:
                            if not row[field]:continue
                            classification,name=normalize_reference(row[field])
                            refs.append({'tenant_id':tenant,'object_kind':kind,'object_id':oid,'field_slot':field,
                                         'stored_reference':row[field],'normalization':classification,'storage_name':name,
                                         'object_exists':True,'supported':(kind,field) in SUPPORTED})
        return sorted(refs,key=canonical_json),objects,classes

    def _registry(self, connection=None, own_file_id=None):
        if self.registry is None or not self.registry.exists():return [],[],'ABSENT'
        def read(conn):
            version=conn.execute('PRAGMA user_version').fetchone()[0]
            if version not in (2,3):raise LegacyAuditError('Registry version unavailable for inventory')
            required={'file_id','tenant_id','storage_root_id','storage_name','size','sha256','classification','state','uploader_id'}
            if not required.issubset({r[1] for r in conn.execute('PRAGMA table_info(files)')}):
                raise LegacyAuditError('Registry inventory schema invalid')
            from services.file_registry import FileRegistry
            expected=FileRegistry.FILE_COLUMNS if version==3 else FileRegistry.FILE_COLUMNS[:-4]
            if [r[1] for r in conn.execute('PRAGMA table_info(files)')]!=expected or [r[1] for r in conn.execute('PRAGMA table_info(bindings)')]!=FileRegistry.BINDING_COLUMNS:
                raise LegacyAuditError('Registry inventory schema invalid')
            files=[dict(r) for r in conn.execute('SELECT * FROM files ORDER BY storage_root_id,storage_name') if r['file_id']!=own_file_id]
            bindings=[dict(r) for r in conn.execute('SELECT * FROM bindings ORDER BY binding_id') if r['file_id']!=own_file_id]
            for row in files:
                if version==2:row.update(provenance_type='VERIFIED_UPLOADER',review_id=None,reviewed_by=None,review_evidence=None)
                row['valid_provenance']=FileRegistry.valid_provenance(row)
            return files,bindings,'SCHEMA_'+str(version)
        if connection is not None:
            if not connection.in_transaction:raise LegacyAuditError('Serialized registry transaction required')
            return read(connection)
        with readonly_database(self.registry) as conn:return read(conn)

    def discover(self, *, registry_connection=None, own_file_id=None):
        source_before={k:fingerprint(p) for k,p in self.databases.items()}
        refs,objects,source_classes=self._references()
        files,bindings,registry_status=self._registry(registry_connection,own_file_id)
        file_by_name={}
        for f in files:
            if f['storage_root_id']=='LOCAL_UPLOADS':
                if f['storage_name'] in file_by_name:raise LegacyAuditError('Duplicate registry locator')
                file_by_name[f['storage_name']]=f
        physical_names=sorted(p.name for p in self.root.iterdir() if p.name!='.gitkeep')
        names=sorted(set(physical_names)|{r['storage_name'] for r in refs if r['storage_name']}|set(file_by_name))
        physical_by_name={n:physical_metadata(self.root,n) for n in names}
        aliases={}
        for name,meta in physical_by_name.items():
            if meta.get('valid') and meta.get('exists'):
                aliases.setdefault(tuple(meta['physical_identity']),[]).append(name)
        candidates=[]
        for name in names:
            references=[r for r in refs if r['storage_name']==name]
            tenants=sorted({r['tenant_id'] for r in references})
            physical=physical_by_name[name]
            alias_names=aliases.get(tuple(physical.get('physical_identity',[])),[name])
            alias_tenants=sorted({r['tenant_id'] for r in refs if r['storage_name'] in alias_names})
            registered=file_by_name.get(name)
            rb=[] if not registered else [b for b in bindings if b['file_id']==registered['file_id']]
            missing=[]
            for b in rb:
                if b['state']=='ACTIVE' and (b['object_kind'],str(b['object_id'])) not in objects.get(b['tenant_id'],{}):
                    missing.append({'object_kind':b['object_kind'],'object_id':b['object_id'],'tenant_id':b['tenant_id']})
            issues=[]; eligible=False
            if not physical['valid']:classification='INVALID_PATH'
            elif len(alias_tenants)>1:classification='CROSS_TENANT_CONFLICT';issues=['CROSS_TENANT_REFERENCES_OR_PHYSICAL_ALIASES']
            elif len(alias_names)>1:classification='AMBIGUOUS';issues=['MULTIPLE_NAMES_SAME_PHYSICAL_IDENTITY']
            elif registered:
                compatible=(physical['exists'] and registered['size']==physical.get('size') and registered['sha256']==physical.get('sha256')
                            and (not tenants or tenants==[registered['tenant_id']]))
                if not compatible or not registered['valid_provenance']:classification='CONFLICT';issues=['REGISTRY_IDENTITY_MISMATCH']
                elif missing:classification='MISSING_OBJECT';issues=['ACTIVE_BINDING_MISSING_OBJECT']
                elif registered['classification']=='UNKNOWN' or registered['state'] in ('WRITING','REVOKED'):
                    classification='UNKNOWN';issues=['REGISTRY_NOT_ELIGIBLE']
                else:classification='ALREADY_REGISTERED'
            elif not physical['exists']:classification='MISSING_PHYSICAL'
            elif not references:classification='ORPHAN'
            elif not all(r['supported'] for r in references):classification='UNKNOWN';issues=['UNSUPPORTED_PERSONAL_ACL']
            else:
                classification='UNKNOWN';eligible=True
                issues=['REFERENCE_ONLY_REQUIRES_INDEPENDENT_CUSTODIAN_EVIDENCE']
            slots=[{'object_kind':r['object_kind'],'object_id':r['object_id'],'field_slot':r['field_slot']} for r in references if r['supported']]
            candidate={'candidate_id':digest({'root':str(self.root),'storage_name':name}),
                       'classification':classification,'storage_name':name,'physical':physical,
                       'reference_count':len(references),'tenant_candidate':tenants[0] if len(tenants)==1 else None,
                       'tenant_sources':{t:str(self.databases[t]) for t in tenants},
                       'inventory_scope':{t:str(p) for t,p in self.databases.items()},
                       'tenants':tenants,'object_bindings':sorted(slots,key=canonical_json),'references':references,
                       'physical_aliases':alias_names,
                       'existing_registry':registered,'existing_bindings':rb,'missing_objects':missing,
                       'conflicts':issues if classification in ('CONFLICT','CROSS_TENANT_CONFLICT') else [],
                       'ambiguity_reasons':issues,'eligible_for_review':eligible,'approval_status':'UNAPPROVED','review_id':None}
            candidate['evidence_digest']=digest(candidate)
            candidates.append(candidate)
        excluded=[r for r in refs if r['normalization']!='LOCAL_UPLOAD']
        counts={c:sum(x['classification']==c for x in candidates) for c in CLASSES}
        for c in ('INVALID_PATH','EXTERNAL_REFERENCE','PUBLIC_NON_UPLOAD'):
            counts[c]+=sum(r['normalization']==c for r in excluded)
        physical_records=[physical_by_name[n] for n in physical_names]
        aggregates={'physical_upload_files':sum(p['exists'] and p['valid'] for p in physical_records),
                    'local_references':sum(r['normalization']=='LOCAL_UPLOAD' for r in refs),
                    'unique_normalized_references':len({r['storage_name'] for r in refs if r['storage_name']}),
                    'classification_counts':counts,'structurally_reviewable':sum(c['eligible_for_review'] for c in candidates)}
        if {k:fingerprint(p) for k,p in self.databases.items()}!=source_before:
            raise LegacyAuditError('Inventory source changed')
        if {n:physical_metadata(self.root,n) for n in names}!=physical_by_name:
            raise LegacyAuditError('Physical inventory changed')
        return {'format_version':1,'upload_root':str(self.root),'tenant_sources':{k:str(p) for k,p in self.databases.items()},
                'source_fingerprints':source_before,'registry_status':registry_status,'reference_classes':source_classes,
                'candidates':candidates,'excluded_references':excluded,'aggregates':aggregates,
                'trust_rule':'REFERENCE != OWNERSHIP; no uploader inference; approval required'}


@dataclass(frozen=True)
class CustodianAuthority:
    """Trusted offline principal/key; never constructed from browser/client input.

    Deployment authentication/key custody remains an administrative responsibility.
    Tests use ephemeral synthetic keys; no production key or approval is generated.
    """
    custodian_id: str
    signing_key: bytes

    def __post_init__(self):
        if (not isinstance(self.custodian_id,str) or not self.custodian_id.strip()
                or any(ord(c)<32 for c in self.custodian_id) or not isinstance(self.signing_key,bytes) or len(self.signing_key)<32):
            raise LegacyAuditError('Invalid offline custodian authority')


def approve_candidate(candidate, authority, independent_evidence):
    if type(authority) is not CustodianAuthority or not candidate.get('eligible_for_review') or candidate['classification']!='UNKNOWN':
        raise LegacyAuditError('Candidate not eligible for custodian review')
    clean={k:v for k,v in candidate.items() if k!='evidence_digest'}
    if candidate.get('evidence_digest')!=digest(clean):raise LegacyAuditError('Candidate evidence digest invalid')
    if (not isinstance(independent_evidence,dict)
            or independent_evidence.get('tenant_id')!=candidate['tenant_candidate']
            or independent_evidence.get('sha256')!=candidate['physical']['sha256']
            or independent_evidence.get('source_kind') not in ('CUSTODIAN_ATTESTATION','BACKUP_RECORD','IMMUTABLE_UPLOAD_RECORD')
            or not all(isinstance(independent_evidence.get(k),str) and independent_evidence[k].strip() for k in ('source_id','statement'))):
        raise LegacyAuditError('Independent provenance evidence required')
    approval={'candidate_id':candidate['candidate_id'],'candidate_digest':candidate['evidence_digest'],
              'decision':'APPROVED','reviewed_classification':'VERIFIED_CANDIDATE','review_id':str(uuid.uuid4()),
              'custodian_id':authority.custodian_id,'independent_evidence':independent_evidence}
    approval['signature']=hmac.new(authority.signing_key,canonical_json(approval).encode(),hashlib.sha256).hexdigest()
    return approval


def apply_synthetic(discovery, candidate, approval, authority, sandbox_root):
    """Production activation intentionally impossible through this entry point.

    Only a copied guarded app under project/.test_runtime/run-* may apply. All DB,
    upload and sidecar paths must be in that exact run. No normal caller/HTTP hook.
    """
    sandbox=Path(sandbox_root).absolute()
    module=Path(__file__).resolve()
    if (module.parents[1]!=sandbox/'app' or sandbox.parent.name!='.test_runtime'
            or not sandbox.name.startswith('run-') or sandbox.resolve()!=sandbox):
        raise LegacyAuditError('Synthetic apply only; production activation forbidden')
    if type(authority) is not CustodianAuthority or not isinstance(approval,dict):
        raise LegacyAuditError('Authenticated offline custodian approval required')
    unsigned={k:v for k,v in approval.items() if k!='signature'}
    expected=hmac.new(authority.signing_key,canonical_json(unsigned).encode(),hashlib.sha256).hexdigest()
    if (not isinstance(approval.get('signature'),str) or not hmac.compare_digest(expected,approval['signature'])
            or approval.get('decision')!='APPROVED' or approval.get('custodian_id')!=authority.custodian_id
            or approval.get('candidate_id')!=candidate.get('candidate_id')
            or approval.get('candidate_digest')!=candidate.get('evidence_digest')):
        raise LegacyAuditError('Approval signature/evidence mismatch')
    from config import Config
    from services.file_registry import FileRegistry
    from services.legacy_provenance import approve_mapping,register_verified_legacy
    paths=[discovery.root,*discovery.databases.values(),discovery.registry,Path(Config.UPLOAD_DIR).absolute(),Config.FILE_REGISTRY_PATH]
    if any(p is None or not Path(p).resolve().is_relative_to(sandbox) for p in paths) or discovery.root!=Path(Config.UPLOAD_DIR).absolute() or discovery.registry!=Config.FILE_REGISTRY_PATH:
        raise LegacyAuditError('Synthetic apply path confinement failed')
    def current(connection=None,own_file_id=None):
        discovery.validate_complete_scope(sandbox/'app/database/master_system.db')
        artifact=discovery.discover(registry_connection=connection,own_file_id=own_file_id)
        row=next((c for c in artifact['candidates'] if c['candidate_id']==candidate['candidate_id']),None)
        if row is None or not row['eligible_for_review'] or row['evidence_digest']!=approval['candidate_digest']:
            raise LegacyAuditError('STALE_REVIEW')
        return row
    live=current()
    evidence=approval.get('independent_evidence',{})
    if (evidence.get('tenant_id')!=live['tenant_candidate'] or evidence.get('sha256')!=live['physical']['sha256']
            or approval.get('reviewed_classification')!='VERIFIED_CANDIDATE'):
        raise LegacyAuditError('Approved provenance mismatch')
    mapping={'tenant_id':live['tenant_candidate'],'storage_name':live['storage_name'],'size':live['physical']['size'],
             'sha256':live['physical']['sha256'],'bindings':live['object_bindings']}
    permit=approve_mapping(mapping,{'decision':'APPROVED','mapping_digest':digest(mapping),
            'review_id':approval['review_id'],'reviewer':authority.custodian_id,'evidence':canonical_json(unsigned)})
    def revalidate(_mapping):
        current();return True
    def serialized_revalidation(_mapping,connection,own_file_id):
        current(connection,own_file_id);return True
    return register_verified_legacy(FileRegistry(),permit,revalidate,revalidate_in_transaction=serialized_revalidation)


def main():
    """Read-only command. No apply/approve-all option exists."""
    import argparse
    parser=argparse.ArgumentParser(description='Read-only legacy inventory; NEVER production apply')
    parser.add_argument('--upload-root',required=True)
    parser.add_argument('--tenant',action='append',required=True,help='trusted explicit TENANT=DATABASE manifest entry')
    parser.add_argument('--registry')
    parser.add_argument('--output',help='explicit private review artifact path; exclusive create')
    args=parser.parse_args()
    manifest={}
    for entry in args.tenant:
        tenant,sep,path=entry.partition('=')
        if not sep or tenant in manifest:parser.error('Invalid tenant manifest')
        manifest[tenant]=path
    artifact=LegacyDiscovery(args.upload_root,manifest,args.registry).discover()
    if args.output:
        output=Path(args.output).absolute()
        if output.resolve()!=output or output.is_relative_to(Path(args.upload_root).absolute()) or 'static' in output.parts:
            raise LegacyAuditError('Review artifact must remain private')
        with output.open('x',encoding='utf-8') as stream:stream.write(json.dumps(artifact,sort_keys=True,indent=2))
    print(json.dumps(artifact['aggregates'],sort_keys=True))


if __name__=='__main__':main()

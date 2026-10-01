"""Offline reviewed legacy primitive, NOT imported by any HTTP/upload route.

Only trusted administrative tooling may call this module. Python code with DB
write access is already inside the trust boundary; a form/role is not a permit.
This is infrastructure, not discovery, approval UI or production rollout.
"""
from dataclasses import dataclass
import hashlib
import json
import re
import uuid
from services.file_registry import FileRegistry, RegistryError, _text, _now
from services.file_access_service import physical_bytes, storage_basename
from config import Config


def mapping_digest(mapping):
    return hashlib.sha256(json.dumps(mapping,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


@dataclass(frozen=True)
class _ReviewedMapping:
    payload: str
    review_id: str
    reviewer: str
    evidence: str


def approve_mapping(mapping, approval):
    """Offline custodian input only; never infer approval from references/roles.

    Future tooling must authenticate the custodian and establish independent
    tenant/provenance evidence before constructing this explicit approval.
    No approve-all, API mode flag or uploader surrogate is accepted here.
    """
    digest=mapping_digest(mapping)
    if (not isinstance(approval,dict) or approval.get('decision')!='APPROVED'
            or approval.get('mapping_digest')!=digest
            or not isinstance(approval.get('evidence'),str) or not approval['evidence'].strip()):
        raise RegistryError('Explicit reviewed mapping required')
    return _ReviewedMapping(json.dumps(mapping,sort_keys=True),_text(approval.get('review_id')),
                            _text(approval.get('reviewer')),hashlib.sha256(approval['evidence'].encode()).hexdigest())


def register_verified_legacy(registry, reviewed, revalidate, *, revalidate_in_transaction=None):
    """One short SQLite transaction: file identity + all exact ACTIVE bindings.

    revalidate is a TRUSTED offline callback reloading exact tenant/object/field
    and checking the full reviewed reference/conflict inventory; no HTTP caller.
    Gateway still revalidates live ACL/field on every read. No uploader fallback.
    Any exception rolls back all metadata; physical bytes are never modified.
    """
    if type(reviewed) is not _ReviewedMapping or not callable(revalidate) or (revalidate_in_transaction is not None and not callable(revalidate_in_transaction)):
        raise RegistryError('Dedicated reviewed legacy authority required')
    mapping=json.loads(reviewed.payload)
    if set(mapping)!={'tenant_id','storage_name','size','sha256','bindings'}:
        raise RegistryError('Invalid reviewed mapping fields')
    tenant=_text(mapping['tenant_id'])
    name=mapping['storage_name']
    size=mapping['size']; digest=mapping['sha256']; bindings=mapping['bindings']
    if (not storage_basename(name) or isinstance(size,bool) or not isinstance(size,int) or size<0
            or not isinstance(digest,str) or not re.fullmatch('[0-9a-f]{64}',digest)
            or not isinstance(bindings,list) or not bindings):
        raise RegistryError('Invalid legacy mapping')
    slots=[]
    for b in bindings:
        if not isinstance(b,dict) or set(b)!={'object_kind','object_id','field_slot'}:
            raise RegistryError('Invalid reviewed binding')
        kind=b['object_kind']; slot=b['field_slot']; oid=_text(b['object_id'])
        if not ((kind=='TASK' and slot in ('file_giao_viec','file_bao_cao')) or
                (kind=='DOCUMENT' and slot=='link_file')):
            raise RegistryError('Unsupported legacy binding')
        key=(kind,oid,slot)
        if key in slots:
            raise RegistryError('Duplicate reviewed binding')
        slots.append(key)
    physical_bytes({'storage_name':name,'size':size,'sha256':digest})
    file_id=str(uuid.uuid4()); now=_now()
    with registry._connection(mutation=True) as conn:
        # Reviewed discovery can inspect this serialized registry transaction
        # without opening its own immutable reader over an active journal.
        validate=lambda: (revalidate_in_transaction(mapping,conn,file_id)
                          if revalidate_in_transaction is not None else revalidate(mapping))
        if validate() is not True:
            raise RegistryError('Stale reviewed mapping')
        if conn.execute('SELECT 1 FROM files WHERE storage_root_id=? AND storage_name=?',
                        (Config.UPLOAD_STORAGE_ROOT_ID,name)).fetchone():
            raise RegistryError('Existing registry identity conflict')
        conn.execute('INSERT INTO files VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (file_id,tenant,None,Config.UPLOAD_STORAGE_ROOT_ID,name,name,now,size,digest,
             'VERIFIED_LEGACY','BOUND',None,1,'LEGACY_VERIFIED_MAPPING',reviewed.review_id,
             reviewed.reviewer,reviewed.evidence))
        for kind,oid,slot in slots:
            if conn.execute("SELECT 1 FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=? AND state IN ('ACTIVE','PENDING')",
                            (tenant,kind,oid,slot)).fetchone():
                raise RegistryError('Legacy binding slot conflict')
            generation=conn.execute('SELECT COALESCE(MAX(generation),0)+1 FROM bindings WHERE tenant_id=? AND object_kind=? AND object_id=? AND field_slot=?',
                                    (tenant,kind,oid,slot)).fetchone()[0]
            conn.execute('INSERT INTO bindings VALUES (?,?,?,?,?,?,?,?,?,?)',
                         (str(uuid.uuid4()),file_id,tenant,kind,oid,slot,generation,'ACTIVE',now,now))
        # Fail closed if exact object references changed during apply callback.
        if validate() is not True:
            raise RegistryError('Post-apply revalidation failed')
        physical_bytes({'storage_name':name,'size':size,'sha256':digest})
    return file_id

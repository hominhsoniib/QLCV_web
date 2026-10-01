"""Authorized-callers-only binding coordinator; no object ACL or file serving.

Sidecar and business commits remain separate. SQLite serializes the slot while
the business callback commits and the exact persisted field is reloaded.
"""
from pathlib import Path
from urllib.parse import urlsplit, unquote
from sqlalchemy import select
from config import Config
from services.file_registry import FileRegistry, RegistryError, _now


class FileBindingService:
    def __init__(self, db, tenant_id, actor_id):
        if not isinstance(tenant_id,str) or not tenant_id or not isinstance(actor_id,str) or not actor_id:
            raise RegistryError('Invalid binding identity')
        self.db, self.tenant, self.actor = db, tenant_id, actor_id
        self.registry=FileRegistry()

    @staticmethod
    def local_name(url):
        if not isinstance(url,str):
            raise RegistryError('Invalid attachment reference')
        try:
            parsed=urlsplit(url)
        except ValueError as exc:
            raise RegistryError('Invalid attachment reference') from exc
        if parsed.scheme or parsed.netloc:
            alias=unquote(unquote(parsed.path)).replace('\\','/').lower()
            if '/static/uploads' in alias:
                raise RegistryError('Absolute local upload alias denied')
            return None
        if not url.startswith('/static/uploads/'):
            if 'uploads' in url.lower() and ('static' in url.lower() or '%' in url or '\\' in url):
                raise RegistryError('Invalid local upload alias')
            return None
        name=url[len('/static/uploads/'):]
        if not name or name in ('.','..') or any(c in name for c in '/\\:%?#') or any(ord(c)<32 for c in name) or name!=name.strip() or name.endswith('.'):
            raise RegistryError('Invalid local upload locator')
        return name

    def reload(self, model, object_id):
        self.db.expire_all()
        return self.db.execute(select(model).where(list(model.__table__.primary_key.columns)[0]==object_id).execution_options(populate_existing=True)).scalar_one_or_none()

    def run(self, model, kind, object_id, field, url, old_url, mutate, *, inherited_from=None):
        name=self.local_name(url)
        record=None
        slot=(self.tenant,kind,str(object_id),field)
        if name:
            if self.registry.path.exists():
                record=self.registry.get_storage_record(Config.UPLOAD_STORAGE_ROOT_ID,name)
            if record is None:
                # Compatibility only for an unchanged/inherited legacy reference.
                if url!=old_url:
                    raise RegistryError('Unregistered local upload')
            else:
                if not self.registry.valid_provenance(record) or record['tenant_id']!=self.tenant or record['classification']=='UNKNOWN' or record['state'] not in ('UNBOUND','BOUND') or self.registry.expired_unbound(record):
                    raise RegistryError('File not eligible for binding')
                active=self.registry.list_active_bindings(record['file_id'],self.tenant)
                own_slot=url==old_url and any(b['object_kind']==kind and b['object_id']==str(object_id) and b['field_slot']==field for b in active)
                shared=False
                if inherited_from:
                    parent_model,parent_id,parent_field=inherited_from
                    parent=self.reload(parent_model,parent_id)
                    shared=bool(parent and getattr(parent,parent_field)==url and any(
                        b['object_kind']=='TASK' and b['object_id']==str(parent_id) and b['field_slot']==parent_field for b in active))
                if record['state']=='UNBOUND' and record['uploader_id']!=self.actor:
                    raise RegistryError('UNBOUND uploader mismatch')
                if record['state']=='BOUND' and record['uploader_id']!=self.actor and not own_slot and not shared:
                    raise RegistryError('No vetted binding authority')
                physical=(Path(Config.UPLOAD_DIR).resolve()/record['storage_name']).resolve()
                if physical.parent!=Path(Config.UPLOAD_DIR).resolve() or not physical.is_file():
                    raise RegistryError('Physical locator unavailable')

        pending=None
        try:
            if record:
                pending=self.registry.create_pending_binding(record['file_id'],*slot,replacement=True)
                receipt=self.registry.get_binding(pending,self.tenant)
            # Even clear/external/legacy mutations serialize against registry slots
            # when sidecar exists. No sidecar creation for legacy or external links.
            if self.registry.path.exists():
                with self.registry._connection(mutation=True) as conn:
                    live=self.registry.slot_bindings(*slot,connection=conn)
                    if any(b['state']=='PENDING' and b['binding_id']!=pending for b in live):
                        raise RegistryError('Another replacement is reserved')
                    result=mutate()
                    if not result.get('success'):
                        raise RegistryError('Business mutation failed')
                    persisted=self.reload(model,object_id)
                    if persisted is None or (getattr(persisted,field) or '')!=url:
                        raise RegistryError('Post-commit binding revalidation failed')
                    if pending:
                        self.registry.activate_binding(pending,self.tenant,expected_generation=receipt['generation'],connection=conn)
                    else:
                        for binding in live:
                            if binding['state']=='ACTIVE':
                                conn.execute("UPDATE bindings SET state='REVOKED',updated_at=? WHERE binding_id=?",(_now(),binding['binding_id']))
                    return result
            result=mutate()
            if not result.get('success'):
                raise RegistryError('Business mutation failed')
            return result
        except Exception as exc:
            self.db.rollback()
            if pending:
                try:
                    self.registry.revoke_pending(pending,self.tenant)
                except RegistryError:
                    pass  # Stale PENDING is not authority; reconciliation required.
            if isinstance(exc,RegistryError):
                raise
            raise RegistryError('Business binding operation failed') from exc

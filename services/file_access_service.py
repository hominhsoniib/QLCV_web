"""Private local read gateway. No writes, ownership claims or ACL duplication."""
from pathlib import Path
from datetime import datetime, timezone
from email.utils import formatdate, parsedate_to_datetime
from urllib.parse import quote
import hashlib
import mimetypes
import os
import re
import stat
from fastapi.responses import Response, JSONResponse
from config import Config
from services.auth_service import AuthService
from services.file_registry import FileRegistry, RegistryError
from services import task_policy
from models.models import Task, Document
from sqlalchemy.exc import SQLAlchemyError


HEADERS={'Cache-Control':'private, no-store','Pragma':'no-cache','Expires':'0',
         'X-Content-Type-Options':'nosniff','X-QLCV-File-Gateway':'1'}


def denied(status=404):
    return JSONResponse({'success':False,'message':'Authentication required' if status==401 else 'Not found'},
                        status_code=status,headers=HEADERS)


def storage_basename(name):
    return bool(isinstance(name,str) and name and name not in ('.','..') and
                name==name.strip() and not name.endswith('.') and
                not any(c in name for c in '/\\:%?#') and
                not any(ord(c)<32 or ord(c)==127 for c in name))


def handle_realpath(fd, fallback):
    """Verify the opened handle, not only the pre-open lexical pathname."""
    if os.name=='nt':
        import ctypes
        import msvcrt
        from ctypes import wintypes
        function=ctypes.WinDLL('kernel32',use_last_error=True).GetFinalPathNameByHandleW
        function.argtypes=[wintypes.HANDLE,wintypes.LPWSTR,wintypes.DWORD,wintypes.DWORD]
        function.restype=wintypes.DWORD
        buffer=ctypes.create_unicode_buffer(32768)
        length=function(msvcrt.get_osfhandle(fd),buffer,len(buffer),0)
        if not length or length>=len(buffer):
            raise RegistryError('Invalid physical handle')
        name=buffer.value
        if name.startswith('\\\\?\\UNC\\'):
            name='\\\\'+name[8:]
        elif name.startswith('\\\\?\\'):
            name=name[4:]
        return Path(name).resolve()
    descriptor=Path('/proc/self/fd')/str(fd)
    if descriptor.exists():
        return descriptor.resolve()
    # Fail closed where opened-handle confinement cannot be verified.
    raise RegistryError('Physical handle verification unavailable')


def physical_bytes(row):
    root=Path(Config.UPLOAD_DIR).absolute()
    if root.resolve()!=root or not storage_basename(row['storage_name']):
        raise RegistryError('Invalid physical root')
    path=root/row['storage_name']
    if path.resolve()!=path or path.resolve().parent!=root:
        raise RegistryError('Physical escape')
    before=path.lstat()
    if not stat.S_ISREG(before.st_mode) or getattr(before,'st_file_attributes',0)&0x400:
        raise RegistryError('Invalid physical type')
    fd=os.open(path,os.O_RDONLY|getattr(os,'O_BINARY',0)|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as stream:
        if handle_realpath(stream.fileno(),path)!=path:
            raise RegistryError('Physical handle escape')
        opened=os.fstat(stream.fileno())
        if not stat.S_ISREG(opened.st_mode) or opened.st_size!=row['size']:
            raise RegistryError('Physical size mismatch')
        content=stream.read()
        after=os.fstat(stream.fileno())
        if (len(content)!=row['size'] or hashlib.sha256(content).hexdigest()!=row['sha256']
                or (opened.st_size,opened.st_mtime_ns)!=(after.st_size,after.st_mtime_ns)):
            raise RegistryError('Physical identity mismatch')
        return content,opened.st_mtime


def file_response(request,row,content,modified):
    # Authorization AND complete hash verification already succeeded.
    headers=dict(HEADERS)
    headers.update({'ETag':'"'+row['sha256']+'"','Last-Modified':formatdate(modified,usegmt=True),
                    'Accept-Ranges':'bytes'})
    name=''.join(c for c in row['original_name'] if ord(c)>=32 and ord(c)!=127)
    name=name.replace('\\','/').rsplit('/',1)[-1] or 'download'
    inferred=mimetypes.guess_type(row['storage_name'])[0] or 'application/octet-stream'
    safe_inline=inferred in ('application/pdf','image/png','image/jpeg','image/gif','image/webp','text/plain')
    disposition='inline' if safe_inline and request.query_params.get('download')!='1' else 'attachment'
    headers['Content-Disposition']=disposition+"; filename*=UTF-8''"+quote(name,safe='')
    mime=inferred if safe_inline else 'application/octet-stream'
    inm=request.headers.get('if-none-match')
    if inm and (inm=='*' or headers['ETag'] in [t.strip().removeprefix('W/') for t in inm.split(',')]):
        return Response(status_code=304,headers=headers)
    if not inm and request.headers.get('if-modified-since'):
        try:
            if int(modified)<=parsedate_to_datetime(request.headers['if-modified-since']).timestamp():
                return Response(status_code=304,headers=headers)
        except (ValueError,TypeError,OverflowError):
            pass
    status=200
    body=content
    range_header=request.headers.get('range')
    if_range=request.headers.get('if-range')
    if if_range and if_range!=headers['ETag']:
        try:
            use_range=int(modified)<=parsedate_to_datetime(if_range).timestamp()
        except (ValueError,TypeError,OverflowError):
            use_range=False
        if not use_range:
            range_header=None
    if range_header:
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',range_header)
        size=len(content)
        try:
            if not match or not size or not any(match.groups()):
                raise ValueError()
            a,b=match.groups()
            start=int(a) if a else max(0,size-int(b))
            end=min(int(b),size-1) if a and b else size-1
            if start>=size or start>end or (not a and int(b)==0):
                raise ValueError()
        except ValueError:
            headers['Content-Range']='bytes */'+str(size)
            return Response(status_code=416,headers=headers)
        body=content[start:end+1]
        status=206
        headers['Content-Range']=f'bytes {start}-{end}/{size}'
    headers['Content-Length']=str(len(body))
    return Response(content=b'' if request.method=='HEAD' else body,status_code=status,
                    media_type=mime,headers=headers)


def gateway(request, storage_name, db):
    try:
        raw=request.scope.get('raw_path',b'').decode('ascii')
        canonical='/static/uploads/'+storage_name
        if not storage_basename(storage_name) or raw!=quote(canonical,safe='/'):
            return denied()
        session=AuthService.get_session(request)
        if not session:
            return denied(401)
        actor=task_policy.actor_from_session(db,session)
        tenant=session.get('company_mst')
        if actor is None or not isinstance(tenant,str) or not tenant:
            return denied(401)
        registry=FileRegistry()
        row,bindings=registry.access_snapshot(tenant,Config.UPLOAD_STORAGE_ROOT_ID,storage_name)
        if not row or not registry.valid_provenance(row) or row['classification'] not in ('PRIVATE','VERIFIED_LEGACY') or row['state'] not in ('UNBOUND','BOUND'):
            return denied()
        if row['state']=='UNBOUND':
            if (row['provenance_type']!='VERIFIED_UPLOADER' or row['classification']!='PRIVATE' or row['uploader_id']!=actor.ma
                    or not row['expires_at'] or registry.expired_unbound(row)):
                return denied()
        else:
            allowed=False
            for binding in bindings:
                if binding['tenant_id']!=tenant:
                    continue
                if binding['object_kind']=='TASK' and binding['field_slot'] in ('file_giao_viec','file_bao_cao'):
                    obj=task_policy.load_task(db,binding['object_id'])
                    allowed=bool(obj and getattr(obj,binding['field_slot'])==canonical and task_policy.can_view_task(actor,obj))
                elif binding['object_kind']=='DOCUMENT' and binding['field_slot']=='link_file':
                    from routes.documents import readable_documents_query
                    obj=readable_documents_query(db,session).filter(Document.ma_tl==binding['object_id']).first()
                    allowed=bool(obj and obj.link_file==canonical)
                if allowed:
                    break
            if not allowed:
                return denied()
        content,modified=physical_bytes(row)
        return file_response(request,row,content,modified)
    except (RegistryError,SQLAlchemyError,OSError,ValueError,TypeError,KeyError,UnicodeError):
        return denied()

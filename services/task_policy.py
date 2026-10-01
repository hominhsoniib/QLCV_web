"""Tenant-local Task capabilities. Payload identity never grants authority."""
from dataclasses import dataclass
from models.models import Employee, Task


def code(value):
    return str(value or "").strip().upper()


@dataclass(frozen=True)
class TaskActor:
    ma: str
    admin: bool


def actor_from_session(db, session):
    if not isinstance(session, dict) or not session.get("company_mst"):
        return None
    ma = code(session.get("ma"))
    if not ma or not db.query(Employee).filter(Employee.ma_nv == ma).first():
        return None
    return TaskActor(ma, code(session.get("role")) == "ADMIN")


def load_task(db, task_id):
    return db.query(Task).filter(Task.id_phan_cong == str(task_id or "").strip()).first()


def can_create_task(actor):
    return actor is not None


def can_view_task(actor, task):
    return bool(actor and task and (actor.admin or actor.ma in
                [code(task.nguoi_giao), code(task.nguoi_nhan)] or
                actor.ma in [code(p) for p in (task.nguoi_phoi_hop or "").split(",")]))


def can_edit_task(actor, task):
    return bool(actor and task and (actor.admin or actor.ma == code(task.nguoi_giao)))


can_assign_task = can_edit_task
can_direct_task = can_edit_task
can_bind_task_attachment = can_edit_task


def can_report_task(actor, task):
    return bool(actor and task and (actor.admin or actor.ma == code(task.nguoi_nhan)))


can_delegate_task = can_report_task


def validate_targets(db, giver, receiver, collaborators):
    """Exact employee-code lookup only in the already selected tenant session."""
    giver, receiver = code(giver), code(receiver)
    if not isinstance(collaborators, str):
        raise ValueError("invalid targets")
    cc = list(dict.fromkeys(code(p) for p in collaborators.split(",") if code(p)))
    targets = {giver, receiver, *cc}
    if not giver or not receiver:
        raise ValueError("invalid targets")
    local = {e.ma_nv for e in db.query(Employee).filter(Employee.ma_nv.in_(targets)).all()}
    if targets != local:
        raise ValueError("invalid targets")
    return giver, receiver, ", ".join(cc)

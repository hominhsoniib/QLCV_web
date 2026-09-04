"""
Personal Management API Routes
Handles Personal Tasks, Weekly Planner, Calendar Events,
Business Trips, Travel Trips, Goals, Reminders, and Dashboard summary.
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import AuthService
from models.models import (
    PersonalTask, WeeklyPlan, PersonalCalendar,
    BusinessTrip, TravelTrip, PersonalGoal, PersonalReminder,
    DailyDiary, PersonalExpense, HealthLog, AuditLog
)
import json
import datetime

router = APIRouter()


def _check_auth(request: Request):
    """Returns (session_dict, user_id) or (None, None) if not logged in."""
    session = AuthService.get_session(request)
    if not session:
        return None, None
    return session, session.get("ma", "")


def _model_to_dict(obj):
    """Convert a SQLAlchemy model instance to a plain dict."""
    return {c.name: getattr(obj, c.name) for c in obj.__table__.columns}


# ================================================================
# DASHBOARD
# ================================================================
@router.get("/api/personal/dashboard")
def api_personal_dashboard(request: Request, db: Session = Depends(get_db)):
    """Returns dashboard summary: stats, today tasks, upcoming events, active goals, upcoming trips."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}

    today = datetime.date.today()
    today_str = today.isoformat()
    now_str = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")

    # --- Personal Tasks ---
    all_tasks = db.query(PersonalTask).filter(PersonalTask.user_id == uid).all()
    total_tasks = len(all_tasks)
    done_tasks = sum(1 for t in all_tasks if t.tinh_trang == "Hoàn thành")
    completion_rate = round(done_tasks / total_tasks * 100) if total_tasks else 0

    today_tasks = [t for t in all_tasks if t.ngay_kt and t.ngay_kt[:10] == today_str and t.tinh_trang != "Hoàn thành"]
    overdue_tasks = [t for t in all_tasks if t.ngay_kt and t.ngay_kt[:10] < today_str and t.tinh_trang not in ("Hoàn thành", "Hoãn")]

    # --- Calendar Events (next 7 days) ---
    future_date = (today + datetime.timedelta(days=7)).isoformat()
    upcoming_events = db.query(PersonalCalendar).filter(
        PersonalCalendar.user_id == uid,
        PersonalCalendar.ngay_gio_bd >= now_str,
        PersonalCalendar.ngay_gio_bd <= future_date + "T23:59"
    ).order_by(PersonalCalendar.ngay_gio_bd).limit(5).all()

    # --- Active Goals ---
    active_goals = db.query(PersonalGoal).filter(
        PersonalGoal.user_id == uid,
        PersonalGoal.trang_thai == "Đang thực hiện"
    ).limit(5).all()

    # --- Upcoming Business Trips ---
    upcoming_btrips = db.query(BusinessTrip).filter(
        BusinessTrip.user_id == uid,
        BusinessTrip.ngay_bd >= today_str,
        BusinessTrip.trang_thai != "Hủy"
    ).order_by(BusinessTrip.ngay_bd).limit(3).all()

    # --- Upcoming Travel Trips ---
    upcoming_ttrips = db.query(TravelTrip).filter(
        TravelTrip.user_id == uid,
        TravelTrip.ngay_di >= today_str
    ).order_by(TravelTrip.ngay_di).limit(3).all()

    return {
        "success": True,
        "stats": {
            "totalTasksCount": total_tasks,
            "todayTasksCount": len(today_tasks),
            "overdueTasksCount": len(overdue_tasks),
            "completionRate": completion_rate,
            "todayTasks": [_model_to_dict(t) for t in today_tasks[:5]],
            "upcomingEvents": [_model_to_dict(e) for e in upcoming_events],
            "activeGoals": [_model_to_dict(g) for g in active_goals],
            "upcomingBusinessTrips": [_model_to_dict(t) for t in upcoming_btrips],
            "upcomingTravelTrips": [_model_to_dict(t) for t in upcoming_ttrips],
        }
    }


# ================================================================
# PERSONAL TASKS
# ================================================================
@router.get("/api/personal/tasks")
def api_get_personal_tasks(request: Request, db: Session = Depends(get_db)):
    """Get all personal tasks for the logged-in user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    tasks = db.query(PersonalTask).filter(PersonalTask.user_id == uid).order_by(
        PersonalTask.ngay_kt.asc()
    ).all()
    return {"success": True, "tasks": [_model_to_dict(t) for t in tasks]}


@router.post("/api/personal/tasks")
def api_create_personal_task(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new personal task."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    if not payload.get("ten_cv"):
        return {"success": False, "message": "Tên công việc không được để trống"}

    task = PersonalTask(
        user_id=uid,
        ten_cv=payload["ten_cv"],
        mo_ta=payload.get("mo_ta", ""),
        loai_cv=payload.get("loai_cv", "Cá nhân"),
        muc_do_uu_tien=payload.get("muc_do_uu_tien", "Trung bình"),
        ngay_bd=payload.get("ngay_bd", ""),
        ngay_kt=payload.get("ngay_kt", ""),
        tinh_trang=payload.get("tinh_trang", "Chưa thực hiện"),
        tien_do=int(payload.get("tien_do", 0)),
        nguoi_lien_quan=payload.get("nguoi_lien_quan", ""),
        ghi_chu=payload.get("ghi_chu", ""),
        ngay_gan_tuan=payload.get("ngay_gan_tuan", ""),
        tuan_ke_hoach=payload.get("tuan_ke_hoach", ""),
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Audit Logging
    log = AuditLog(
        user=uid,
        action=f"Tạo công việc cá nhân mới ID {task.id}: {task.ten_cv}",
        status="Thành công"
    )
    db.add(log)
    db.commit()

    return {"success": True, "task": _model_to_dict(task)}


@router.put("/api/personal/tasks/{task_id}")
def api_update_personal_task(task_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update an existing personal task."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    task = db.query(PersonalTask).filter(PersonalTask.id == task_id, PersonalTask.user_id == uid).first()
    if not task:
        return {"success": False, "message": "Không tìm thấy công việc"}
    for field in ("ten_cv","mo_ta","loai_cv","muc_do_uu_tien","ngay_bd","ngay_kt",
                  "tinh_trang","tien_do","nguoi_lien_quan","ghi_chu","ngay_gan_tuan","tuan_ke_hoach"):
        if field in payload:
            setattr(task, field, payload[field])
    db.commit()

    # Audit Logging
    log = AuditLog(
        user=uid,
        action=f"Cập nhật công việc cá nhân ID {task.id}: {task.ten_cv}",
        status="Thành công"
    )
    db.add(log)
    db.commit()

    return {"success": True, "task": _model_to_dict(task)}


@router.delete("/api/personal/tasks/{task_id}")
def api_delete_personal_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a personal task."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    task = db.query(PersonalTask).filter(PersonalTask.id == task_id, PersonalTask.user_id == uid).first()
    if not task:
        return {"success": False, "message": "Không tìm thấy công việc"}
    
    # Audit Logging before deletion
    log = AuditLog(
        user=uid,
        action=f"Xóa công việc cá nhân ID {task.id}: {task.ten_cv}",
        status="Thành công"
    )
    db.add(log)

    db.delete(task)
    db.commit()
    return {"success": True}


@router.post("/api/personal/tasks/{task_id}/copy")
def api_copy_personal_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    """Copy an existing personal task."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    task = db.query(PersonalTask).filter(PersonalTask.id == task_id, PersonalTask.user_id == uid).first()
    if not task:
        return {"success": False, "message": "Không tìm thấy công việc để sao chép"}

    new_task = PersonalTask(
        user_id=uid,
        ten_cv=f"Sao chép: {task.ten_cv}",
        mo_ta=task.mo_ta,
        loai_cv=task.loai_cv,
        muc_do_uu_tien=task.muc_do_uu_tien,
        ngay_bd=task.ngay_bd,
        ngay_kt=task.ngay_kt,
        tinh_trang="Chưa thực hiện",
        tien_do=0,
        nguoi_lien_quan=task.nguoi_lien_quan,
        ghi_chu=task.ghi_chu,
        ngay_gan_tuan=task.ngay_gan_tuan,
        tuan_ke_hoach=task.tuan_ke_hoach,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    # Audit Logging
    log = AuditLog(
        user=uid,
        action=f"Sao chép công việc cá nhân ID {task.id} -> ID mới {new_task.id}",
        status="Thành công"
    )
    db.add(log)
    db.commit()

    return {"success": True, "task": _model_to_dict(new_task)}


# ================================================================
# WEEKLY PLANNER
# ================================================================
@router.get("/api/personal/weekly")
def api_get_weekly_plan(request: Request, week: str = "", db: Session = Depends(get_db)):
    """Get weekly plan + tasks assigned to this week."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}

    plan = db.query(WeeklyPlan).filter(
        WeeklyPlan.user_id == uid,
        WeeklyPlan.tuan == week
    ).first()

    if not plan:
        plan_data = {"muc_tieu_tuan": "", "tong_gio_du_kien": 0.0, "tong_gio_thuc_te": 0.0}
    else:
        plan_data = _model_to_dict(plan)

    tasks = db.query(PersonalTask).filter(
        PersonalTask.user_id == uid,
        PersonalTask.tuan_ke_hoach == week
    ).all()

    return {"success": True, "plan": plan_data, "tasks": [_model_to_dict(t) for t in tasks]}


@router.post("/api/personal/weekly")
def api_save_weekly_plan(request: Request, payload: dict, week: str = "", db: Session = Depends(get_db)):
    """Save or update a weekly plan."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    if not week:
        week = payload.get("tuan", "")

    plan = db.query(WeeklyPlan).filter(WeeklyPlan.user_id == uid, WeeklyPlan.tuan == week).first()
    if plan:
        plan.muc_tieu_tuan = payload.get("muc_tieu_tuan", plan.muc_tieu_tuan)
        plan.tong_gio_du_kien = float(payload.get("tong_gio_du_kien", plan.tong_gio_du_kien))
        plan.tong_gio_thuc_te = float(payload.get("tong_gio_thuc_te", plan.tong_gio_thuc_te))
    else:
        plan = WeeklyPlan(
            user_id=uid, tuan=week,
            muc_tieu_tuan=payload.get("muc_tieu_tuan", ""),
            tong_gio_du_kien=float(payload.get("tong_gio_du_kien", 0)),
            tong_gio_thuc_te=float(payload.get("tong_gio_thuc_te", 0)),
        )
        db.add(plan)
    db.commit()
    return {"success": True}


# ================================================================
# PERSONAL CALENDAR
# ================================================================
@router.get("/api/personal/calendar")
def api_get_calendar(request: Request, db: Session = Depends(get_db)):
    """Get all calendar events for the logged-in user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    events = db.query(PersonalCalendar).filter(PersonalCalendar.user_id == uid).order_by(
        PersonalCalendar.ngay_gio_bd.asc()
    ).all()
    return {"success": True, "events": [_model_to_dict(e) for e in events]}


@router.post("/api/personal/calendar")
def api_create_calendar_event(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new calendar event."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    event = PersonalCalendar(
        user_id=uid,
        tieu_de=payload.get("tieu_de", "Sự kiện"),
        loai_lich=payload.get("loai_lich", "Công việc"),
        ngay_gio_bd=payload.get("ngay_gio_bd", ""),
        ngay_gio_kt=payload.get("ngay_gio_kt", ""),
        dia_diem=payload.get("dia_diem", ""),
        nguoi_tham_gia=payload.get("nguoi_tham_gia", ""),
        ghi_chu=payload.get("ghi_chu", ""),
        nhac_nho=payload.get("nhac_nho", "Không"),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return {"success": True, "event": _model_to_dict(event)}


@router.put("/api/personal/calendar/{event_id}")
def api_update_calendar_event(event_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update a calendar event."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    event = db.query(PersonalCalendar).filter(PersonalCalendar.id == event_id, PersonalCalendar.user_id == uid).first()
    if not event:
        return {"success": False, "message": "Không tìm thấy sự kiện"}
    for field in ("tieu_de","loai_lich","ngay_gio_bd","ngay_gio_kt","dia_diem","nguoi_tham_gia","ghi_chu","nhac_nho"):
        if field in payload:
            setattr(event, field, payload[field])
    db.commit()
    return {"success": True}


@router.delete("/api/personal/calendar/{event_id}")
def api_delete_calendar_event(event_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a calendar event."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    event = db.query(PersonalCalendar).filter(PersonalCalendar.id == event_id, PersonalCalendar.user_id == uid).first()
    if not event:
        return {"success": False, "message": "Không tìm thấy sự kiện"}
    db.delete(event)
    db.commit()
    return {"success": True}


# ================================================================
# BUSINESS TRIPS
# ================================================================
@router.get("/api/personal/trips/business")
def api_get_business_trips(request: Request, db: Session = Depends(get_db)):
    """Get all business trips for the current user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    trips = db.query(BusinessTrip).filter(BusinessTrip.user_id == uid).order_by(
        BusinessTrip.ngay_bd.desc()
    ).all()
    return {"success": True, "trips": [_model_to_dict(t) for t in trips]}


@router.post("/api/personal/trips/business")
def api_create_business_trip(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new business trip."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    trip = BusinessTrip(
        user_id=uid,
        ten_chuyen_di=payload.get("ten_chuyen_di", "Công tác"),
        ngay_bd=payload.get("ngay_bd", ""),
        ngay_kt=payload.get("ngay_kt", ""),
        lich_trinh_json=json.dumps(payload.get("lich_trinh", []), ensure_ascii=False),
        chi_phi_json=json.dumps(payload.get("chi_phi", []), ensure_ascii=False),
        trang_thai=payload.get("trang_thai", "Lên kế hoạch"),
        dia_diem=payload.get("dia_diem", ""),
        phuong_tien=payload.get("phuong_tien", ""),
        khach_san=payload.get("khach_san", ""),
        chi_phi_du_kien=float(payload.get("chi_phi_du_kien", 0) or 0),
        chi_phi_thuc_te=float(payload.get("chi_phi_thuc_te", 0) or 0),
        cong_viec_json=json.dumps(payload.get("cong_viec", []), ensure_ascii=False),
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return {"success": True, "trip": _model_to_dict(trip)}


@router.put("/api/personal/trips/business/{trip_id}")
def api_update_business_trip(trip_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update an existing business trip."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    trip = db.query(BusinessTrip).filter(BusinessTrip.id == trip_id, BusinessTrip.user_id == uid).first()
    if not trip:
        return {"success": False, "message": "Không tìm thấy chuyến công tác"}
    for field in ("ten_chuyen_di","ngay_bd","ngay_kt","trang_thai","dia_diem","phuong_tien","khach_san"):
        if field in payload:
            setattr(trip, field, payload[field])
    if "chi_phi_du_kien" in payload:
        trip.chi_phi_du_kien = float(payload["chi_phi_du_kien"] or 0)
    if "chi_phi_thuc_te" in payload:
        trip.chi_phi_thuc_te = float(payload["chi_phi_thuc_te"] or 0)
    if "lich_trinh" in payload:
        trip.lich_trinh_json = json.dumps(payload["lich_trinh"], ensure_ascii=False)
    if "chi_phi" in payload:
        trip.chi_phi_json = json.dumps(payload["chi_phi"], ensure_ascii=False)
    if "cong_viec" in payload:
        trip.cong_viec_json = json.dumps(payload["cong_viec"], ensure_ascii=False)
    db.commit()
    return {"success": True}


@router.delete("/api/personal/trips/business/{trip_id}")
def api_delete_business_trip(trip_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a business trip."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    trip = db.query(BusinessTrip).filter(BusinessTrip.id == trip_id, BusinessTrip.user_id == uid).first()
    if not trip:
        return {"success": False, "message": "Không tìm thấy"}
    db.delete(trip)
    db.commit()
    return {"success": True}


# ================================================================
# TRAVEL TRIPS
# ================================================================
@router.get("/api/personal/trips/travel")
def api_get_travel_trips(request: Request, db: Session = Depends(get_db)):
    """Get all travel trips for the current user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    trips = db.query(TravelTrip).filter(TravelTrip.user_id == uid).order_by(TravelTrip.ngay_di.asc()).all()
    return {"success": True, "trips": [_model_to_dict(t) for t in trips]}


@router.post("/api/personal/trips/travel")
def api_create_travel_trip(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new travel trip with a default packing checklist."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}

    default_checklist = [
        {"item": "Đặt vé máy bay / xe / tàu", "done": False},
        {"item": "Đặt khách sạn / phòng nghỉ", "done": False},
        {"item": "Chuẩn bị hành lý", "done": False},
        {"item": "Mang theo CMND / hộ chiếu", "done": False},
        {"item": "Đổi tiền / nạp tiền thẻ", "done": False},
        {"item": "Mua bảo hiểm du lịch", "done": False},
        {"item": "Tải app bản đồ offline", "done": False},
        {"item": "Sạc dự phòng / cáp sạc", "done": False},
    ]
    checklist = payload.get("checklist", default_checklist)

    trip = TravelTrip(
        user_id=uid,
        ten_chuyen_di=payload.get("ten_chuyen_di", "Chuyến đi"),
        diem_den=payload.get("diem_den", ""),
        ngay_di=payload.get("ngay_di", ""),
        ngay_ve=payload.get("ngay_ve", ""),
        ngan_sach=float(payload.get("ngan_sach", 0)),
        nguoi_di_cung=payload.get("nguoi_di_cung", ""),
        checklist_json=json.dumps(checklist, ensure_ascii=False),
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return {"success": True, "trip": _model_to_dict(trip)}


@router.put("/api/personal/trips/travel/{trip_id}")
def api_update_travel_trip(trip_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update a travel trip (including checklist toggle)."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    trip = db.query(TravelTrip).filter(TravelTrip.id == trip_id, TravelTrip.user_id == uid).first()
    if not trip:
        return {"success": False, "message": "Không tìm thấy chuyến đi"}
    for field in ("ten_chuyen_di","diem_den","ngay_di","ngay_ve","nguoi_di_cung"):
        if field in payload:
            setattr(trip, field, payload[field])
    if "ngan_sach" in payload:
        trip.ngan_sach = float(payload["ngan_sach"])
    if "checklist" in payload:
        trip.checklist_json = json.dumps(payload["checklist"], ensure_ascii=False)
    db.commit()
    return {"success": True}


@router.delete("/api/personal/trips/travel/{trip_id}")
def api_delete_travel_trip(trip_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a travel trip."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    trip = db.query(TravelTrip).filter(TravelTrip.id == trip_id, TravelTrip.user_id == uid).first()
    if not trip:
        return {"success": False, "message": "Không tìm thấy"}
    db.delete(trip)
    db.commit()
    return {"success": True}


# ================================================================
# PERSONAL GOALS
# ================================================================
@router.get("/api/personal/goals")
def api_get_goals(request: Request, db: Session = Depends(get_db)):
    """Get all personal goals for the current user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    goals = db.query(PersonalGoal).filter(PersonalGoal.user_id == uid).order_by(
        PersonalGoal.ngay_kt.asc()
    ).all()
    return {"success": True, "goals": [_model_to_dict(g) for g in goals]}


@router.post("/api/personal/goals")
def api_create_goal(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new personal goal."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    goal = PersonalGoal(
        user_id=uid,
        ten_muc_tieu=payload.get("ten_muc_tieu", "Mục tiêu"),
        loai_muc_tieu=payload.get("loai_muc_tieu", "Tháng"),
        mo_ta=payload.get("mo_ta", ""),
        ngay_bd=payload.get("ngay_bd", ""),
        ngay_kt=payload.get("ngay_kt", ""),
        kpi=payload.get("kpi", ""),
        tien_do=int(payload.get("tien_do", 0)),
        trang_thai=payload.get("trang_thai", "Đang thực hiện"),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"success": True, "goal": _model_to_dict(goal)}


@router.put("/api/personal/goals/{goal_id}")
def api_update_goal(goal_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update a personal goal."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    goal = db.query(PersonalGoal).filter(PersonalGoal.id == goal_id, PersonalGoal.user_id == uid).first()
    if not goal:
        return {"success": False, "message": "Không tìm thấy mục tiêu"}
    for field in ("ten_muc_tieu","loai_muc_tieu","mo_ta","ngay_bd","ngay_kt","kpi","tien_do","trang_thai"):
        if field in payload:
            setattr(goal, field, payload[field])
    db.commit()
    return {"success": True}


@router.delete("/api/personal/goals/{goal_id}")
def api_delete_goal(goal_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a personal goal."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    goal = db.query(PersonalGoal).filter(PersonalGoal.id == goal_id, PersonalGoal.user_id == uid).first()
    if not goal:
        return {"success": False, "message": "Không tìm thấy"}
    db.delete(goal)
    db.commit()
    return {"success": True}


# ================================================================
# PERSONAL REMINDERS
# ================================================================
@router.get("/api/personal/reminders")
def api_get_reminders(request: Request, db: Session = Depends(get_db)):
    """Get all personal reminders for the current user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    reminders = db.query(PersonalReminder).filter(PersonalReminder.user_id == uid).order_by(
        PersonalReminder.thoi_gian_nhac.asc()
    ).all()
    return {"success": True, "reminders": [_model_to_dict(r) for r in reminders]}


@router.post("/api/personal/reminders")
def api_create_reminder(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new personal reminder."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    reminder = PersonalReminder(
        user_id=uid,
        loai_nhac=payload.get("loai_nhac", "App"),
        thoi_gian_nhac=payload.get("thoi_gian_nhac", ""),
        lap_lai=payload.get("lap_lai", "Không"),
        noi_dung=payload.get("noi_dung", ""),
        ref_type=payload.get("ref_type", "task"),
        ref_id=payload.get("ref_id"),
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return {"success": True, "reminder": _model_to_dict(reminder)}


@router.delete("/api/personal/reminders/{reminder_id}")
def api_delete_reminder(reminder_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a personal reminder."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    reminder = db.query(PersonalReminder).filter(
        PersonalReminder.id == reminder_id, PersonalReminder.user_id == uid
    ).first()
    if not reminder:
        return {"success": False, "message": "Không tìm thấy"}
    db.delete(reminder)
    db.commit()
    return {"success": True}


# ================================================================
# DAILY DIARY
# ================================================================
@router.get("/api/personal/diary")
def api_get_diary(request: Request, db: Session = Depends(get_db)):
    """Get all diary logs for current user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    diaries = db.query(DailyDiary).filter(DailyDiary.user_id == uid).order_by(DailyDiary.ngay.desc()).all()
    return {"success": True, "diaries": [_model_to_dict(d) for d in diaries]}


@router.post("/api/personal/diary")
def api_create_diary(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new diary log."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    diary = DailyDiary(
        user_id=uid,
        ngay=payload.get("ngay", ""),
        tieu_de=payload.get("tieu_de", "Nhật ký"),
        noi_dung=payload.get("noi_dung", ""),
        tam_trang=payload.get("tam_trang", "")
    )
    db.add(diary)
    db.commit()
    db.refresh(diary)
    return {"success": True, "diary": _model_to_dict(diary)}


@router.put("/api/personal/diary/{diary_id}")
def api_update_diary(diary_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update diary log."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    diary = db.query(DailyDiary).filter(DailyDiary.id == diary_id, DailyDiary.user_id == uid).first()
    if not diary:
        return {"success": False, "message": "Không tìm thấy nhật ký"}
    for field in ("tieu_de", "noi_dung", "tam_trang", "ngay"):
        if field in payload:
            setattr(diary, field, payload[field])
    db.commit()
    return {"success": True, "diary": _model_to_dict(diary)}


@router.delete("/api/personal/diary/{diary_id}")
def api_delete_diary(diary_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete diary log."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    diary = db.query(DailyDiary).filter(DailyDiary.id == diary_id, DailyDiary.user_id == uid).first()
    if not diary:
        return {"success": False, "message": "Không tìm thấy nhật ký"}
    db.delete(diary)
    db.commit()
    return {"success": True}


# ================================================================
# PERSONAL EXPENSES
# ================================================================
@router.get("/api/personal/expenses")
def api_get_expenses(request: Request, db: Session = Depends(get_db)):
    """Get all expenses for current user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    expenses = db.query(PersonalExpense).filter(PersonalExpense.user_id == uid).order_by(PersonalExpense.ngay.desc()).all()
    return {"success": True, "expenses": [_model_to_dict(e) for e in expenses]}


@router.post("/api/personal/expenses")
def api_create_expense(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new expense item."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    expense = PersonalExpense(
        user_id=uid,
        ngay=payload.get("ngay", ""),
        khoan_chi=payload.get("khoan_chi", ""),
        so_tien=float(payload.get("so_tien", 0)),
        danh_muc=payload.get("danh_muc", "Khác"),
        ghi_chu=payload.get("ghi_chu", "")
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return {"success": True, "expense": _model_to_dict(expense)}


@router.put("/api/personal/expenses/{expense_id}")
def api_update_expense(expense_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update expense item."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    expense = db.query(PersonalExpense).filter(PersonalExpense.id == expense_id, PersonalExpense.user_id == uid).first()
    if not expense:
        return {"success": False, "message": "Không tìm thấy khoản chi"}
    for field in ("khoan_chi", "danh_muc", "ghi_chu", "ngay"):
        if field in payload:
            setattr(expense, field, payload[field])
    if "so_tien" in payload:
        expense.so_tien = float(payload["so_tien"])
    db.commit()
    return {"success": True, "expense": _model_to_dict(expense)}


@router.delete("/api/personal/expenses/{expense_id}")
def api_delete_expense(expense_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete expense item."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    expense = db.query(PersonalExpense).filter(PersonalExpense.id == expense_id, PersonalExpense.user_id == uid).first()
    if not expense:
        return {"success": False, "message": "Không tìm thấy khoản chi"}
    db.delete(expense)
    db.commit()
    return {"success": True}


# ================================================================
# HEALTH LOGS
# ================================================================
@router.get("/api/personal/health")
def api_get_health(request: Request, db: Session = Depends(get_db)):
    """Get all health logs for current user."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    logs = db.query(HealthLog).filter(HealthLog.user_id == uid).order_by(HealthLog.ngay.desc()).all()
    return {"success": True, "logs": [_model_to_dict(l) for l in logs]}


@router.post("/api/personal/health")
def api_create_health(request: Request, payload: dict, db: Session = Depends(get_db)):
    """Create a new health log."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    log = HealthLog(
        user_id=uid,
        ngay=payload.get("ngay", ""),
        huyet_ap=payload.get("huyet_ap", ""),
        can_nang=float(payload.get("can_nang", 0) or 0),
        tinh_trang_suc_khoe=payload.get("tinh_trang_suc_khoe", ""),
        ghi_chu=payload.get("ghi_chu", "")
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"success": True, "log": _model_to_dict(log)}


@router.put("/api/personal/health/{log_id}")
def api_update_health(log_id: int, request: Request, payload: dict, db: Session = Depends(get_db)):
    """Update health log."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    log = db.query(HealthLog).filter(HealthLog.id == log_id, HealthLog.user_id == uid).first()
    if not log:
        return {"success": False, "message": "Không tìm thấy ghi chép sức khỏe"}
    for field in ("huyet_ap", "tinh_trang_suc_khoe", "ghi_chu", "ngay"):
        if field in payload:
            setattr(log, field, payload[field])
    if "can_nang" in payload:
        log.can_nang = float(payload["can_nang"] or 0)
    db.commit()
    return {"success": True, "log": _model_to_dict(log)}


@router.delete("/api/personal/health/{log_id}")
def api_delete_health(log_id: int, request: Request, db: Session = Depends(get_db)):
    """Delete health log."""
    session, uid = _check_auth(request)
    if not session:
        return {"success": False, "message": "Chưa đăng nhập"}
    log = db.query(HealthLog).filter(HealthLog.id == log_id, HealthLog.user_id == uid).first()
    if not log:
        return {"success": False, "message": "Không tìm thấy ghi chép sức khỏe"}
    db.delete(log)
    db.commit()
    return {"success": True}

import json
import datetime
from sqlalchemy.orm import Session
from models.models import (
    PersonalTask, WeeklyPlan, PersonalCalendar, 
    BusinessTrip, TravelTrip, PersonalGoal, PersonalReminder
)

class PersonalService:
    @staticmethod
    def get_dashboard_stats(db: Session, user_id: str):
        """Calculates general dashboard stats for a specific user."""
        today_str = datetime.date.today().isoformat()
        
        # 1. Today tasks: starting or ending today, or in progress
        today_tasks_query = db.query(PersonalTask).filter(
            PersonalTask.user_id == user_id,
            (
                PersonalTask.ngay_bd.like(f"{today_str}%") | 
                PersonalTask.ngay_kt.like(f"{today_str}%") | 
                (PersonalTask.tinh_trang == "Đang thực hiện")
            )
        )
        today_tasks_count = today_tasks_query.count()
        today_tasks = [
            {
                "id": t.id,
                "ten_cv": t.ten_cv,
                "loai_cv": t.loai_cv,
                "ngay_kt": t.ngay_kt,
                "tinh_trang": t.tinh_trang,
                "tien_do": t.tien_do,
                "muc_do_uu_tien": t.muc_do_uu_tien
            } for t in today_tasks_query.limit(5).all()
        ]

        # 2. Overdue tasks: deadline passed and progress < 100
        overdue_query = db.query(PersonalTask).filter(
            PersonalTask.user_id == user_id,
            PersonalTask.ngay_kt < today_str,
            PersonalTask.tinh_trang != "Hoàn thành",
            PersonalTask.tien_do < 100
        )
        overdue_count = overdue_query.count()

        # 3. All active tasks (this week or overall)
        all_tasks = db.query(PersonalTask).filter(PersonalTask.user_id == user_id).all()
        total_tasks = len(all_tasks)
        completed_tasks = sum(1 for t in all_tasks if t.tinh_trang == "Hoàn thành" or t.tien_do == 100)
        completion_rate = round((completed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

        # 4. Upcoming calendar events
        calendar_events = db.query(PersonalCalendar).filter(
            PersonalCalendar.user_id == user_id,
            PersonalCalendar.ngay_gio_bd >= today_str
        ).order_by(PersonalCalendar.ngay_gio_bd.asc()).limit(5).all()
        
        events_list = [
            {
                "id": e.id,
                "tieu_de": e.tieu_de,
                "loai_lich": e.loai_lich,
                "ngay_gio_bd": e.ngay_gio_bd,
                "dia_diem": e.dia_diem
            } for e in calendar_events
        ]

        # 5. Upcoming trips
        business_trips = db.query(BusinessTrip).filter(
            BusinessTrip.user_id == user_id,
            BusinessTrip.ngay_bd >= today_str
        ).order_by(BusinessTrip.ngay_bd.asc()).limit(3).all()
        
        b_trips_list = [
            {
                "id": t.id,
                "ten_chuyen_di": t.ten_chuyen_di,
                "ngay_bd": t.ngay_bd,
                "ngay_kt": t.ngay_kt,
                "trang_thai": t.trang_thai
            } for t in business_trips
        ]

        travel_trips = db.query(TravelTrip).filter(
            TravelTrip.user_id == user_id,
            TravelTrip.ngay_di >= today_str
        ).order_by(TravelTrip.ngay_di.asc()).limit(3).all()
        
        t_trips_list = [
            {
                "id": t.id,
                "ten_chuyen_di": t.ten_chuyen_di,
                "diem_den": t.diem_den,
                "ngay_di": t.ngay_di,
                "ngay_ve": t.ngay_ve
            } for t in travel_trips
        ]

        # 6. Active goals
        active_goals = db.query(PersonalGoal).filter(
            PersonalGoal.user_id == user_id,
            PersonalGoal.trang_thai == "Đang thực hiện"
        ).order_by(PersonalGoal.ngay_kt.asc()).all()
        
        goals_list = [
            {
                "id": g.id,
                "ten_muc_tieu": g.ten_muc_tieu,
                "loai_muc_tieu": g.loai_muc_tieu,
                "tien_do": g.tien_do,
                "ngay_kt": g.ngay_kt
            } for g in active_goals
        ]

        return {
            "success": True,
            "stats": {
                "todayTasksCount": today_tasks_count,
                "overdueTasksCount": overdue_count,
                "totalTasksCount": total_tasks,
                "completionRate": completion_rate,
                "todayTasks": today_tasks,
                "upcomingEvents": events_list,
                "upcomingBusinessTrips": b_trips_list,
                "upcomingTravelTrips": t_trips_list,
                "activeGoals": goals_list
            }
        }

    # --- PERSONAL TASK CRUD ---
    @staticmethod
    def get_tasks(db: Session, user_id: str):
        return db.query(PersonalTask).filter(PersonalTask.user_id == user_id).all()

    @staticmethod
    def create_task(db: Session, user_id: str, data: dict):
        task = PersonalTask(
            user_id=user_id,
            ten_cv=data.get("ten_cv"),
            mo_ta=data.get("mo_ta", ""),
            loai_cv=data.get("loai_cv", "Cá nhân"),
            muc_do_uu_tien=data.get("muc_do_uu_tien", "Trung bình"),
            ngay_bd=data.get("ngay_bd"),
            ngay_kt=data.get("ngay_kt"),
            tinh_trang=data.get("tinh_trang", "Chưa thực hiện"),
            tien_do=data.get("tien_do", 0),
            nguoi_lien_quan=data.get("nguoi_lien_quan", ""),
            file_dinh_kem=data.get("file_dinh_kem", ""),
            ghi_chu=data.get("ghi_chu", ""),
            co_nhac_nho=data.get("co_nhac_nho", 0),
            ngay_gan_tuan=data.get("ngay_gan_tuan", ""),
            tuan_ke_hoach=data.get("tuan_ke_hoach", "")
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def update_task(db: Session, user_id: str, task_id: int, data: dict):
        task = db.query(PersonalTask).filter(PersonalTask.id == task_id, PersonalTask.user_id == user_id).first()
        if not task:
            return None
        
        task.ten_cv = data.get("ten_cv", task.ten_cv)
        task.mo_ta = data.get("mo_ta", task.mo_ta)
        task.loai_cv = data.get("loai_cv", task.loai_cv)
        task.muc_do_uu_tien = data.get("muc_do_uu_tien", task.muc_do_uu_tien)
        task.ngay_bd = data.get("ngay_bd", task.ngay_bd)
        task.ngay_kt = data.get("ngay_kt", task.ngay_kt)
        task.tinh_trang = data.get("tinh_trang", task.tinh_trang)
        task.tien_do = data.get("tien_do", task.tien_do)
        task.nguoi_lien_quan = data.get("nguoi_lien_quan", task.nguoi_lien_quan)
        task.file_dinh_kem = data.get("file_dinh_kem", task.file_dinh_kem)
        task.ghi_chu = data.get("ghi_chu", task.ghi_chu)
        task.co_nhac_nho = data.get("co_nhac_nho", task.co_nhac_nho)
        task.ngay_gan_tuan = data.get("ngay_gan_tuan", task.ngay_gan_tuan)
        task.tuan_ke_hoach = data.get("tuan_ke_hoach", task.tuan_ke_hoach)
        
        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, user_id: str, task_id: int):
        task = db.query(PersonalTask).filter(PersonalTask.id == task_id, PersonalTask.user_id == user_id).first()
        if not task:
            return False
        db.delete(task)
        db.commit()
        return True

    # --- WEEKLY PLAN & DAY DISTRIBUTION ---
    @staticmethod
    def get_weekly_plan(db: Session, user_id: str, week_str: str):
        # Fetch or auto-create weekly plan object
        plan = db.query(WeeklyPlan).filter(WeeklyPlan.user_id == user_id, WeeklyPlan.tuan == week_str).first()
        if not plan:
            plan = WeeklyPlan(user_id=user_id, tuan=week_str, muc_tieu_tuan="", tong_gio_du_kien=0.0, tong_gio_thuc_te=0.0)
            db.add(plan)
            db.commit()
            db.refresh(plan)
            
        tasks = db.query(PersonalTask).filter(
            PersonalTask.user_id == user_id,
            PersonalTask.tuan_ke_hoach == week_str
        ).all()
        
        return {
            "plan": plan,
            "tasks": tasks
        }

    @staticmethod
    def save_weekly_plan(db: Session, user_id: str, week_str: str, data: dict):
        plan = db.query(WeeklyPlan).filter(WeeklyPlan.user_id == user_id, WeeklyPlan.tuan == week_str).first()
        if not plan:
            plan = WeeklyPlan(user_id=user_id, tuan=week_str)
            db.add(plan)
        
        plan.muc_tieu_tuan = data.get("muc_tieu_tuan", plan.muc_tieu_tuan)
        plan.tong_gio_du_kien = float(data.get("tong_gio_du_kien", plan.tong_gio_du_kien or 0.0))
        plan.tong_gio_thuc_te = float(data.get("tong_gio_thuc_te", plan.tong_gio_thuc_te or 0.0))
        db.commit()
        db.refresh(plan)
        return plan

    # --- PERSONAL CALENDAR CRUD ---
    @staticmethod
    def get_calendar(db: Session, user_id: str):
        return db.query(PersonalCalendar).filter(PersonalCalendar.user_id == user_id).all()

    @staticmethod
    def create_calendar(db: Session, user_id: str, data: dict):
        event = PersonalCalendar(
            user_id=user_id,
            tieu_de=data.get("tieu_de"),
            loai_lich=data.get("loai_lich", "Công việc"),
            ngay_gio_bd=data.get("ngay_gio_bd"),
            ngay_gio_kt=data.get("ngay_gio_kt"),
            dia_diem=data.get("dia_diem", ""),
            nguoi_tham_gia=data.get("nguoi_tham_gia", ""),
            ghi_chu=data.get("ghi_chu", ""),
            nhac_nho=data.get("nhac_nho", "Không")
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def update_calendar(db: Session, user_id: str, event_id: int, data: dict):
        event = db.query(PersonalCalendar).filter(PersonalCalendar.id == event_id, PersonalCalendar.user_id == user_id).first()
        if not event:
            return None
        event.tieu_de = data.get("tieu_de", event.tieu_de)
        event.loai_lich = data.get("loai_lich", event.loai_lich)
        event.ngay_gio_bd = data.get("ngay_gio_bd", event.ngay_gio_bd)
        event.ngay_gio_kt = data.get("ngay_gio_kt", event.ngay_gio_kt)
        event.dia_diem = data.get("dia_diem", event.dia_diem)
        event.nguoi_tham_gia = data.get("nguoi_tham_gia", event.nguoi_tham_gia)
        event.ghi_chu = data.get("ghi_chu", event.ghi_chu)
        event.nhac_nho = data.get("nhac_nho", event.nhac_nho)
        db.commit()
        db.refresh(event)
        return event

    @staticmethod
    def delete_calendar(db: Session, user_id: str, event_id: int):
        event = db.query(PersonalCalendar).filter(PersonalCalendar.id == event_id, PersonalCalendar.user_id == user_id).first()
        if not event:
            return False
        db.delete(event)
        db.commit()
        return True

    # --- BUSINESS TRIP CRUD ---
    @staticmethod
    def get_business_trips(db: Session, user_id: str):
        return db.query(BusinessTrip).filter(BusinessTrip.user_id == user_id).all()

    @staticmethod
    def create_business_trip(db: Session, user_id: str, data: dict):
        trip = BusinessTrip(
            user_id=user_id,
            ten_chuyen_di=data.get("ten_chuyen_di"),
            ngay_bd=data.get("ngay_bd"),
            ngay_kt=data.get("ngay_kt"),
            lich_trinh_json=json.dumps(data.get("lich_trinh", [])),
            chi_phi_json=json.dumps(data.get("chi_phi", [])),
            trang_thai=data.get("trang_thai", "Lên kế hoạch")
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def update_business_trip(db: Session, user_id: str, trip_id: int, data: dict):
        trip = db.query(BusinessTrip).filter(BusinessTrip.id == trip_id, BusinessTrip.user_id == user_id).first()
        if not trip:
            return None
        trip.ten_chuyen_di = data.get("ten_chuyen_di", trip.ten_chuyen_di)
        trip.ngay_bd = data.get("ngay_bd", trip.ngay_bd)
        trip.ngay_kt = data.get("ngay_kt", trip.ngay_kt)
        if "lich_trinh" in data:
            trip.lich_trinh_json = json.dumps(data["lich_trinh"])
        if "chi_phi" in data:
            trip.chi_phi_json = json.dumps(data["chi_phi"])
        trip.trang_thai = data.get("trang_thai", trip.trang_thai)
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def delete_business_trip(db: Session, user_id: str, trip_id: int):
        trip = db.query(BusinessTrip).filter(BusinessTrip.id == trip_id, BusinessTrip.user_id == user_id).first()
        if not trip:
            return False
        db.delete(trip)
        db.commit()
        return True

    # --- TRAVEL TRIP CRUD ---
    @staticmethod
    def get_travel_trips(db: Session, user_id: str):
        return db.query(TravelTrip).filter(TravelTrip.user_id == user_id).all()

    @staticmethod
    def create_travel_trip(db: Session, user_id: str, data: dict):
        # Default checklist from requirements
        default_checklist = [
            {"item": "Đặt vé", "done": False},
            {"item": "Đặt khách sạn", "done": False},
            {"item": "Chuẩn bị hành lý", "done": False},
            {"item": "Đổi tiền", "done": False},
            {"item": "Mua bảo hiểm", "done": False},
            {"item": "Chuẩn bị giấy tờ", "done": False}
        ]
        checklist = data.get("checklist", default_checklist)
        
        trip = TravelTrip(
            user_id=user_id,
            ten_chuyen_di=data.get("ten_chuyen_di"),
            diem_den=data.get("diem_den", ""),
            ngay_di=data.get("ngay_di"),
            ngay_ve=data.get("ngay_ve"),
            ngan_sach=float(data.get("ngan_sach", 0.0)),
            nguoi_di_cung=data.get("nguoi_di_cung", ""),
            checklist_json=json.dumps(checklist)
        )
        db.add(trip)
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def update_travel_trip(db: Session, user_id: str, trip_id: int, data: dict):
        trip = db.query(TravelTrip).filter(TravelTrip.id == trip_id, TravelTrip.user_id == user_id).first()
        if not trip:
            return None
        trip.ten_chuyen_di = data.get("ten_chuyen_di", trip.ten_chuyen_di)
        trip.diem_den = data.get("diem_den", trip.diem_den)
        trip.ngay_di = data.get("ngay_di", trip.ngay_di)
        trip.ngay_ve = data.get("ngay_ve", trip.ngay_ve)
        trip.ngan_sach = float(data.get("ngan_sach", trip.ngan_sach or 0.0))
        trip.nguoi_di_cung = data.get("nguoi_di_cung", trip.nguoi_di_cung)
        if "checklist" in data:
            trip.checklist_json = json.dumps(data["checklist"])
        db.commit()
        db.refresh(trip)
        return trip

    @staticmethod
    def delete_travel_trip(db: Session, user_id: str, trip_id: int):
        trip = db.query(TravelTrip).filter(TravelTrip.id == trip_id, TravelTrip.user_id == user_id).first()
        if not trip:
            return False
        db.delete(trip)
        db.commit()
        return True

    # --- PERSONAL GOALS CRUD ---
    @staticmethod
    def get_goals(db: Session, user_id: str):
        return db.query(PersonalGoal).filter(PersonalGoal.user_id == user_id).all()

    @staticmethod
    def create_goal(db: Session, user_id: str, data: dict):
        goal = PersonalGoal(
            user_id=user_id,
            ten_muc_tieu=data.get("ten_muc_tieu"),
            loai_muc_tieu=data.get("loai_muc_tieu", "Tháng"),
            mo_ta=data.get("mo_ta", ""),
            ngay_bd=data.get("ngay_bd"),
            ngay_kt=data.get("ngay_kt"),
            kpi=data.get("kpi", ""),
            tien_do=int(data.get("tien_do", 0)),
            trang_thai=data.get("trang_thai", "Đang thực hiện")
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def update_goal(db: Session, user_id: str, goal_id: int, data: dict):
        goal = db.query(PersonalGoal).filter(PersonalGoal.id == goal_id, PersonalGoal.user_id == user_id).first()
        if not goal:
            return None
        goal.ten_muc_tieu = data.get("ten_muc_tieu", goal.ten_muc_tieu)
        goal.loai_muc_tieu = data.get("loai_muc_tieu", goal.loai_muc_tieu)
        goal.mo_ta = data.get("mo_ta", goal.mo_ta)
        goal.ngay_bd = data.get("ngay_bd", goal.ngay_bd)
        goal.ngay_kt = data.get("ngay_kt", goal.ngay_kt)
        goal.kpi = data.get("kpi", goal.kpi)
        goal.tien_do = int(data.get("tien_do", goal.tien_do or 0))
        goal.trang_thai = data.get("trang_thai", goal.trang_thai)
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete_goal(db: Session, user_id: str, goal_id: int):
        goal = db.query(PersonalGoal).filter(PersonalGoal.id == goal_id, PersonalGoal.user_id == user_id).first()
        if not goal:
            return False
        db.delete(goal)
        db.commit()
        return True

    # --- REMINDERS CRUD ---
    @staticmethod
    def get_reminders(db: Session, user_id: str):
        return db.query(PersonalReminder).filter(PersonalReminder.user_id == user_id).all()

    @staticmethod
    def create_reminder(db: Session, user_id: str, data: dict):
        reminder = PersonalReminder(
            user_id=user_id,
            loai_nhac=data.get("loai_nhac", "App"),
            thoi_gian_nhac=data.get("thoi_gian_nhac"),
            lap_lai=data.get("lap_lai", "Không"),
            noi_dung=data.get("noi_dung", ""),
            ref_type=data.get("ref_type", "task"),
            ref_id=data.get("ref_id")
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        return reminder

    @staticmethod
    def delete_reminder(db: Session, user_id: str, reminder_id: int):
        reminder = db.query(PersonalReminder).filter(PersonalReminder.id == reminder_id, PersonalReminder.user_id == user_id).first()
        if not reminder:
            return False
        db.delete(reminder)
        db.commit()
        return True

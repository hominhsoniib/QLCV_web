from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Date
from database.connection import Base
import datetime

class Employee(Base):
    __tablename__ = "employees"
    
    ma_nv = Column(String, primary_key=True, index=True)
    ten_nv = Column(String, nullable=False)
    mat_khau = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    quyen = Column(String, default="USER") # ADMIN, MANAGER, USER
    chuc_danh = Column(String, nullable=True)
    chuc_vu = Column(String, nullable=True)
    phong_ban = Column(String, nullable=True)
    nguoi_ql = Column(String, nullable=True)

class Department(Base):
    __tablename__ = "departments"
    
    ma_bp = Column(String, primary_key=True, index=True)
    ten_bp = Column(String, nullable=False)
    khoi = Column(String, nullable=True) # Maps to Khoi or KhoiPhuTrach
    chuc_nang = Column(Text, default="")
    nhiem_vu = Column(Text, default="")
    quyen_han = Column(Text, default="")
    kpi_chinh = Column(Text, default="")
    kpi_phu = Column(Text, default="")

class Task(Base):
    __tablename__ = "tasks"
    
    id_phan_cong = Column(String, primary_key=True, index=True) # ID_PhanCong
    ma_cv = Column(String, index=True) # MaCV
    ten_cv = Column(String, nullable=False) # TenCV
    nguoi_giao = Column(String, nullable=False) # NguoiGiao
    nguoi_nhan = Column(String, nullable=False) # NguoiNhan
    ngay_bd = Column(String, nullable=True) # NgayBD (kept as String to preserve original formats)
    ngay_kt = Column(String, nullable=True) # NgayKT
    phan_tram_ht = Column(Integer, default=0) # %HT (mapped to Integer 0-100)
    tinh_trang = Column(String, default="Chưa bắt đầu") # TinhTrang
    nhat_ky_bao_cao = Column(Text, default="") # VuongMac / NHAT_KY_BAO_CAO (Column J)
    y_kien_cap_tren = Column(Text, default="") # YkCapTren (Column K)
    so_lan_bao_cao = Column(Integer, default=0) # VaiTro / SO_LAN_BAO_CAO (Column L)
    thoi_gian_xem_cuoi = Column(String, nullable=True) # ThoiGianXemCuoi (Column M)
    noi_dung_nhac_nho = Column(Text, default="") # NoiDungNhacNho (Column N)
    so_lan_nhac = Column(Integer, default=0) # SoLanNhac (Column O)
    file_giao_viec = Column(String, nullable=True) # File_GiaoViec (Column P)
    file_bao_cao = Column(String, nullable=True) # File_BaoCao (Column Q)
    nguoi_phoi_hop = Column(String, nullable=True) # NguoiPhoiHop (Column R, CC list)

class Document(Base):
    __tablename__ = "documents"
    
    ma_tl = Column(String, primary_key=True, index=True)
    ten_tl = Column(String, nullable=False)
    loai = Column(String, nullable=False) # PhanLoai
    ngay_cap_nhat = Column(String, nullable=True)
    link_file = Column(String, nullable=True) # DuongDan / LinkFile
    phong_ban = Column(String, nullable=True)
    mo_ta = Column(Text, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(String, nullable=True)
    action = Column(String, nullable=False)
    status = Column(String, nullable=True)

class PersonalTask(Base):
    __tablename__ = "personal_tasks"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    ten_cv = Column(String, nullable=False)
    mo_ta = Column(Text, default="")
    loai_cv = Column(String, default="Cá nhân") # Cá nhân / Gia đình / Công tác / Du lịch / Học tập
    muc_do_uu_tien = Column(String, default="Trung bình") # Cao / Trung bình / Thấp
    ngay_bd = Column(String, nullable=True) # YYYY-MM-DD HH:MM
    ngay_kt = Column(String, nullable=True) # YYYY-MM-DD HH:MM
    tinh_trang = Column(String, default="Chưa thực hiện") # Chưa thực hiện / Đang thực hiện / Hoàn thành / Hoãn
    tien_do = Column(Integer, default=0) # 0-100
    nguoi_lien_quan = Column(String, default="")
    file_dinh_kem = Column(String, default="")
    ghi_chu = Column(Text, default="")
    co_nhac_nho = Column(Integer, default=0) # 0 = No, 1 = Yes
    ngay_gan_tuan = Column(String, default="") # e.g. "Thu 2", "Thu 3" for Weekly Planner
    tuan_ke_hoach = Column(String, default="") # e.g. "2026-W26" for Weekly Planner

class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    tuan = Column(String, nullable=False) # e.g. "2026-W26"
    muc_tieu_tuan = Column(Text, default="")
    tong_gio_du_kien = Column(Float, default=0.0)
    tong_gio_thuc_te = Column(Float, default=0.0)

class PersonalCalendar(Base):
    __tablename__ = "personal_calendar"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    tieu_de = Column(String, nullable=False)
    loai_lich = Column(String, default="Công việc") # Công việc / Công tác / Du lịch / Sự kiện / Khám bệnh / Việc gia đình / Học tập / Thanh toán hóa đơn
    ngay_gio_bd = Column(String, nullable=True) # YYYY-MM-DD HH:MM
    ngay_gio_kt = Column(String, nullable=True)
    dia_diem = Column(String, default="")
    nguoi_tham_gia = Column(String, default="")
    ghi_chu = Column(Text, default="")
    nhac_nho = Column(String, default="Không") # e.g. "Trước 15 phút"

class BusinessTrip(Base):
    __tablename__ = "business_trips"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    ten_chuyen_di = Column(String, nullable=False)
    ngay_bd = Column(String, nullable=True)
    ngay_kt = Column(String, nullable=True)
    lich_trinh_json = Column(Text, default="[]") # JSON list of itinerary items
    chi_phi_json = Column(Text, default="[]") # JSON list of expenses
    trang_thai = Column(String, default="Lên kế hoạch") # Lên kế hoạch / Đang đi / Hoàn thành / Hủy
    dia_diem = Column(String, default="")
    phuong_tien = Column(String, default="")
    khach_san = Column(String, default="")
    chi_phi_du_kien = Column(Float, default=0.0)
    chi_phi_thuc_te = Column(Float, default=0.0)
    cong_viec_json = Column(Text, default="[]")

class TravelTrip(Base):
    __tablename__ = "travel_trips"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    ten_chuyen_di = Column(String, nullable=False)
    diem_den = Column(String, default="")
    ngay_di = Column(String, nullable=True)
    ngay_ve = Column(String, nullable=True)
    ngan_sach = Column(Float, default=0.0)
    nguoi_di_cung = Column(String, default="")
    checklist_json = Column(Text, default="[]") # JSON checklist

class PersonalGoal(Base):
    __tablename__ = "personal_goals"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    ten_muc_tieu = Column(String, nullable=False)
    loai_muc_tieu = Column(String, default="Tháng") # Năm / Quý / Tháng / Tuần
    mo_ta = Column(Text, default="")
    ngay_bd = Column(String, nullable=True)
    ngay_kt = Column(String, nullable=True)
    kpi = Column(String, default="")
    tien_do = Column(Integer, default=0) # 0-100
    trang_thai = Column(String, default="Đang thực hiện") # Đang thực hiện / Hoàn thành / Tạm dừng

class PersonalReminder(Base):
    __tablename__ = "personal_reminders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    loai_nhac = Column(String, default="App") # App / Email / SMS / Zalo / Telegram
    thoi_gian_nhac = Column(String, nullable=True) # YYYY-MM-DD HH:MM
    lap_lai = Column(String, default="Không") # Không / Hàng ngày / Hàng tuần / Hàng tháng
    noi_dung = Column(Text, default="")
    ref_type = Column(String, default="task") # task / calendar / trip
    ref_id = Column(Integer, nullable=True)

class DailyDiary(Base):
    __tablename__ = "daily_diaries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    ngay = Column(String, nullable=False) # YYYY-MM-DD
    tieu_de = Column(String, nullable=False)
    noi_dung = Column(Text, default="")
    tam_trang = Column(String, default="") # Mood / Notes

class PersonalExpense(Base):
    __tablename__ = "personal_expenses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    ngay = Column(String, nullable=False) # YYYY-MM-DD
    khoan_chi = Column(String, nullable=False)
    so_tien = Column(Float, default=0.0)
    danh_muc = Column(String, default="Khác") # Ăn uống / Di chuyển / Mua sắm / Giải trí / Khác
    ghi_chu = Column(Text, default="")

class HealthLog(Base):
    __tablename__ = "health_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    ngay = Column(String, nullable=False) # YYYY-MM-DD
    huyet_ap = Column(String, default="") # e.g. "120/80"
    can_nang = Column(Float, default=0.0) # kg
    tinh_trang_suc_khoe = Column(Text, default="")
    ghi_chu = Column(Text, default="")

class AIConfig(Base):
    __tablename__ = "ai_configs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String, default="gemini") # "gemini", "claude", or "none"
    gemini_api_key = Column(String, nullable=True)
    gemini_model = Column(String, default="gemini-1.5-flash")
    claude_api_key = Column(String, nullable=True)
    claude_model = Column(String, default="claude-3-5-sonnet-20241022")

class Process(Base):
    __tablename__ = "processes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dept_code = Column(String, nullable=False, index=True)
    code = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    objective = Column(Text, default="")
    scope = Column(Text, default="")
    flowchart_mermaid = Column(Text, default="")
    checklist = Column(Text, default="[]")  # JSON list
    kpi_suggestions = Column(Text, default="[]")  # JSON list
    status = Column(String, default="draft")
    version = Column(Integer, default=1)

class ProcessStep(Base):
    __tablename__ = "process_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    process_id = Column(Integer, nullable=False, index=True)
    step_no = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=True)
    input = Column(Text, nullable=True)
    output = Column(Text, nullable=True)
    sla = Column(String, nullable=True)

class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ma_nv = Column(String, nullable=True, index=True)
    chuc_danh = Column(String, nullable=True, index=True)
    objective = Column(Text, default="")
    responsibilities = Column(Text, default="[]")  # JSON list
    authority = Column(Text, default="[]")  # JSON list
    kpi = Column(Text, default="[]")  # JSON list
    competencies = Column(Text, default="[]")  # JSON list
    reports_to = Column(String, nullable=True)



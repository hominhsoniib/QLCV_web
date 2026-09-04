from sqlalchemy.orm import Session
from models.models import Task, Employee
import datetime

class TaskService:
    @staticmethod
    def get_index_init_data(db: Session, ma_nv: str, role: str):
        """Retrieves and formats all tasks visible to the user.
        Admin/CEO see all tasks, Managers/Users see tasks they assigned, are assigned to, or are CC'd in.
        """
        ma_nv_upper = str(ma_nv or "").strip().upper()
        is_super_admin = (ma_nv_upper == "ADMIN")
        
        query = db.query(Task)
        if not is_super_admin:
            query = query.filter(
                (Task.nguoi_giao == ma_nv_upper) | 
                (Task.nguoi_nhan == ma_nv_upper)
            )
            
        tasks = query.all()
        results = []
        
        for t in tasks:
            # Calculate report count based on 'NV BÁO CÁO' occurrences in the diary
            diary = t.nhat_ky_bao_cao or ""
            calculated_reports = diary.count("NV BÁO CÁO")
            
            task_dict = {
                "idPhanCong": t.id_phan_cong,
                "maCV": t.ma_cv,
                "tenCV": t.ten_cv,
                "nguoiGiao": t.nguoi_giao,
                "nguoiNhan": t.nguoi_nhan,
                "ngayBD": t.ngay_bd,
                "ngayKT": t.ngay_kt,
                "tienDo": t.phan_tram_ht or 0,
                "status": t.tinh_trang,
                "link": t.file_giao_viec or "",
                "phoiHop": t.nguoi_phoi_hop or "",
                "nhatKyBaoCao": t.nhat_ky_bao_cao or "",
                "noiDungNhacNho": t.noi_dung_nhac_nho or "",
                "soLanNhac": t.so_lan_nhac or 0,
                "soLanBaoCao": max(t.so_lan_bao_cao or 0, calculated_reports)
            }
            results.append(task_dict)
            
        # Reverse tasks list to match Apps Script (newest on top)
        results.reverse()
        return {"success": True, "data": results}

    @staticmethod
    def get_task_by_id(db: Session, task_id: str):
        """Retrieves details of a single task by its id_phan_cong."""
        t = db.query(Task).filter(Task.id_phan_cong == task_id).first()
        if not t:
            return None
            
        diary = t.nhat_ky_bao_cao or ""
        calculated_reports = diary.count("NV BÁO CÁO")
        
        return {
            "idPhanCong": t.id_phan_cong,
            "maCV": t.ma_cv,
            "tenCV": t.ten_cv,
            "nguoiGiao": t.nguoi_giao,
            "nguoiNhan": t.nguoi_nhan,
            "ngayKT": t.ngay_kt,
            "tienDo": t.phan_tram_ht or 0,
            "lichSuNhac": t.noi_dung_nhac_nho or "",
            "soLanNhac": t.so_lan_nhac or 0,
            "lichSuBaoCao": t.nhat_ky_bao_cao or "",
            "soLanBaoCao": max(t.so_lan_bao_cao or 0, calculated_reports),
            "link": t.file_giao_viec or "",
            "file_bao_cao": t.file_bao_cao or "",
            "phoiHop": t.nguoi_phoi_hop or ""
        }

    @staticmethod
    def get_suggested_ma_cv(db: Session, prefix: str):
        """Generates the next task code (MaCV) for a given employee prefix by scanning database.
        E.g. If CEO has 'CEO.001', 'CEO002', 'CEO.008', returns 'CEO.009'
        """
        import re
        raw = str(prefix or "").strip()
        if "-" in raw:
            raw = raw.split("-")[0].strip()
        prefix_clean = raw.upper()
        
        if not prefix_clean:
            prefix_clean = "CEO"

        # Search for tasks where nguoi_giao matches or ma_cv / id_phan_cong starts with prefix
        tasks = db.query(Task).filter(
            (Task.nguoi_giao == prefix_clean) |
            (Task.ma_cv.like(f"{prefix_clean}%")) |
            (Task.id_phan_cong.like(f"%{prefix_clean}%"))
        ).all()
        
        max_num = 0
        pattern = re.compile(rf"{re.escape(prefix_clean)}[\._-]?(\d+)", re.IGNORECASE)
        
        for t in tasks:
            for val in [t.ma_cv, t.id_phan_cong]:
                if not val:
                    continue
                m = pattern.search(val)
                if m:
                    try:
                        num = int(m.group(1))
                        if num > max_num:
                            max_num = num
                    except ValueError:
                        pass

        next_num = max_num + 1
        return f"{prefix_clean}.{str(next_num).zfill(3)}"

    @staticmethod
    def save_task_data(db: Session, obj: dict):
        """Creates a new task or updates an existing one."""
        id_pc = str(obj.get("idPhanCong", "")).strip()
        
        # Check if existing task in database
        existing_task = db.query(Task).filter(Task.id_phan_cong == id_pc).first() if id_pc and id_pc != "TỰ ĐỘNG" else None
        is_new = existing_task is None
        
        # Parse progress
        try:
            progress = int(float(obj.get("tienDo", 0)))
        except ValueError:
            progress = 0
            
        prefix = str(obj.get("nguoiGiao", "")).strip().upper()
        if "-" in prefix:
            prefix = prefix.split("-")[0].strip()

        if is_new:
            # It's a new task, calculate max MaCV from database
            ma_cv = str(obj.get("maCV", "")).strip()
            if not ma_cv or ma_cv == "TỰ ĐỘNG" or ma_cv == id_pc:
                ma_cv = TaskService.get_suggested_ma_cv(db, prefix)
            if not id_pc or id_pc == "TỰ ĐỘNG":
                id_pc = ma_cv
            
            task = Task(
                id_phan_cong=id_pc,
                ma_cv=ma_cv,
                ten_cv=clean_string(obj.get("tenCV")),
                nguoi_giao=prefix,
                nguoi_nhan=str(obj.get("nguoiNhan", "")).strip().upper(),
                ngay_bd=obj.get("ngayBD"),
                ngay_kt=obj.get("ngayKT"),
                phan_tram_ht=progress,
                tinh_trang=obj.get("status", "Chưa bắt đầu"),
                file_giao_viec=obj.get("link", ""),
                nguoi_phoi_hop=obj.get("phoiHop", ""),
                nhat_ky_bao_cao=obj.get("nhatKyBaoCao", ""),
                noi_dung_nhac_nho=obj.get("noiDungNhacNho", "")
            )
            db.add(task)
            db.commit()
            return {"success": True, "message": f"Thêm mới thành công công việc [{ma_cv}]!"}
        else:
            # Updating an existing task
            task = existing_task
            task.ten_cv = clean_string(obj.get("tenCV", task.ten_cv))
            task.nguoi_giao = prefix if prefix else task.nguoi_giao
            task.nguoi_nhan = str(obj.get("nguoiNhan", task.nguoi_nhan)).strip().upper()
            task.ngay_bd = obj.get("ngayBD", task.ngay_bd)
            task.ngay_kt = obj.get("ngayKT", task.ngay_kt)
            task.phan_tram_ht = progress
            task.tinh_trang = obj.get("status", task.tinh_trang)
            task.file_giao_viec = obj.get("link", task.file_giao_viec)
            task.nguoi_phoi_hop = obj.get("phoiHop", task.nguoi_phoi_hop)
            
            # Keep previous logs if form does not supply them
            if obj.get("nhatKyBaoCao"):
                task.nhat_ky_bao_cao = obj.get("nhatKyBaoCao")
            if obj.get("noiDungNhacNho"):
                task.noi_dung_nhac_nho = obj.get("noiDungNhacNho")
                
            message = "Cập nhật thành công!"
            
        db.commit()
        return {"success": True, "message": message, "id": id_pc}

    @staticmethod
    def update_bao_cao(db: Session, obj: dict):
        """Logs a report, prepending comments to nhat_ky_bao_cao and updating progress."""
        task_id = str(obj.get("id", "")).strip()
        task = db.query(Task).filter(Task.id_phan_cong == task_id).first()
        if not task:
            return {"success": False, "message": f"🚨 Không tìm thấy ID công việc: {task_id}"}
            
        # 1. Format report string
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        new_entry = f"[{now_str}] NV BÁO CÁO: Đạt {obj.get('tienDo')}% - {obj.get('status')}\n--\n{obj.get('giaiTrinh')}\n\n"
        
        # 2. Prepend to history
        old_history = task.nhat_ky_bao_cao or ""
        task.nhat_ky_bao_cao = new_entry + old_history
        
        # 3. Update report count
        current_count = task.so_lan_bao_cao or 0
        task.so_lan_bao_cao = current_count + 1
        
        # 4. Update progress and status
        try:
            task.phan_tram_ht = int(float(obj.get("tienDo", 0)))
        except ValueError:
            pass
        task.tinh_trang = obj.get("status")
        
        # 5. Save attachment link if provided
        if obj.get("linkBaoCao"):
            task.file_bao_cao = obj.get("linkBaoCao")
            
        db.commit()
        return {"success": True, "message": f"✅ Báo cáo thành công! Số lượt đã tăng lên {current_count + 1}"}

    @staticmethod
    def update_nhac_nho(db: Session, task_id: str, message: str):
        """Logs manager directions, prepending comments and incrementing reminder count."""
        task_id_clean = str(task_id or "").strip()
        task = db.query(Task).filter(Task.id_phan_cong == task_id_clean).first()
        if not task:
            return {"success": False, "message": f"🚨 Không tìm thấy ID công việc: {task_id_clean}"}
            
        # 1. Format reminder entry
        now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        new_entry = f"[{now_str}] SEP CHỈ ĐẠO: {message}\n--\n"
        
        # 2. Prepend to history
        old_history = task.noi_dung_nhac_nho or ""
        task.noi_dung_nhac_nho = new_entry + old_history
        
        # 3. Increment reminder count
        current_count = task.so_lan_nhac or 0
        task.so_lan_nhac = current_count + 1
        
        db.commit()
        return {"success": True, "message": f"✅ Đã phát lệnh chỉ đạo thành công! Số lần nhắc: {current_count + 1}"}

    @staticmethod
    def save_forward(db: Session, payload: dict):
        """Delegates/Forwards a task. Marks parent as 'Đã ủy quyền' and spawns child task."""
        parent_id = str(payload.get("idPhanCongGoc", "")).strip()
        if not parent_id:
            return {"success": False, "message": "🚨 Lỗi: Thiếu ID gốc!"}
            
        parent_task = db.query(Task).filter(Task.id_phan_cong == parent_id).first()
        if not parent_task:
            return {"success": False, "message": "🚨 Lỗi: Không tìm thấy công việc gốc!"}
            
        # Generate new MaCV and child task ID
        receiver = str(payload.get("nguoiNhanUyQuyen", "")).strip().upper()
        new_ma_cv = TaskService.get_suggested_ma_cv(db, receiver)
        child_id = f"{parent_id}_{new_ma_cv}"
        
        # Create child task
        child_task = Task(
            id_phan_cong=child_id,
            ma_cv=new_ma_cv,
            ten_cv=payload.get("tenCV", f"Ủy quyền: {parent_task.ten_cv}"),
            nguoi_giao=str(payload.get("nguoiGiao", parent_task.nguoi_nhan)).strip().upper(),
            nguoi_nhan=receiver,
            ngay_bd=datetime.date.today().strftime("%Y-%m-%d"),
            ngay_kt=payload.get("ngayKT", parent_task.ngay_kt),
            phan_tram_ht=0,
            tinh_trang="Chưa bắt đầu",
            file_giao_viec=parent_task.file_giao_viec,
            nguoi_phoi_hop=payload.get("phoiHopMoi", ""),
            y_kien_cap_tren=payload.get("txtNote", "") # "Chỉ dẫn: ..."
        )
        
        db.add(child_task)
        
        # Mark parent as delegated/forwarded
        parent_task.tinh_trang = "Đã ủy quyền"
        
        db.commit()
        return {"success": True, "message": "✅ Xác nhận Ủy quyền thành công!", "id": child_id}

def clean_string(val):
    if val is None:
        return ""
    return str(val).strip()

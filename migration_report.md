# Báo Cáo Chuyển Đổi Hệ Thống (Migration Report)

Báo cáo chi tiết quá trình chuyển đổi phần mềm Quản Lý Công Việc (QLCV) từ Google Apps Script (GAS) sang Python Web Application (FastAPI).

---

## 1. Bản Đồ Ánh Xạ File (File Mapping Map)

Dưới đây là sơ đồ chi tiết ánh xạ từ hệ thống cũ sang kiến trúc mới:

### Backend Mapping
| Apps Script File (Old) | Python Path (New) | Vai Trò Kiến Trúc |
| :--- | :--- | :--- |
| `00_Config.gs` | `config.py` | Centralized Configurations, constants, environment settings |
| `01_Code.gs` | `app.py` & routers | Core FastAPI engine, startup initialization & router bindings |
| `02_AuthService.gs` | `services/auth_service.py` | Login check, signed cookie context, password change, stats |
| `03_UIService.gs` | Routed automatically | Handled natively by FastAPI + Jinja2 templates |
| `04_TaskService.gs` | `services/task_service.py` | Task core CRUD, status reporting, managers reminding, delegation |
| `05.DriveService.gs` (CSS) | `static/css/styles.css` | Global custom visual design system & glassmorphism variables |
| `06.DepartmentService.gs` | `services/department_service.py` | [NEW] Full implementation of Department CRUD |
| `07.EmployeeService.gs` | `services/employee_service.py` | Employee profile management, CRUD, dropdown queries |
| `08.SheetService.gs` | `services/sheet_service.py` | Seeding script importing raw data from `seed.xlsx` to SQLite |

### Frontend Template Mapping
| Apps Script HTML (Old) | Jinja2 Template (New) | Trạng Thái / Nâng Cấp |
| :--- | :--- | :--- |
| `FormLogin.html` | `templates/login.html` | Thiết kế Glassmorphism, AJAX Form data login |
| `MainForm.html` | `templates/dashboard.html` | Central control menu, stats counters with animate-up |
| `FormIndex.html` | `templates/tasks/index.html` | Bảng quản lý chung, hỗ trợ upload cục bộ hoặc Drive |
| `FormBaoCao.html` | `templates/tasks/report.html` | Báo cáo tiến độ và đính kèm file minh chứng |
| `FormForward.html` | `templates/tasks/forward.html` | Chuyển tiếp việc cấp dưới, auto suggest mã số công việc |
| `FormDM_BOPHAN.html` | `templates/master/departments.html` | CRUD danh mục cơ cấu phòng ban |
| `FormDM_NVIEN.html` | `templates/master/employees.html` | [NEW] Tự thiết kế giao diện CRUD Nhân sự hoàn chỉnh |
| `FormDMTaiLieu.html` | `templates/documents/index.html` | CRUD tài liệu, tự sinh mã theo loại (BM01, QT02...) |
| `FormKhoTaiLieu.html` | `templates/documents/repository.html` | Thư viện tài nguyên chung, bộ lọc nhanh theo mã đầu mục |
| `FormChangePass.html` | `templates/auth/change_password.html` | Giao diện đổi mật khẩu & logout tự động |
| --- | `templates/tasks/remind.html` | [NEW] Ý kiến chỉ đạo cấp trên (cột N & O) |
| --- | `templates/tasks/personal.html` | [NEW] Bộ lọc kế hoạch cá nhân của riêng user đăng nhập |
| --- | `templates/tasks/overdue.html` | [NEW] Radar cảnh báo sớm các rủi ro quá hạn |
| --- | `templates/tasks/report_center.html`| [NEW] Biểu đồ phân tích tỷ lệ hoàn thành & chậm hạn |

---

## 2. Kiến Trúc Cơ Sở Dữ Liệu (Database Layer Translation)

Hệ thống cũ lưu trữ dữ liệu dạng phẳng trên các tab Google Sheets. Hệ thống mới chuyển đổi sang cơ sở dữ liệu quan hệ SQLite quản lý bởi SQLAlchemy ORM.

### Bảng Nhân Sự (employees)
Lưu trữ thông tin tài khoản và cấu trúc sơ đồ báo cáo.
- `ma_nv` (Khóa chính) -> `MaNV`
- `ten_nv` -> `TenNV`
- `mat_khau` -> `MatKhau`
- `quyen` -> `Quyen` (ADMIN/MANAGER/USER)
- `chuc_danh` -> `Chucdanh`
- `chuc_vu` -> `Chucvu`
- `phong_ban` -> `PhongBan`
- `nguoi_ql` -> `NguoiQL`

### Bảng Cơ Cấu Tổ Chức (departments)
- `ma_bp` (Khóa chính) -> `MaBP`
- `ten_bp` -> `TenBP`
- `khoi` -> `KhoiPhuTrach` / `Khoi`

### Bảng Công Việc (tasks)
Thiết lập 18 cột theo đúng thiết kế cơ bản:
- `id_phan_cong` (Khóa chính) -> `ID_PhanCong`
- `ma_cv` -> `MaCV`
- `ten_cv` -> `TenCV`
- `nguoi_giao` -> `NguoiGiao`
- `nguoi_nhan` -> `NguoiNhan`
- `ngay_bd` -> `NgayBD` (Chuyển sang định dạng chuẩn YYYY-MM-DD để tương thích input date)
- `ngay_kt` -> `NgayKT` (YYYY-MM-DD)
- `phan_tram_ht` -> `%HT` (Lưu dưới dạng số nguyên 0-100)
- `tinh_trang` -> `TinhTrang`
- `nhat_ky_bao_cao` -> `VuongMac` / `NHAT_KY_BAO_CAO`
- `y_kien_cap_tren` -> `YkCapTren`
- `so_lan_bao_cao` -> `VaiTro` / `SO_LAN_BAO_CAO`
- `thoi_gian_xem_cuoi` -> `ThoiGianXemCuoi`
- `noi_dung_nhac_nho` -> `NoiDungNhacNho`
- `so_lan_nhac` -> `SoLanNhac`
- `file_giao_viec` -> `File_GiaoViec`
- `file_bao_cao` -> `File_BaoCao`
- `nguoi_phoi_hop` -> `NguoiPhoiHop` (Danh sách CC cách nhau bởi dấu phẩy)

### Bảng Thư Mục Tài Liệu (documents)
- `ma_tl` (Khóa chính) -> `MaTL`
- `ten_tl` -> `TenTL`
- `loai` -> `PhanLoai`
- `ngay_cap_nhat` -> `NgayCapNhat`
- `link_file` -> `DuongDan`

---

## 3. Chuyển Đổi `google.script.run` sang REST API

Tất cả các lệnh RPC client-side gọi bất đồng bộ lên Apps Script đã được chuyển đổi sang chuẩn AJAX Fetch API tương ứng với các HTTP methods của FastAPI:

| Apps Script Function | HTTP Method | REST API Endpoint |
| :--- | :--- | :--- |
| `Auth_checkLogin(u, p)` | POST (Form) | `/api/auth/login` |
| `processChangePassword(payload)` | POST (JSON) | `/api/auth/change-password` |
| `Auth_getDashboardStats()` | GET | `/api/dashboard/stats` |
| `Task_getIndexInitData()` | GET | `/api/tasks` |
| `Task_saveTaskData(payload)` | POST (JSON) | `/api/tasks` |
| `Task_getTaskById(id)` | GET | `/api/tasks/{task_id}` |
| `Task_updateBaoCao(payload)` | POST (JSON) | `/api/tasks/{task_id}/report` |
| `Task_updateNhacNho(id, msg)` | POST (JSON) | `/api/tasks/{task_id}/remind` |
| `Task_saveForward(payload)` | POST (JSON) | `/api/tasks/forward` |
| `getDepartmentManagementData()` | GET | `/api/departments` |
| `addDepartment(payload)` | POST (JSON) | `/api/departments` |
| `updateDepartment(payload)` | POST (JSON) | `/api/departments/update` |
| `deleteDepartment(ma)` | DELETE | `/api/departments/{ma_bp}` |
| `getEmployeeManagementData()` | GET | `/api/employees` |
| `addEmployee(payload)` | POST (JSON) | `/api/employees` |
| `updateEmployee(payload)` | POST (JSON) | `/api/employees/update` |
| `getDocumentManagementData()` | GET | `/api/documents` |
| `getNextDocCode(loai)` | GET | `/api/documents/next-code` |

---

## 4. Những Nâng Cấp Vượt Trội Sau Khi Migration

1. **Hiệu năng vượt trội:** Không còn bị ảnh hưởng bởi giới hạn thời gian chạy 6 phút (Quota limit) của Google Apps Script hay độ trễ truy xuất bảng tính lớn.
2. **Khả năng chạy offline:** Hệ thống có thể hoạt động hoàn toàn độc lập mà không cần kết nối Google Cloud, nhờ lưu trữ CSDL SQLite cục bộ và lưu trữ tệp tin tại `/static/uploads`.
3. **Mở rộng dễ dàng:** FastAPI và SQLAlchemy cho phép cấu hình kết nối sang các CSDL doanh nghiệp lớn (PostgreSQL, MySQL, SQL Server) chỉ bằng một dòng thay đổi tại tệp `.env`.
4. **Bảo mật tối cao:** Mật khẩu và thông tin đăng nhập được kiểm soát thông qua cơ chế Signed Cookies (`itsdangerous`), chống giả mạo thông tin phiên từ trình duyệt.

# SPEC KỸ THUẬT: Thêm trường Email — AMS PRO 5.0 (Quản trị Danh mục Nhân sự)

> Tài liệu này dùng để đưa trực tiếp cho AI code editor (Cursor / Antigravity / Claude Code) thực thi.
> Module: `master/employees`
> Stack giả định: PostgreSQL + NestJS (TypeORM) + Next.js form — điều chỉnh nếu stack thực tế khác (Google Apps Script / Sheet DB thì xem mục 5).

---

## 1. SQL MIGRATION (PostgreSQL)

### 1.1. Migration UP — thêm cột email

```sql
-- Migration: add_email_to_employees
-- Mục tiêu: thêm cột email, cho phép NULL tạm thời, unique khi có giá trị

BEGIN;

ALTER TABLE employees
  ADD COLUMN email VARCHAR(255) NULL;

-- Unique index cho phép nhiều dòng NULL (Postgres mặc định coi NULL != NULL)
CREATE UNIQUE INDEX idx_employees_email_unique
  ON employees (LOWER(email))
  WHERE email IS NOT NULL;

-- Cờ xác thực email (dùng cho Phase 4 - reset password / verify)
ALTER TABLE employees
  ADD COLUMN email_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- Timestamp để tracking khi nào email được xác thực
ALTER TABLE employees
  ADD COLUMN email_verified_at TIMESTAMP NULL;

COMMENT ON COLUMN employees.email IS 'Email dùng để đăng nhập (song song với mã NV), lowercase khi lưu';
COMMENT ON COLUMN employees.email_verified IS 'Trạng thái xác thực email, mặc định false';

COMMIT;
```

### 1.2. Migration DOWN — rollback

```sql
BEGIN;

DROP INDEX IF EXISTS idx_employees_email_unique;
ALTER TABLE employees DROP COLUMN IF EXISTS email_verified_at;
ALTER TABLE employees DROP COLUMN IF EXISTS email_verified;
ALTER TABLE employees DROP COLUMN IF EXISTS email;

COMMIT;
```

### 1.3. Validate trước khi chạy migration (chạy thử trên staging trước)

```sql
-- Kiểm tra có email trùng lặp sẵn trong dữ liệu cũ hay không (nếu import từ nguồn khác)
SELECT LOWER(email) AS email_lower, COUNT(*)
FROM employees
WHERE email IS NOT NULL
GROUP BY LOWER(email)
HAVING COUNT(*) > 1;
```

### 1.4. TypeORM Entity — bổ sung field

```typescript
// employee.entity.ts
@Column({ type: 'varchar', length: 255, nullable: true, unique: false })
email: string | null;

@Column({ type: 'boolean', default: false })
emailVerified: boolean;

@Column({ type: 'timestamp', nullable: true })
emailVerifiedAt: Date | null;
```

> Lưu ý: unique constraint xử lý bằng partial index ở DB (mục 1.1), KHÔNG dùng `@Column({ unique: true })` trực tiếp vì TypeORM sẽ tạo unique index thường (không cho phép nhiều NULL trên một số DB config — cần kiểm tra kỹ nếu dùng synchronize).

### 1.5. DTO Validation (NestJS class-validator)

```typescript
// create-employee.dto.ts / update-employee.dto.ts
import { IsEmail, IsOptional } from 'class-validator';

@IsOptional()
@IsEmail({}, { message: 'Email không đúng định dạng' })
email?: string;
```

### 1.6. Service-layer check trùng email (trước khi insert/update)

```typescript
async validateEmailUnique(email: string, excludeId?: string) {
  if (!email) return;
  const existing = await this.employeeRepo.findOne({
    where: { email: email.toLowerCase() },
  });
  if (existing && existing.id !== excludeId) {
    throw new BadRequestException('Email đã được sử dụng bởi nhân viên khác');
  }
}
```

---

## 2. CẤU TRÚC FORM FIELD (UI)

### 2.1. Field mới

| Field name (name/id) | Label hiển thị | Type | Required | Placeholder | Validate |
|---|---|---|---|---|---|
| `email` | EMAIL | `input type="email"` | Không bắt buộc (Phase 1-3) → Bắt buộc (Phase 4) | `VD: nhanvien@badenfarm.com.vn` | Regex email chuẩn, lowercase trước khi lưu, check unique khi blur/submit |

### 2.2. Vị trí trong layout hiện tại (theo ảnh chụp form gốc)

**Layout cũ (4 field/hàng):**
```
Hàng 1: MÃ NHÂN VIÊN | HỌ VÀ TÊN | MẬT KHẨU | PHÂN QUYỀN TRUY CẬP
Hàng 2: CHỨC DANH | CHỨC VỤ | PHÒNG BAN BỘ PHẬN | NGƯỜI QUẢN LÝ
```

**Layout mới (đề xuất, thêm EMAIL):**
```
Hàng 1: MÃ NHÂN VIÊN | HỌ VÀ TÊN | EMAIL | PHÂN QUYỀN TRUY CẬP
Hàng 2: MẬT KHẨU | CHỨC DANH | CHỨC VỤ | PHÒNG BAN BỘ PHẬN
Hàng 3: NGƯỜI QUẢN LÝ | (để trống hoặc field tương lai)
```

Grid class (nếu dùng TailwindCSS, giữ pattern hiện tại `grid-cols-4`):
```jsx
<div className="grid grid-cols-1 md:grid-cols-4 gap-4">
  {/* Hàng 1 */}
  <FormField label="MÃ NHÂN VIÊN" name="employeeCode" placeholder="VD: CEO" />
  <FormField label="HỌ VÀ TÊN" name="fullName" placeholder="Nhập tên nhân viên..." />
  <FormField
    label="EMAIL"
    name="email"
    type="email"
    placeholder="VD: nhanvien@badenfarm.com.vn"
  />
  <SelectField label="PHÂN QUYỀN TRUY CẬP" name="role" options={roleOptions} />

  {/* Hàng 2 */}
  <FormField label="MẬT KHẨU" name="password" type="password" placeholder="Mặc định: 123456" />
  <FormField label="CHỨC DANH" name="jobTitle" placeholder="VD: Chuyên viên..." />
  <FormField label="CHỨC VỤ" name="position" placeholder="VD: Trưởng phòng..." />
  <SelectField label="PHÒNG BAN BỘ PHẬN" name="departmentId" options={departmentOptions} />

  {/* Hàng 3 */}
  <SelectField label="NGƯỜI QUẢN LÝ" name="managerId" options={managerOptions} />
</div>
```

### 2.3. Cập nhật bảng danh sách nhân sự (phía dưới form)

Thêm cột **EMAIL** vào bảng, đặt sau cột "HỌ VÀ TÊN", trước "PHÒNG BAN":

```
MÃ NV | HỌ VÀ TÊN | EMAIL | PHÒNG BAN | PHÂN QUYỀN | CHỨC DANH | NGƯỜI QL
```

Nếu email trống → hiển thị badge cảnh báo nhỏ: `⚠ Chưa có email` (màu vàng/cam), giúp admin dễ rà soát tiến độ Phase 3.

### 2.4. Validate phía frontend (trước khi gọi API)

```typescript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateEmail(value: string): string | null {
  if (!value) return null; // optional trong Phase 1-3
  if (!emailRegex.test(value)) return 'Email không đúng định dạng';
  return null;
}
```

---

## 3. API ENDPOINT — thay đổi cần thiết

| Endpoint | Thay đổi |
|---|---|
| `POST /master/employees` | Thêm `email` vào body, validate DTO, check unique |
| `PUT /master/employees/:id` | Thêm `email` vào body, validate DTO, check unique (exclude chính nó) |
| `GET /master/employees` | Trả thêm field `email`, `emailVerified` trong response |
| `GET /master/employees/missing-email` (mới, optional) | Trả danh sách NV chưa có email — phục vụ Phase 3 rà soát |

---

## 4. PHASE 4 (sau này) — Đăng nhập song song bằng Email hoặc Mã NV

Không triển khai ngay, chỉ ghi chú kiến trúc để AI code editor hiểu hướng tương lai, tránh code sai định hướng:

```typescript
async login(identifier: string, password: string) {
  const isEmail = identifier.includes('@');
  const employee = isEmail
    ? await this.employeeRepo.findOne({ where: { email: identifier.toLowerCase() } })
    : await this.employeeRepo.findOne({ where: { employeeCode: identifier } });

  if (!employee) throw new UnauthorizedException('Tài khoản không tồn tại');
  // ...verify password...
}
```

---

## 5. NẾU BACKEND LÀ GOOGLE APPS SCRIPT + GOOGLE SHEET (không phải Postgres)

Vì Sơn có nhiều dự án chạy trên GAS (NEXUS PRO ERP), nếu `app.badenfarm.com.vn:8081` thực chất là GAS Web App:

1. Thêm cột `Email` vào Sheet `Employees` (ngay sau cột `HoTen`).
2. Cập nhật `EmployeeRepo` (Apps Script service layer) để đọc/ghi thêm field `email`.
3. Thêm validate trùng email trong hàm `validateEmployee_()` trước khi `appendRow`/`updateRow`.
4. Cập nhật HTML form (`employees.html`) theo cấu trúc field ở mục 2.2 — giữ nguyên namespace pattern hiện có của module (nếu theo chuẩn PHIEU_CHI thì dùng prefix tương ứng của module Employees).

> Cho mình biết chính xác stack đang chạy (NestJS+Postgres hay GAS+Sheet) để mình chốt lại đúng 1 bộ migration/code duy nhất, tránh AI code editor chạy nhầm hướng.

---

## 6. CHECKLIST THỰC THI CHO AI CODE EDITOR

- [ ] Chạy migration SQL (mục 1.1) trên môi trường staging trước
- [ ] Kiểm tra dữ liệu trùng lặp (mục 1.3) trước khi apply unique index
- [ ] Cập nhật Entity + DTO (mục 1.4, 1.5)
- [ ] Thêm service check unique email (mục 1.6)
- [ ] Cập nhật API endpoints (mục 3)
- [ ] Cập nhật form UI theo layout mới (mục 2.2)
- [ ] Cập nhật bảng danh sách + badge cảnh báo thiếu email (mục 2.3)
- [ ] Test: thêm mới NV có email, thêm mới NV không email, cập nhật email trùng (phải báo lỗi), cập nhật email hợp lệ
- [ ] Deploy migration production sau khi test staging pass

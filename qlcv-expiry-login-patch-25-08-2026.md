# Ghi chú hệ thống — QLCV_web: bổ sung chặn đăng nhập khi hết hạn — 25/08/2026

> File này ghi lại các lệnh cần chạy trên VPS để bổ sung tính năng chặn đăng nhập
> khi công ty hết hạn sử dụng phần mềm, cho AMS PRO 5.0 / QLCV_web.
> Chạy tuần tự từng khối lệnh, không bỏ bước verify.

---

## 0. Bối cảnh

- App thật: `/root/QLCV_web`, service `nexus-qlcv.service`, port 8081.
- File `start_date`/`expiry_date` đã được khôi phục vào form + DB ngày 24/08/2026
  (sau sự cố ghi đè code cũ), nhưng **logic chặn đăng nhập khi hết hạn thì
  CHƯA từng tồn tại** trong `services/auth_service.py` — xác nhận qua
  `grep -rn expiry_date` không ra kết quả nào trong route xác thực.
- Vị trí chèn: ngay sau khi `password_valid = True` được xác định, trước khi
  trả về session thành công — trong hàm `AuthService.check_login()`.
- Không được chặn tài khoản Master Admin NSX (nhánh xử lý riêng ở phần 1 của
  hàm, không đi qua đoạn code này).

---

## 1. Backup file gốc trước khi sửa

```bash
mkdir -p /root/QLCV_web/_fix_backup_20260825
cp /root/QLCV_web/services/auth_service.py \
   /root/QLCV_web/_fix_backup_20260825/auth_service.py.before
```

---

## 2. Tạo script patch Python (tự kiểm tra MATCH_COUNT trước khi ghi)

```bash
cat > /root/QLCV_web/_patch_expiry_login.py << 'PYEOF'
f = "/root/QLCV_web/services/auth_service.py"
content = open(f, encoding="utf-8").read()

old = (
    "                    if password_valid:\n"
    "                        if not comp_name:"
)

count = content.count(old)
print("MATCH_COUNT:", count)

if count == 1:
    expiry_block = (
        "                    if password_valid:\n"
        "                        # --- Kiểm tra hạn sử dụng phần mềm của công ty ---\n"
        "                        from datetime import datetime as _dt_check\n"
        "                        master_db_lic = MasterSessionLocal()\n"
        "                        try:\n"
        "                            comp_lic = master_db_lic.query(MasterCompany).filter_by(tax_code=company_mst).first()\n"
        "                            if comp_lic and comp_lic.expiry_date:\n"
        "                                today_str = _dt_check.now().strftime(\"%Y-%m-%d\")\n"
        "                                if str(comp_lic.expiry_date).strip() < today_str:\n"
        "                                    return {\n"
        "                                        \"success\": False,\n"
        "                                        \"message\": f\"Tài khoản phần mềm của Quý công ty đã hết hạn sử dụng vào ngày {comp_lic.expiry_date}. Vui lòng liên hệ Nhà sản xuất phần mềm để gia hạn.\"\n"
        "                                    }\n"
        "                        finally:\n"
        "                            master_db_lic.close()\n"
        "\n"
        "                        if not comp_name:"
    )
    content = content.replace(old, expiry_block, 1)
    open(f, "w", encoding="utf-8").write(content)
    print("PATCHED_OK")
else:
    print("SKIP - khong khop dung 1 lan, KHONG ghi file")
PYEOF
```

---

## 3. Chạy script patch

```bash
python3 /root/QLCV_web/_patch_expiry_login.py
```

**Kỳ vọng:** `MATCH_COUNT: 1` và `PATCHED_OK`.
Nếu ra số khác 1 hoặc `SKIP` → **dừng lại**, không đi tiếp, báo lại kết quả
trước khi làm gì thêm (không được đoán mò sửa tay khi script báo không khớp).

---

## 4. Kiểm tra cú pháp Python

```bash
/root/QLCV_web/venv/bin/python3 -m py_compile /root/QLCV_web/services/auth_service.py \
  && echo "COMPILE_OK"
```

Nếu báo lỗi (traceback) → xem lại nội dung file, khôi phục từ backup nếu cần:
```bash
cp /root/QLCV_web/_fix_backup_20260825/auth_service.py.before \
   /root/QLCV_web/services/auth_service.py
```

---

## 5. Xác nhận điểm chạm đã chèn đúng

```bash
grep -n "Kiểm tra hạn sử dụng phần mềm" /root/QLCV_web/services/auth_service.py
grep -c "expiry_date" /root/QLCV_web/services/auth_service.py
```

---

## 6. Restart service thật

```bash
systemctl restart nexus-qlcv.service
sleep 2
systemctl is-active nexus-qlcv.service
systemctl show nexus-qlcv.service -p ActiveEnterTimestamp -p MainPID
```

**Kỳ vọng:** `active`, timestamp vừa restart.

---

## 7. Test round-trip qua API thật (dùng công ty TEST, KHÔNG dùng SAVINA/Phúc An)

### 7.1. Đặt hạn quá khứ cho công ty test `0312345678`

```bash
COOKIE_JAR=/tmp/qlcv_admin_cookies.txt
rm -f $COOKIE_JAR

# Login admin NSX
curl -s -c $COOKIE_JAR -X POST http://127.0.0.1:8081/api/auth/login \
  -d "username=ADMIN&password=Admin@123"

# Set expiry_date về quá khứ cho công ty test
curl -s -b $COOKIE_JAR -X POST http://127.0.0.1:8081/api/companies/update \
  --data-urlencode "tax_code=0312345678" \
  --data-urlencode "code=DEFAULT" \
  --data-urlencode "name=CÔNG TY TNHH GIẢI PHÁP CÔNG NGHIỆP VIỆT" \
  --data-urlencode "expiry_date=2020-01-01"
```

### 7.2. Thử đăng nhập công ty test — kỳ vọng BỊ CHẶN

```bash
curl -s -X POST http://127.0.0.1:8081/api/auth/login \
  -d "tax_code=0312345678&username=<user_that_cua_cong_ty_test>&password=<pass_dung>"
```

**Kỳ vọng:** `{"success": false, "message": "Tài khoản phần mềm ... đã hết hạn ... 2020-01-01 ..."}`

### 7.3. Khôi phục lại `expiry_date` rỗng cho công ty test

```bash
curl -s -b $COOKIE_JAR -X POST http://127.0.0.1:8081/api/companies/update \
  --data-urlencode "tax_code=0312345678" \
  --data-urlencode "code=DEFAULT" \
  --data-urlencode "name=CÔNG TY TNHH GIẢI PHÁP CÔNG NGHIỆP VIỆT" \
  --data-urlencode "expiry_date="
```

---

## 8. Xác nhận SAVINA và Phúc An không bị ảnh hưởng

```bash
curl -s -X POST http://127.0.0.1:8081/api/auth/login \
  -d "tax_code=3901323107&username=hominhsoniib@gmail.com&password=Sonho@123"
```

**Kỳ vọng:** `{"success": true, ...}` — đăng nhập bình thường (vì `expiry_date`
của SAVINA đang đặt tương lai `25/08/2026` trở đi, hoặc rỗng).

Lặp lại tương tự cho Phúc An (MST `0317598974`) nếu có tài khoản test sẵn.

---

## 9. Dọn dẹp file tạm

```bash
rm -f /root/QLCV_web/_patch_expiry_login.py
rm -f /tmp/qlcv_admin_cookies.txt
```

Giữ lại `_fix_backup_20260825/auth_service.py.before` — không xóa, để đối chiếu
nếu cần rollback sau này.

---

## 10. Checklist xác nhận hoàn tất

- [ ] `MATCH_COUNT: 1`, `PATCHED_OK`
- [ ] `COMPILE_OK`, không traceback
- [ ] Service `active` sau restart
- [ ] Công ty test bị chặn đúng khi `expiry_date` quá khứ, đúng thông báo
- [ ] Công ty test khôi phục `expiry_date` rỗng, đăng nhập lại bình thường
- [ ] SAVINA (`hominhsoniib@gmail.com` / MST `3901323107`) đăng nhập bình thường
- [ ] Phúc An (MST `0317598974`) đăng nhập bình thường
- [ ] File tạm đã dọn, backup gốc còn giữ lại

---

*Ghi chú kỹ thuật — phiên làm việc 25/08/2026.*

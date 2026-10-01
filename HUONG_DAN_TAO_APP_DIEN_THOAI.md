# 📱 HƯỚNG DẪN SỬ DỤNG VÀ TẠO APP DI ĐỘNG (MOBILE APP) CHO AMS PRO 5.0

Hệ thống **AMS PRO 5.0 (QLCV_web)** đã được bổ sung phiên bản ứng dụng di động chuyên dụng (`/mobile`) và chuẩn **Progressive Web App (PWA)**, cho phép cài đặt lên điện thoại di động (iPhone, Android) như một app ứng dụng gốc từ App Store / Google Play.

---

## 🚀 CÁCH 1: CÀI ĐẶT APP PWA TRỰC TIẾP LÊN ĐIỆN THOẠI (KHÔNG CẦN CHỜ DUYỆT APP STORE)

Đây là cách nhanh nhất (chỉ mất 10 giây). Ứng dụng sẽ tự xuất hiện biểu tượng (Icon) ngoài Màn hình chính của điện thoại, khởi chạy toàn màn hình độc lập.

### 📱 1. Đối với iPhone / iPad (iOS Safari)
1. Mở trình duyệt **Safari** trên iPhone.
2. Truy cập địa chỉ ứng dụng: `https://app.congty.com/mobile` (hoặc IP VPS / domain công ty).
3. Nhấp vào nút **Chia sẻ (Share icon)** <i class="fa-solid fa-share-nodes"></i> ở thanh công cụ dưới Safari.
4. Cuộn xuống và chọn **"Thêm vào Màn hình chính" (Add to Home Screen)**.
5. Đặt tên app là **QLCV Mobile** và bấm **Thêm (Add)**.
6. Mở app ngay ngoài màn hình iPhone để trải nghiệm giao diện full màn hình!

### 🤖 2. Đối với điện thoại Android (Google Chrome)
1. Mở trình duyệt **Google Chrome** trên Android.
2. Truy cập địa chỉ `https://app.congty.com/mobile`.
3. Bấm vào dấu **3 chấm** ở góc trên bên phải Chrome.
4. Chọn **"Thêm vào màn hình chính" (Add to Home Screen)** hoặc **"Cài đặt ứng dụng" (Install App)**.
5. Bấm **Thêm/Cài đặt**.
6. Biểu tượng **QLCV Mobile** sẽ xuất hiện trên màn hình ứng dụng điện thoại.

---

## 🛠️ CÁCH 2: ĐÓNG GÓI THÀNH FILE `.APK` CÀI ĐẶT CHO ANDROID (Dành cho IT / ADMIN)

Nếu công ty muốn cấp file `.apk` cài đặt trực tiếp cho nhân viênAndroid:

### Phương pháp 1: Sử dụng Bubblewrap CLI (Google Trusted Web Activity - TWA)
1. Cài đặt Node.js và Java JDK 17 trên máy tính.
2. Mở Terminal / Command Prompt và chạy:
   ```bash
   npm install -g @bubblewrap/cli
   bubblewrap init --manifest=https://app.congty.com/manifest.json
   bubblewrap build
   ```
3. File `app-release-signed.apk` sẽ được tạo ra sẵn sàng gửi qua Zalo / Email để cài đặt.

### Phương pháp 2: Sử dụng Capacitor Wrapper
1. Di chuyển vào thư mục `mobile_app_builder/`.
2. Mở file `capacitor.config.json` và cập nhật đường dẫn `url` thành domain máy chủ VPS của bạn (`https://app.congty.com/mobile`).
3. Khởi chạy Capacitor:
   ```bash
   npm install @capacitor/core @capacitor/cli @capacitor/android
   npx cap add android
   npx cap open android
   ```
4. Mở Android Studio và chọn **Build -> Build Bundle(s) / APK(s) -> Build APK(s)**.

---

## ✨ TÍNH NĂNG NỔI BẬT CỦA PHIÊN BẢN DI ĐỘNG (`/mobile`)

- **Trang chủ di động (`/mobile/dashboard`)**: Xem nhanh KPI công việc, công việc đang thực hiện, hoàn thành, trễ hạn.
- **Danh sách công việc di động (`/mobile/tasks`)**: Lọc theo trạng thái (Đang làm, Quá hạn, Hoàn thành), tìm kiếm tức thì.
- **Danh bạ CRM di động (`/mobile/crm`)**: Phím tắt 1-Touch Gọi điện (`tel:`) & Mở Zalo (`https://zalo.me/`) cho khách hàng.
- **Trợ lý AI di động (`/mobile/ai`)**: Trò chuyện và gợi ý kế hoạch công việc ngay trên điện thoại.
- **Thanh điều hướng đáy (Bottom Navigation Bar)**: Chuẩn trải nghiệm ứng dụng di động native.

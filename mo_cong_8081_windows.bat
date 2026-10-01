@echo off
title MO CONG FIREWALL 8081 CHO WINDOWS SERVER / VPS
color 0A
cd /d "%~dp0"

echo =====================================================================
echo    TU DONG MO CONG FIREWALL WINDOWS CHO PORT 8081 (AMS PRO 5.0)
echo =====================================================================
echo.

net session >nul 2>&1
if %errorLevel% == 0 (
    echo [+] Da xac nhan quyen Administrator!
) else (
    echo [!] CHU Y: Vui long nhap chuot phai vao file bat nay va chon "Run as administrator" (Chay voi quyen Quat tri)!
    echo.
    pause
    exit /b 1
)

echo [*] Dang tao Inbound Rule mo port 8081 trong Windows Firewall...
netsh advfirewall firewall add rule name="AMS_PRO_QLCV_Port_8081" dir=in action=allow protocol=TCP localport=8081 >nul 2>&1
netsh advfirewall firewall add rule name="AMS_PRO_BaoGia_Port_8502" dir=in action=allow protocol=TCP localport=8502 >nul 2>&1

echo [+] DA MO THANH CONG PORT 8081 VA 8502 TREN WINDOWS FIREWALL!
echo.
echo Bay gio ban co the truy cap bang: http://app.badenfarm.com.vn:8081
echo.
pause

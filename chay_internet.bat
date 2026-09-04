@echo off
title AMS PRO 5.0 - KET NOI INTERNET 1-CLICK
color 0B
cd /d "%~dp0"

echo =====================================================================
echo    AMS PRO 5.0 - KET NOI INTERNET 1-CLICK (CLOUDFLARE TUNNEL)
echo =====================================================================
echo.

if not exist venv\Scripts\python.exe (
    echo [ERROR] Khong tim thay moi truong ao venv!
    pause
    exit /b
)

set APP_PORT=8081
if exist .env (
    for /f "usebackq tokens=2 delims==" %%i in (`findstr "^PORT=" .env`) do (
        for /f %%j in ("%%i") do set APP_PORT=%%j
    )
)

echo [+] Dang kiem tra may chu AMS PRO (Port %APP_PORT%)...
netstat -ano | findstr ":%APP_PORT% " >nul 2>&1
if errorlevel 1 (
    echo [*] Dang khoi dong may chu backend FastAPI tai cong %APP_PORT%...
    start "AMS-PRO-FastAPI" /min cmd /c "venv\Scripts\python.exe app.py"
    ping 127.0.0.1 -n 5 >nul
) else (
    echo [+] May chu AMS PRO 5.0 dang chay san sang tai port %APP_PORT%!
)

echo.
echo =====================================================================
echo [*] KHOI TAO DUONG TRUYEN INTERNET TOAN CAU (CLOUDFLARE TUNNEL)
echo =====================================================================
echo.

venv\Scripts\python.exe share_internet.py

pause

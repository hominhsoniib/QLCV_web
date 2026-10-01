@echo off
title AMS PRO 5.0 - QUAN LY CONG VIEC (QLCV) WEB OS - Auto Startup
color 0A
cd /d "%~dp0"

echo =====================================================================
echo    KHOI DONG HE THONG QUAN LY CONG VIEC - AMS PRO 5.0 (QLCV WEB OS)
echo =====================================================================
echo.

:: 1. Kiem tra moi truong ao venv
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe --version >nul 2>&1
    if not errorlevel 1 (
        echo [+] Da phat hien moi truong ao venv san sang.
        goto START_SERVICES
    )
)

:: 2. Kiem tra Python tren he thong neu chua co venv
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI CRITICAL] May tinh cua ban chua cai dat Python hoac chua them vao PATH!
    echo Vui long cai dat Python 3.9+ va tich chon "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: 3. Tao venv moi va cai dat thu vien
echo [*] Dang khoi tao moi truong ao venv...
python -m venv venv
if errorlevel 1 (
    echo [LOI CRITICAL] Khong the tao moi truong ao venv!
    echo.
    pause
    exit /b 1
)

echo [*] Dang cai dat cac thu vien can thiet...
call venv\Scripts\activate
venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
if exist requirements.txt (
    venv\Scripts\pip.exe install -r requirements.txt
)

:START_SERVICES
:: Doc PORT tu file .env
set APP_PORT=8081
if exist .env (
    for /f "usebackq tokens=2 delims==" %%i in (`findstr "^PORT=" .env`) do (
        for /f %%j in ("%%i") do set APP_PORT=%%j
    )
)

echo.
echo =====================================================================
echo   DANG KHOI DONG CAC MAY CHU HET THONG WEB QLCV...
echo   - 1. Main Web System (AMS PRO 5.0 QLCV): http://localhost:%APP_PORT%
echo =====================================================================
echo.

:: Tu dong mo trinh duyet khi server san sang
start /b venv\Scripts\python.exe -c "import time, socket, webbrowser; [time.sleep(1) for _ in range(30) if socket.socket().connect_ex(('127.0.0.1', %APP_PORT%)) != 0]; webbrowser.open('http://localhost:%APP_PORT%')"

:: Chay main FastAPI server
echo [*] Dang khoi dong Main FastAPI Web Application (Port %APP_PORT%)...
venv\Scripts\python.exe app.py

if errorlevel 1 (
    echo.
    echo =====================================================================
    echo [LOI THUC THI] May chu Web dung hoac gap loi khi khoi chay!
    echo Nguyên nhân co thể do cong %APP_PORT% dang bi chiem dung boi tien trinh khac.
    echo =====================================================================
)

echo.
echo Nhan phan bat ky de dong cua so nay...
pause

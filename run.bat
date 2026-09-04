@echo off
cd /d "%~dp0"
title AMS PRO 5.0 - Quan Ly Cong Viec (QLCV)
color 0A
echo =====================================================================
echo    KHOI DONG HE THONG QUAN LY CONG VIEC CA NHAN - AMS PRO 5.0
echo =====================================================================
echo.

if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe --version >nul 2>&1
    if not errorlevel 1 goto START_APP
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] May tinh cua ban chua cai dat Python hoac chua them vao PATH!
    echo Vui long cai dat Python 3.9+ va tich chon "Add Python to PATH".
    pause
    exit /b 1
)

echo [*] Dang khoi tao moi truong ao Python (venv)...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Khong the tao moi truong ao venv!
    pause
    exit /b 1
)

call venv\Scripts\activate
venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
if exist requirements.txt (
    venv\Scripts\pip.exe install -r requirements.txt
)

:START_APP
set APP_PORT=8000
if exist .env (
    for /f "usebackq tokens=2 delims==" %%i in (`findstr "^PORT=" .env`) do (
        for /f %%j in ("%%i") do set APP_PORT=%%j
    )
)

echo.
echo =====================================================================
echo [+] May chu dang khoi dong...
echo [+] Tu dong mo trinh duyet truy cap: http://localhost:%APP_PORT%
echo [+] Nhan Ctrl + C de dung may chu.
echo =====================================================================
echo.

start /b venv\Scripts\python.exe -c "import time, socket, webbrowser; [time.sleep(1) for _ in range(30) if socket.socket().connect_ex(('127.0.0.1', %APP_PORT%)) != 0]; webbrowser.open('http://localhost:%APP_PORT%')"

venv\Scripts\python.exe app.py

if errorlevel 1 (
    echo.
    echo [LOI] May chu ngung hoat dong hoac cong %APP_PORT% dang bi chiem.
)
echo.
pause

@echo off
title AMS PRO 5.0 - QUAN LY CONG VIEC (QLCV WEB OS) - WINDOWS VPS PRODUCTION SERVER
color 0A
cd /d "%~dp0"

echo =====================================================================
echo    HET THONG QUAN LY CONG VIEC - AMS PRO 5.0 (QLCV WEB OS)
echo              MAY CHU PRODUCTION VPS (WINDOWS SERVER)
echo =====================================================================
echo.

:: 1. Kiem tra moi truong ao venv
if exist venv\Scripts\python.exe (
    venv\Scripts\python.exe --version >nul 2>&1
    if not errorlevel 1 (
        echo [+] Moi truong ao venv hop le va da san sang.
        goto LOAD_ENV
    )
)

:: 2. Kiem tra Python he thong neu chua co venv
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI CRITICAL] VPS chua cai dat Python hoac chua them Python vao PATH!
    echo Vui long cai dat Python 3.9+ va tich chon "Add Python to PATH".
    echo.
    pause
    exit /b 1
)

:: 3. Tu dong khoi tao venv & cai dat dependencies cho VPS
echo [*] Dang khoi tao moi truong ao Python (venv)...
python -m venv venv
if errorlevel 1 (
    echo [LOI CRITICAL] Khong the tao moi truong ao venv!
    echo.
    pause
    exit /b 1
)

echo [*] Dang cap nhat pip va cai dat cac thu vien can thiet...
call venv\Scripts\activate
venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
if exist requirements.txt (
    echo [*] Cai dat dependencies tu requirements.txt
    venv\Scripts\pip.exe install -r requirements.txt
)

:LOAD_ENV
:: 4. Doc thong so PORT va HOST tu file .env
set APP_PORT=8081
set APP_HOST=0.0.0.0

if exist .env (
    for /f "usebackq tokens=2 delims==" %%i in (`findstr "^PORT=" .env`) do (
        for /f %%j in ("%%i") do set APP_PORT=%%j
    )
    for /f "usebackq tokens=2 delims==" %%i in (`findstr "^HOST=" .env`) do (
        for /f %%j in ("%%i") do set APP_HOST=%%j
    )
)

echo.
echo =====================================================================
echo [THONG TIN CAU HINH MAY CHU VPS]
echo   - Binding Host : %APP_HOST% (Cho phep truy cap tu Internet/VPS)
echo   - FastAPI Port : %APP_PORT%
echo =====================================================================
echo.

:: 5. Mo cong firewall neu chua co rule
netsh advfirewall firewall show rule name="QLCV_Web_Port_%APP_PORT%" >nul 2>&1
if errorlevel 1 goto ADD_FIREWALL_RULES
goto START_BROWSER

:ADD_FIREWALL_RULES
echo [*] Dang mo cong Firewall Windows cho port %APP_PORT%
netsh advfirewall firewall add rule name="QLCV_Web_Port_%APP_PORT%" dir=in action=allow protocol=TCP localport=%APP_PORT% >nul 2>&1

:START_BROWSER
:: 7. Tu dong mo Trinh duyet Web sau 3 giay
echo [*] Dang tu dong mo trinh duyet truy cap chuong trinh...
start /b cmd /c "ping 127.0.0.1 -n 4 >nul && start http://localhost:%APP_PORT%"

:: 8. Vong lap chay May chu FastAPI (Auto Reload khi cap nhat code)
:SERVER_LOOP
echo.
echo =====================================================================
echo [+] MAY CHU AMS PRO 5.0 DANG CHAY TREN VPS (PORT %APP_PORT%) 24/7
echo [+] Dia chi truy cap noi bo VPS: http://localhost:%APP_PORT%
echo [+] Dia chi truy cap tu xa   : http://[IP_PUBLIC_VPS]:%APP_PORT%
echo [+] Nhan Ctrl + C de dung may chu.
echo =====================================================================
echo.

:: Chay Uvicorn che do Production an dinh 24/7 (khong reload gay treo watcher)
venv\Scripts\python.exe -m uvicorn app:app --host %APP_HOST% --port %APP_PORT% --timeout-keep-alive 65

if errorlevel 1 (
    echo.
    echo [CANH BAO CRITICAL] May chu ngung hoac gap su co! DANG TU DONG KHOI DONG LAI NGAY LAP TUC...
    timeout /t 2 /nobreak >nul
    goto SERVER_LOOP
)

pause

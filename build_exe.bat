@echo off
title AMS PRO 5.0 - Compile Executable Package
color 0E
echo =====================================================================
echo    BIEN DICH VA DONG GOI UNG DUNG AMS PRO 5.0 (PYINSTALLER)
echo =====================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] May tinh cua ban chua cai dat Python!
    pause
    exit /b
)

:: Run compiler script using local environment
if exist venv (
    echo [*] Kich hoat moi truong ao venv de build...
    call venv\Scripts\activate
)

pyinstaller QLCV_AMS_PRO.spec --clean -y
pause

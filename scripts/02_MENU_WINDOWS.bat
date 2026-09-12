@echo off
setlocal
cd /d "%~dp0\.."

:menu
cls
echo ============================================================
echo PROYECTO FINAL - SIGVACH - WINDOWS
echo ============================================================
echo 1. FIREBASE - elegir dispositivo
echo 2. FIREBASE - Chrome
echo 3. Ver dispositivos
echo 0. Salir
echo ============================================================
set /p option=Opcion: 

if "%option%"=="1" flutter run
if "%option%"=="2" flutter run -d chrome
if "%option%"=="3" flutter devices
if "%option%"=="0" exit /b 0

echo.
pause
goto menu

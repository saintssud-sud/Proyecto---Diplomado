@echo off
setlocal
cd /d "%~dp0\.."

echo No hay nada que configurar.
echo La app usa Firebase (Authentication + Cloud Firestore) y la configuracion
echo va incrustada en lib\firebase_options.dart.
echo.
echo Solo necesitas:
echo   flutter pub get
echo   flutter run
pause

@echo off
cd /d "%~dp0"
echo ============================================================
echo  SECURITY INCIDENT DASHBOARD - Iniciando con Docker
echo ============================================================
echo  Asegurate de tener Docker Desktop ABIERTO.
echo  Abre luego: http://localhost:8000/docs
echo  Para detener: cierra esta ventana o pulsa Ctrl + C
echo ============================================================
echo.
docker compose up --build
pause

@echo off
cd /d "%~dp0"
echo ============================================================
echo  SECURITY INCIDENT DASHBOARD - Modo local (necesita MySQL)
echo ============================================================
echo.

if not exist venv (
    echo [1/3] Creando entorno virtual...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [2/3] Instalando dependencias (primera vez, puede tardar)...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

if not exist .env (
    echo [3/3] No existe .env. Creandolo desde la plantilla...
    copy .env.example .env
    echo.
    echo  *** IMPORTANTE ***
    echo  Se abrira el Bloc de notas. Ajusta DATABASE_URL con tu MySQL,
    echo  guarda, cierra el Bloc de notas y volvera a continuar.
    echo.
    pause
    notepad .env
)

echo.
echo Iniciando API en http://localhost:8000/docs ...
echo (Para detener: Ctrl + C)
echo.
uvicorn app.main:app --reload
pause

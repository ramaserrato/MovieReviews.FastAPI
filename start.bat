@echo off
echo 🎬 INICIANDO MOVIE REVIEWS FASTAPI
echo ===================================

if not exist "venv\" (
    echo ❌ Entorno virtual no encontrado. Ejecuta install.sh
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
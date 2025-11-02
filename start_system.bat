@echo off
echo ============================================================
echo    SISTEMA DE CONTROL DE RESIDUOS
echo ============================================================
echo.

echo Iniciando sistema...
python run_app.py
if errorlevel 1 (
    echo.
    echo Error al iniciar el sistema
    pause
    exit /b 1
)

echo.
echo Sistema iniciado correctamente!
pause

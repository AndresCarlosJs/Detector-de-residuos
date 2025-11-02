@echo off
REM Script de despliegue para Windows

echo === Iniciando el despliegue del sistema ===

REM Crear directorios necesarios
if not exist "logs" mkdir logs
if not exist "instance" mkdir instance

REM Activar el entorno virtual si existe
if exist ".venv\Scripts\activate.bat" (
    echo Activando entorno virtual...
    call .venv\Scripts\activate.bat
) else (
    echo Creando nuevo entorno virtual...
    python -m venv .venv
    call .venv\Scripts\activate.bat
)

REM Instalar o actualizar dependencias
echo Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Configurar variables de entorno
echo Configurando variables de entorno...
set FLASK_APP=web.app
set FLASK_ENV=production
set SECRET_KEY=tu-clave-secreta-aqui

REM Inicializar/actualizar la base de datos
echo Inicializando la base de datos...
python db_admin.py init

REM Verificar modelo YOLO
echo Verificando modelo YOLO...
if not exist "yolov8n.pt" (
    echo Descargando modelo YOLO...
    python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
)

REM Iniciar Gunicorn
echo Iniciando el servidor...
python -m gunicorn -c gunicorn.conf.py "web.app:app"

echo === Despliegue completado ===
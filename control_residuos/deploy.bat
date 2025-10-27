@echo off
REM Script de despliegue para Windows

echo Iniciando el despliegue del sistema...

REM Crear directorio para logs si no existe
if not exist "logs" mkdir logs

REM Activar el entorno virtual
call .venv\Scripts\activate.bat

REM Instalar o actualizar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Configurar variables de entorno
set FLASK_APP=web.app
set FLASK_ENV=production
set SECRET_KEY=tu-clave-secreta-aqui

REM Inicializar/actualizar la base de datos
echo Inicializando la base de datos...
python init_db.py

REM Iniciar Gunicorn
echo Iniciando el servidor...
python -m gunicorn -c gunicorn.conf.py "web.app:app"

echo Despliegue completado.
# -*- coding: utf-8 -*-
import os
import logging
from pathlib import Path

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Configuración de logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Configuración del servidor web
APP_HOST = '127.0.0.1'  # Para desarrollo local
APP_PORT = 5000  # Puerto por defecto
DEBUG_MODE = False
AUTO_PORT = True  # Buscar puerto alternativo si el default está ocupado

# Configuración de la base de datos PostgreSQL
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'residuos_db'
DB_USER = 'postgres'
DB_PASSWORD = '123'

SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuración del modelo YOLO
YOLO_MODEL_PATH = str(BASE_DIR.parent / 'runs/detect/waste_detector3/weights/best.pt')
YOLO_CONFIDENCE = 0.3  # Umbral de confianza para detecciones

# Configuración de cámaras
MAX_CAMERAS = 4  # Número máximo de cámaras soportadas
CAMERA_WIDTH = 640  # Ancho de captura de la cámara
CAMERA_HEIGHT = 480  # Alto de captura de la cámara
CAMERA_FPS = 30  # FPS objetivo para la captura
CAMERA_BUFFER_SIZE = 1  # Tamaño del buffer de frames

# Configuración de seguridad
SECRET_KEY = 'dev-key-change-in-production'
SESSION_TYPE = 'filesystem'
# -*- coding: utf-8 -*-
import os
import sys
import logging
import traceback
import socket
import codecs
from settings import *

# Añadir el directorio padre al path
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

# Configurar logging
logging.basicConfig(
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'app.log'), encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Forzar codificación UTF-8 en la salida estándar
if sys.stdout.encoding != 'utf-8' and hasattr(sys.stdout, 'detach'):
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
if sys.stderr.encoding != 'utf-8' and hasattr(sys.stderr, 'detach'):
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logger = logging.getLogger(__name__)

# Asegurarse de que estamos en el directorio correcto
os.chdir(BASE_DIR)
logger.info(f"Directorio de trabajo: {BASE_DIR}")

# Verificar que el modelo YOLO existe
if not os.path.exists(YOLO_MODEL_PATH):
    logger.error(f"No se encontró el modelo YOLO en {YOLO_MODEL_PATH}")
    sys.exit(1)
logger.info(f"Modelo YOLO encontrado en {YOLO_MODEL_PATH}")

try:
    # Importar dependencias críticas
    import cv2
    import numpy as np
    from ultralytics import YOLO
    logger.info("Dependencias críticas importadas correctamente")
    
    # Importar la aplicación
    from web.app import app
    logger.info("Aplicación web importada correctamente")
    
except ImportError as e:
    logger.error(f"Error al importar dependencias: {str(e)}")
    logger.error(traceback.format_exc())
    sys.exit(1)
except Exception as e:
    logger.error(f"Error inesperado durante la inicialización: {str(e)}")
    logger.error(traceback.format_exc())
    sys.exit(1)

def find_free_port(start_port=APP_PORT, max_port=APP_PORT + 10):
    """Encuentra un puerto disponible empezando por APP_PORT"""
    for port in range(start_port, max_port + 1):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((APP_HOST, port))
            sock.close()
            return port
        except OSError:
            continue
        finally:
            sock.close()
    return None

if __name__ == '__main__':
    try:
        logger.info("\n=== Iniciando Sistema de Control de Residuos ===")
        
        port = find_free_port() if AUTO_PORT else APP_PORT
        if port is None:
            logger.error(f"No se encontró ningún puerto disponible entre {APP_PORT} y {APP_PORT + 10}")
            sys.exit(1)
            
        logger.info(f"Iniciando servidor web en http://{APP_HOST}:{port}")
        logger.info("Presiona Ctrl+C para detener el servidor")
        
        # Iniciar servidor
        app.run(
            debug=DEBUG_MODE,
            host=APP_HOST,
            port=port,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        logger.info("\n=== Deteniendo servidor por solicitud del usuario ===")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\nError inesperado: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)
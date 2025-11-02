"""
Script para verificar la configuración del sistema y sus componentes.
Ejecutar este script antes de iniciar el sistema para asegurarse de que todo está correctamente configurado.
"""

import os
import sys
import cv2
import logging
import psycopg2
from ultralytics import YOLO
import numpy as np

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_model():
    """Verifica que el modelo YOLO esté presente y funcione correctamente."""
    try:
        from config import MODEL_CONFIG
        
        logger.info("=== Verificando modelo YOLO ===")
        model_path = MODEL_CONFIG['path']
        
        if not os.path.exists(model_path):
            logger.error(f"No se encontró el modelo en: {model_path}")
            return False
            
        logger.info(f"Modelo encontrado en: {model_path}")
        logger.info("Intentando cargar el modelo...")
        
        model = YOLO(model_path)
        
        # Hacer una detección de prueba
        test_image = np.zeros((640, 480, 3), dtype=np.uint8)
        results = model(test_image, verbose=False)
        
        logger.info("Modelo YOLO verificado correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al verificar el modelo: {str(e)}")
        return False

def check_camera():
    """Verifica que se puede acceder a la cámara."""
    try:
        from config import CAMERA_CONFIG
        
        logger.info("=== Verificando acceso a cámara ===")
        resolution = CAMERA_CONFIG['resolution']
        fps = CAMERA_CONFIG['fps']
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logger.error("No se pudo acceder a la cámara")
            return False
            
        # Configurar propiedades
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
        cap.set(cv2.CAP_PROP_FPS, fps)
        
        # Leer un frame
        ret, frame = cap.read()
        if not ret:
            logger.error("No se pudo leer frame de la cámara")
            return False
            
        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        logger.info(f"Resolución: {actual_width}x{actual_height}")
        logger.info(f"FPS: {actual_fps}")
        
        cap.release()
        logger.info("Cámara verificada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al verificar la cámara: {str(e)}")
        if 'cap' in locals():
            cap.release()
        return False

def check_database():
    """Verifica la conexión a la base de datos."""
    try:
        from config import DB_CONFIG
        
        logger.info("=== Verificando conexión a base de datos ===")
        
        # Intentar conexión
        conn = psycopg2.connect(
            dbname=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        
        # Verificar que podemos ejecutar consultas
        cur = conn.cursor()
        cur.execute('SELECT version();')
        version = cur.fetchone()
        
        logger.info(f"Conectado a PostgreSQL: {version[0]}")
        
        cur.close()
        conn.close()
        logger.info("Base de datos verificada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al verificar la base de datos: {str(e)}")
        return False

def check_directories():
    """Verifica que existan todos los directorios necesarios."""
    try:
        from config import BASE_DIR, LOG_CONFIG
        
        logger.info("=== Verificando directorios del sistema ===")
        
        directories = [
            os.path.join(BASE_DIR, 'logs'),
            os.path.join(BASE_DIR, 'instance'),
            os.path.dirname(LOG_CONFIG['file'])
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Creado directorio: {directory}")
            else:
                logger.info(f"Directorio existente: {directory}")
        
        logger.info("Directorios verificados correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al verificar directorios: {str(e)}")
        return False

def main():
    """Ejecuta todas las verificaciones."""
    logger.info("\n=== Iniciando verificación del sistema ===\n")
    
    checks = [
        ("Directorios", check_directories),
        ("Base de datos", check_database),
        ("Modelo YOLO", check_model),
        ("Cámara", check_camera)
    ]
    
    all_passed = True
    
    for name, check in checks:
        logger.info(f"\nEjecutando verificación: {name}")
        try:
            if check():
                logger.info(f"✓ {name}: OK")
            else:
                logger.error(f"✗ {name}: FAILED")
                all_passed = False
        except Exception as e:
            logger.error(f"✗ {name}: ERROR - {str(e)}")
            all_passed = False
            
    logger.info("\n=== Resumen de verificación ===")
    if all_passed:
        logger.info("✓ Todas las verificaciones pasaron correctamente")
        return 0
    else:
        logger.error("✗ Algunas verificaciones fallaron")
        return 1

if __name__ == '__main__':
    sys.exit(main())
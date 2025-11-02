import cv2
import logging
import numpy as np
import traceback
from ultralytics import YOLO
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_model():
    try:
        # Cargar el modelo
        model_path = os.path.join(os.path.dirname(__file__), 'yolov8n.pt')
        logger.info(f"Cargando modelo desde {model_path}")
        model = YOLO(model_path)
        logger.info("Modelo cargado exitosamente")
        
        # Mostrar clases del modelo
        logger.info("\n=== Clases detectables por el modelo ===")
        class_names = model.names
        for idx, name in class_names.items():
            logger.info(f"{idx:3d}: {name}")
        logger.info(f"Total de clases: {len(class_names)}")
        
        # Identificar clases relevantes para residuos
        residuos_relevantes = [
            name for name in class_names.values()
            if any(keyword in name.lower() for keyword in [
                'bottle', 'cup', 'can', 'box', 'paper', 
                'bag', 'container', 'food', 'waste', 'trash',
                'plastic', 'metal', 'glass'
            ])
        ]
        
        logger.info("\n=== Clases relevantes para detección de residuos ===")
        for item in sorted(residuos_relevantes):
            logger.info(f"- {item}")
        logger.info(f"Total de clases relevantes: {len(residuos_relevantes)}")

        # Crear una imagen de prueba
        test_image = cv2.imread(os.path.join(os.path.dirname(__file__), 'yolov8n.pt'))
        if test_image is None:
            test_image = np.zeros((640, 640, 3), np.uint8)
        logger.info(f"Imagen de prueba creada con forma {test_image.shape}")

        # Realizar una detección
        logger.info("Intentando detección...")
        results = model(test_image)
        logger.info("Detección completada")
        
        logger.info("Test completado exitosamente")
        return True

    except Exception as e:
        logger.error(f"Error durante el test: {str(e)}")
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    test_model()
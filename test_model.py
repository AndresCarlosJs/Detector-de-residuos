import cv2
from ultralytics import YOLO
import os
from control_residuos.settings import *

def test_model():
    # Cargar el modelo configurado
    print(f"Cargando modelo desde {YOLO_MODEL_PATH}...")
    model = YOLO(YOLO_MODEL_PATH)
    
    # Directorio de imágenes de prueba
    test_dir = "datasets/garbage_classification/test"
    
    # Tomar algunas imágenes de prueba
    print("\nProbando detección en imágenes...")
    for class_dir in os.listdir(test_dir):
        class_path = os.path.join(test_dir, class_dir)
        if os.path.isdir(class_path):
            # Tomar la primera imagen de cada clase
            images = [f for f in os.listdir(class_path) if f.endswith(('.jpg', '.png', '.jpeg'))]
            if images:
                img_path = os.path.join(class_path, images[0])
                print(f"\nProbando imagen de clase {class_dir}: {img_path}")
                
                # Cargar y procesar la imagen
                img = cv2.imread(img_path)
                if img is None:
                    print(f"Error al cargar la imagen: {img_path}")
                    continue
                    
                # Realizar la detección con umbral configurado
                results = model.predict(img, conf=YOLO_CONFIDENCE)
                
                # Mostrar resultados
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = model.names[cls_id]
                        print(f"Detectado: {class_name} (confianza: {conf:.2f})")

if __name__ == "__main__":
    test_model()
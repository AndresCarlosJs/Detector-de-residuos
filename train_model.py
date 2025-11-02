from ultralytics import YOLO
import os
from pathlib import Path
from control_residuos.settings import *

def setup_dataset_yaml():
    """Crea el archivo de configuración YAML para el dataset"""
    yaml_content = """path: ./datasets/garbage_classification
train: Garbage classification/Garbage classification
val: Garbage classification/Garbage classification
test: Garbage classification/Garbage classification

names:
  0: cardboard
  1: glass
  2: metal
  3: paper
  4: plastic
  5: trash"""
    
    dataset_dir = Path('datasets/garbage_classification')
    yaml_path = dataset_dir / 'dataset.yaml'
    
    with open(yaml_path, 'w') as f:
        f.write(yaml_content)
    
    return yaml_path

def train_waste_model():
    """Entrena un modelo YOLOv8 para detección de residuos"""
    
    # Crear configuración del dataset
    dataset_path = setup_dataset_yaml()
    
    print("🚀 Iniciando entrenamiento del modelo...")
    
    try:
        # Usar el modelo base configurado
        base_model = Path(YOLO_MODEL_PATH)
        if not base_model.exists():
            print(f"❌ Error: No se encontró el modelo base en {YOLO_MODEL_PATH}")
            return
            
        model = YOLO(str(base_model))
        
        # Entrenar con nuestro dataset
        results = model.train(
            data=str(dataset_path),
            epochs=50,
            imgsz=CAMERA_WIDTH,  # Usar resolución de cámara configurada
            batch=16,
            name='waste_detector',
            device='cpu',  # Usar CPU para entrenamiento
            conf=YOLO_CONFIDENCE  # Usar umbral de confianza configurado
        )
        
        # Guardar modelo en carpeta models
        models_dir = Path('models')
        models_dir.mkdir(exist_ok=True)
        
        trained_model = Path('runs/detect/waste_detector/weights/best.pt')
        if trained_model.exists():
            final_path = models_dir / 'waste_detector.pt'
            trained_model.rename(final_path)
            print(f"✅ Modelo guardado en {final_path}")
        else:
            print("❌ Error: No se encontró el modelo entrenado")
            
    except Exception as e:
        print(f"❌ Error durante el entrenamiento: {str(e)}")

if __name__ == '__main__':
    train_waste_model()
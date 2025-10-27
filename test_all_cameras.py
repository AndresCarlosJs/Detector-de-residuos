import cv2
import time
import numpy as np

def test_all_cameras():
    print("\n=== Test de todas las cámaras disponibles ===")
    
    # Lista de backends a probar
    backends = [
        (cv2.CAP_ANY, "Default"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation")
    ]
    
    # Probar cámaras en índices 0-4
    for camera_index in range(5):
        print(f"\nBuscando cámara en índice {camera_index}...")
        
        for backend, name in backends:
            try:
                print(f"\nProbando con {name}...")
                cap = None
                
                if backend == cv2.CAP_ANY:
                    cap = cv2.VideoCapture(camera_index)
                else:
                    cap = cv2.VideoCapture(camera_index + backend)
                
                if not cap.isOpened():
                    print(f"✗ No se pudo abrir la cámara con {name}")
                    continue
                
                # Intentar diferentes resoluciones
                resolutions = [
                    (640, 480),
                    (1280, 720),
                    (1920, 1080)
                ]
                
                for width, height in resolutions:
                    print(f"\nProbando resolución {width}x{height}...")
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                    
                    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
                    
                    # Intentar capturar frames
                    frames_captured = 0
                    for _ in range(5):  # Intentar 5 frames
                        ret, frame = cap.read()
                        if ret and frame is not None:
                            frames_captured += 1
                            
                            # Guardar el primer frame como imagen
                            if frames_captured == 1:
                                filename = f'camera_{camera_index}_{name.lower().replace(" ", "_")}_{width}x{height}.jpg'
                                cv2.imwrite(filename, frame)
                                print(f"✓ Frame guardado como {filename}")
                    
                    if frames_captured > 0:
                        print(f"✓ Configuración exitosa:")
                        print(f"  - Backend: {name}")
                        print(f"  - Resolución real: {actual_width}x{actual_height}")
                        print(f"  - FPS: {actual_fps}")
                        print(f"  - Frames capturados: {frames_captured}/5")
                
                cap.release()
                
            except Exception as e:
                print(f"✗ Error con {name}: {str(e)}")
                if cap is not None:
                    cap.release()
                continue
    
    print("\n=== Test completado ===")

if __name__ == "__main__":
    test_all_cameras()
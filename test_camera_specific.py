import cv2
import time

def test_camera_specific():
    print("\n=== Test específico para HD Web Camera ===")
    
    # Intentar diferentes configuraciones
    configs = [
        (0, cv2.CAP_DSHOW),
        (0, cv2.CAP_ANY),
        (0, cv2.CAP_MSMF),
        (1, cv2.CAP_DSHOW),
        (1, cv2.CAP_ANY),
        (1, cv2.CAP_MSMF)
    ]
    
    for camera_id, backend in configs:
        try:
            print(f"\nProbando cámara {camera_id} con backend {backend}...")
            
            # Crear string para la cámara
            if backend == cv2.CAP_DSHOW:
                cap = cv2.VideoCapture(camera_id, backend)
                # Configurar propiedades específicas para DirectShow
                cap.set(cv2.CAP_PROP_SETTINGS, 1)  # Mostrar diálogo de propiedades
            else:
                cap = cv2.VideoCapture(camera_id)
            
            if not cap.isOpened():
                print("No se pudo abrir la cámara")
                continue
            
            # Configurar resolución más baja para pruebas
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Intentar leer frames
            print("Intentando leer frames...")
            frames_read = 0
            for i in range(10):
                ret, frame = cap.read()
                if ret and frame is not None:
                    frames_read += 1
                    if frames_read == 1:
                        # Guardar el primer frame como prueba
                        filename = f'camera_{camera_id}_backend_{backend}_test.jpg'
                        cv2.imwrite(filename, frame)
                        print(f"✓ Frame guardado como {filename}")
                        print(f"✓ Dimensiones del frame: {frame.shape}")
                time.sleep(0.1)
            
            if frames_read > 0:
                print(f"✓ Éxito! Se leyeron {frames_read} frames")
                print(f"- Resolución: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                print(f"- FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")
                
            cap.release()
            
        except Exception as e:
            print(f"Error: {str(e)}")
            if 'cap' in locals():
                cap.release()

if __name__ == "__main__":
    test_camera_specific()
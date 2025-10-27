import cv2
import time

def test_camera_all():
    print("\n=== Test Completo de Cámara ===")
    
    # 1. Probar diferentes índices
    print("\nBuscando cámaras disponibles...")
    cameras_found = []
    
    # Lista de backends a probar
    backends = [
        (cv2.CAP_ANY, "Default"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation")
    ]
    
    # Probar cada índice con cada backend
    for camera_index in range(4):  # Probar índices 0-3
        print(f"\nProbando cámara índice {camera_index}:")
        for backend, backend_name in backends:
            try:
                print(f"\nIntentando con backend {backend_name}...")
                cap = cv2.VideoCapture(camera_index + backend)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"✓ Éxito con {backend_name}!")
                        print(f"- Resolución: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                        print(f"- FPS: {cap.get(cv2.CAP_PROP_FPS)}")
                        cameras_found.append((camera_index, backend, backend_name))
                        
                        # Guardar frame de prueba
                        test_file = f'camera_{camera_index}_{backend_name.lower().replace(" ", "_")}_test.jpg'
                        cv2.imwrite(test_file, frame)
                        print(f"- Frame de prueba guardado en: {test_file}")
                    else:
                        print(f"✗ {backend_name}: No puede leer frames")
                else:
                    print(f"✗ {backend_name}: No puede abrir la cámara")
                cap.release()
            except Exception as e:
                print(f"✗ Error con {backend_name}: {str(e)}")
    
    if not cameras_found:
        print("\n❌ No se encontró ninguna cámara funcional")
    else:
        print("\n✓ Cámaras encontradas:")
        for idx, backend, name in cameras_found:
            print(f"- Cámara {idx} usando {name}")
        
        # Probar la primera cámara encontrada
        print(f"\nProbando captura continua con la primera cámara encontrada...")
        idx, backend, name = cameras_found[0]
        cap = cv2.VideoCapture(idx + backend)
        
        if cap.isOpened():
            for i in range(10):
                ret, frame = cap.read()
                if ret:
                    print(f"Frame {i+1} capturado correctamente")
                time.sleep(0.1)
            cap.release()
    
    print("\n=== Test completado ===")

if __name__ == "__main__":
    test_camera_all()
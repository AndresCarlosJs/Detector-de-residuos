import cv2
import time

def test_camera():
    print("Iniciando prueba de cámara...")
    
    try:
        # Intentar abrir la cámara
        print("Intentando abrir la cámara...")
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("No se pudo abrir la cámara")
            return False
            
        print("Cámara abierta exitosamente")
        print(f"Backend siendo usado: {cap.getBackendName()}")
        
        # Obtener propiedades
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Resolución: {width}x{height}")
        print(f"FPS: {fps}")
        
        # Intentar leer algunos frames
        print("\nIntentando leer frames...")
        for i in range(5):
            ret, frame = cap.read()
            if ret:
                print(f"Frame {i+1} capturado exitosamente - Tamaño: {frame.shape}")
            else:
                print(f"Error al capturar frame {i+1}")
            time.sleep(0.5)
        
        # Liberar la cámara
        cap.release()
        print("\nPrueba completada")
        return True
        
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")
        return False

if __name__ == "__main__":
    # Listar backends disponibles
    print("Backends de OpenCV disponibles:")
    backends = [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_GSTREAMER, cv2.CAP_FFMPEG]
    backend_names = ["DEFAULT", "DSHOW", "MEDIA FOUNDATION", "GSTREAMER", "FFMPEG"]
    
    for backend, name in zip(backends, backend_names):
        try:
            cap = cv2.VideoCapture(0 + backend)
            if cap.isOpened():
                print(f"✓ {name} - Disponible y funcional")
                cap.release()
            else:
                print(f"✗ {name} - No funcional")
        except:
            print(f"✗ {name} - No disponible")
    
    print("\nIniciando prueba completa de cámara...")
    test_camera()
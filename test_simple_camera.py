import cv2
import time

def test_simple_camera():
    print("\n=== Test Simple de Cámara ===")
    
    # 1. Intentar abrir la cámara
    print("\nIntentando abrir la cámara...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    if not cap.isOpened():
        print("❌ Error: No se pudo abrir la cámara")
        return
    
    print("✓ Cámara abierta exitosamente")
    
    # 2. Obtener información de la cámara
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"\nInformación de la cámara:")
    print(f"- Resolución: {width}x{height}")
    print(f"- FPS: {fps}")
    
    # 3. Intentar leer algunos frames
    print("\nIntentando leer frames...")
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            print(f"✓ Frame {i+1} capturado exitosamente - Tamaño: {frame.shape}")
        else:
            print(f"❌ Error al capturar frame {i+1}")
        time.sleep(0.1)
    
    # 4. Liberar la cámara
    cap.release()
    print("\n=== Test completado ===")

if __name__ == "__main__":
    test_simple_camera()
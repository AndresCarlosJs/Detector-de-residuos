import cv2
import time

def test_camera():
    print("\n=== Test Básico de Cámara ===\n")
    
    # 1. Probar con backend predeterminado
    print("1. Probando con backend predeterminado...")
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ ¡Éxito! Se pudo capturar imagen")
                print(f"- Resolución: {frame.shape[1]}x{frame.shape[0]}")
                cv2.imwrite('test_default.jpg', frame)
                print("- Imagen guardada como 'test_default.jpg'")
            else:
                print("✗ No se pudo capturar imagen")
        else:
            print("✗ No se pudo abrir la cámara")
        cap.release()
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    # 2. Probar con DirectShow
    print("\n2. Probando con DirectShow...")
    try:
        cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✓ ¡Éxito! Se pudo capturar imagen")
                print(f"- Resolución: {frame.shape[1]}x{frame.shape[0]}")
                cv2.imwrite('test_dshow.jpg', frame)
                print("- Imagen guardada como 'test_dshow.jpg'")
            else:
                print("✗ No se pudo capturar imagen")
        else:
            print("✗ No se pudo abrir la cámara")
        cap.release()
    except Exception as e:
        print(f"✗ Error: {str(e)}")

    print("\n=== Test Completado ===")

if __name__ == "__main__":
    test_camera()
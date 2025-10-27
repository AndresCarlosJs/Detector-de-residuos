import cv2
import time

def test_camera():
    print("\n=== Test Simple de Cámara ===")
    
    # Probar cámara con índice 0 (integrada/default)
    print("\nProbando cámara 0 (Default)...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Cámara 0 funciona!")
            print(f"- Resolución: {frame.shape[1]}x{frame.shape[0]}")
            print(f"- FPS: {cap.get(cv2.CAP_PROP_FPS)}")
            cv2.imwrite('camera_test.jpg', frame)
            print("✓ Imagen de prueba guardada como 'camera_test.jpg'")
        else:
            print("✗ No se pudo leer frame de la cámara 0")
        cap.release()
    else:
        print("✗ No se pudo abrir la cámara 0")
    
    # Probar con DirectShow
    print("\nProbando cámara 0 con DirectShow...")
    cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Cámara 0 funciona con DirectShow!")
            print(f"- Resolución: {frame.shape[1]}x{frame.shape[0]}")
            print(f"- FPS: {cap.get(cv2.CAP_PROP_FPS)}")
            cv2.imwrite('camera_test_dshow.jpg', frame)
            print("✓ Imagen de prueba guardada como 'camera_test_dshow.jpg'")
        else:
            print("✗ No se pudo leer frame de la cámara 0 con DirectShow")
        cap.release()
    else:
        print("✗ No se pudo abrir la cámara 0 con DirectShow")
    
    # Probar con Media Foundation
    print("\nProbando cámara 0 con Media Foundation...")
    cap = cv2.VideoCapture(0 + cv2.CAP_MSMF)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Cámara 0 funciona con Media Foundation!")
            print(f"- Resolución: {frame.shape[1]}x{frame.shape[0]}")
            print(f"- FPS: {cap.get(cv2.CAP_PROP_FPS)}")
            cv2.imwrite('camera_test_msmf.jpg', frame)
            print("✓ Imagen de prueba guardada como 'camera_test_msmf.jpg'")
        else:
            print("✗ No se pudo leer frame de la cámara 0 con Media Foundation")
        cap.release()
    else:
        print("✗ No se pudo abrir la cámara 0 con Media Foundation")

if __name__ == "__main__":
    test_camera()
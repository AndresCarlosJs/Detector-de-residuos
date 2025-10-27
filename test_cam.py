import cv2
print("\n=== Test de Cámara Simple ===")

print("\n1. Probando backend predeterminado...")
cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("✓ Cámara funciona con backend predeterminado")
        print(f"- Resolución: {frame.shape[1]}x{frame.shape[0]}")
        cv2.imwrite('test_cam_default.jpg', frame)
        print("- Imagen guardada como test_cam_default.jpg")
    else:
        print("✗ No se pudo leer frame")
    cap.release()
else:
    print("✗ No se pudo abrir la cámara")

print("\n2. Probando DirectShow...")
cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("✓ Cámara funciona con DirectShow")
        print(f"- Resolución: {frame.shape[1]}x{frame.shape[0]}")
        cv2.imwrite('test_cam_dshow.jpg', frame)
        print("- Imagen guardada como test_cam_dshow.jpg")
    else:
        print("✗ No se pudo leer frame")
    cap.release()
else:
    print("✗ No se pudo abrir la cámara")

print("\n=== Test Completado ===")
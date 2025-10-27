import cv2

def test_cameras():
    # Probar diferentes índices de cámara
    for i in range(4):  # Intentará con cámaras 0-3
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Cámara {i} está disponible")
            # Obtener información de la cámara
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            print(f"Resolución: {width}x{height}")
            print(f"FPS: {fps}")
            
            # Intentar leer un frame
            ret, frame = cap.read()
            if ret:
                print(f"Lectura de frame exitosa para cámara {i}")
            else:
                print(f"No se pudo leer frame de cámara {i}")
        else:
            print(f"Cámara {i} no está disponible")
        cap.release()

if __name__ == "__main__":
    print("Buscando cámaras disponibles...")
    test_cameras()
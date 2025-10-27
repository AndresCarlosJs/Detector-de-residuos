import cv2
import time
import platform
import os

def print_section(title):
    print(f"\n{'='*20} {title} {'='*20}")

def get_system_info():
    print_section("Información del Sistema")
    print(f"Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print(f"OpenCV: {cv2.__version__}")
    print(f"Arquitectura: {platform.machine()}")

def test_camera_backends():
    print_section("Prueba de Backends")
    
    backends = [
        (None, "Default"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation")
    ]
    
    for backend, name in backends:
        print(f"\nProbando con {name}...")
        try:
            if backend is None:
                cap = cv2.VideoCapture(0)
            else:
                cap = cv2.VideoCapture(0 + backend)
            
            if not cap.isOpened():
                print(f"✗ No se pudo abrir la cámara con {name}")
                continue
                
            # Intentar leer un frame
            start_time = time.time()
            ret, frame = cap.read()
            end_time = time.time()
            
            if not ret or frame is None:
                print(f"✗ No se pudo leer frame con {name}")
                cap.release()
                continue
                
            # Obtener propiedades
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            print(f"✓ Éxito con {name}:")
            print(f"  - Tiempo de captura: {(end_time - start_time)*1000:.0f}ms")
            print(f"  - Resolución: {width}x{height}")
            print(f"  - FPS: {fps}")
            
            # Guardar frame de prueba
            filename = f"camera_test_{name.lower().replace(' ', '_')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"  - Frame guardado como: {filename}")
            
            # Probar captura continua
            print("  - Probando captura continua...")
            frames = 0
            test_time = 1.0  # segundos
            start_time = time.time()
            
            while time.time() - start_time < test_time:
                ret, frame = cap.read()
                if ret:
                    frames += 1
                    
            actual_fps = frames / test_time
            print(f"  - FPS reales: {actual_fps:.1f}")
            
            cap.release()
            
        except Exception as e:
            print(f"✗ Error con {name}: {str(e)}")
            if 'cap' in locals():
                cap.release()

def check_video_devices():
    print_section("Verificación de Dispositivos")
    try:
        if platform.system() == 'Windows':
            # Probar índices 0-9
            for i in range(10):
                try:
                    cap = cv2.VideoCapture(i)
                    if cap.isOpened():
                        ret, frame = cap.read()
                        if ret:
                            print(f"✓ Cámara encontrada en índice {i}")
                            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            print(f"  - Resolución: {width}x{height}")
                    cap.release()
                except:
                    continue
    except Exception as e:
        print(f"Error al verificar dispositivos: {str(e)}")

def main():
    print("\n=== Iniciando Diagnóstico de Cámara ===\n")
    
    try:
        get_system_info()
        check_video_devices()
        test_camera_backends()
        
        print("\n=== Diagnóstico Completado ===")
        
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {str(e)}")

if __name__ == "__main__":
    main()
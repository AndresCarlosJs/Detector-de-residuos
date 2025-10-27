import cv2 
import numpy as np
from threading import Thread, Lock
import time
import traceback

def list_available_cameras():
    """Lista todas las cámaras disponibles en el sistema."""
    available_cameras = []
    
    # Probar diferentes índices y backends
    for idx in range(10):  # Probar los primeros 10 índices
        for backend, name in [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Default")
        ]:
            try:
                if backend == cv2.CAP_ANY:
                    cap = cv2.VideoCapture(idx)
                else:
                    cap = cv2.VideoCapture(idx + backend)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        available_cameras.append({
                            'id': idx,
                            'backend': backend,
                            'backend_name': name,
                            'resolution': f"{width}x{height}",
                            'fps': fps
                        })
                cap.release()
            except:
                continue
    
    return available_cameras

class CameraCapture:
    def __init__(self, camera_id=0, resolution=(640, 480), fps=30):
        self.camera_id = camera_id
        self.resolution = resolution
        self.fps = fps
        self.cap = None
        self.frame = None
        self.running = False
        self.lock = Lock()
        self.last_frame_time = 0
        self.frame_interval = 1.0 / fps
        self.capture_thread = None
        self.backend = None
        print(f"\n=== Inicializando CameraCapture ===")
        print(f"- ID de cámara: {camera_id}")
        print(f"- Resolución solicitada: {resolution}")
        print(f"- FPS solicitados: {fps}")
        print(f"Inicializando CameraCapture con ID: {camera_id}")
        
    def _try_open_camera(self):
        """Intenta abrir la cámara con diferentes backends"""
        backends = [
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation"),
            (cv2.CAP_ANY, "Default"),
            (-1, "Auto")
        ]
        
        for backend, name in backends:
            try:
                print(f"Intentando abrir cámara con {name}...")
                if backend == -1:
                    cap = cv2.VideoCapture(self.camera_id)
                else:
                    cap = cv2.VideoCapture(self.camera_id + backend)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"✓ Conexión exitosa con {name}")
                        self.backend = backend
                        return cap
                    cap.release()
            except Exception as e:
                print(f"Error con {name}: {str(e)}")
                continue
        
        return None

    def start(self):
        try:
            print(f"\n=== Iniciando cámara {self.camera_id} ===")
            if self.cap is None:
                print(f"Intentando abrir cámara {self.camera_id}...")
                
                # Intentar listar cámaras disponibles
                available_cameras = []
                for i in range(5):  # Probar los primeros 5 índices
                    try:
                        temp_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                        if temp_cap.isOpened():
                            ret, frame = temp_cap.read()
                            if ret:
                                available_cameras.append(i)
                        temp_cap.release()
                    except:
                        continue
                
                print(f"Cámaras disponibles: {available_cameras}")
                
                if self.camera_id not in available_cameras and available_cameras:
                    print(f"WARNING: Camera ID {self.camera_id} no encontrada. Usando primera cámara disponible: {available_cameras[0]}")
                    self.camera_id = available_cameras[0]
                
                # Lista de backends a probar
                backends = [
                    (cv2.CAP_DSHOW, "DirectShow"),
                    (cv2.CAP_MSMF, "Media Foundation"),
                    (cv2.CAP_ANY, "Default"),
                    (-1, "Auto")  # Intentar detección automática
                ]
                
                # Intentar cada backend
                for backend, name in backends:
                    try:
                        print(f"Probando backend: {name}")
                        self.cap = cv2.VideoCapture(self.camera_id, backend)
                        if self.cap.isOpened():
                            print(f"Conexión exitosa usando {name}")
                            break
                    except Exception as e:
                        print(f"Error con backend {name}: {str(e)}")
                        continue
                
                if self.cap is None or not self.cap.isOpened():
                    raise RuntimeError("No se pudo abrir la cámara con ningún backend")
                
                # Configurar propiedades
                print("Configurando propiedades de la cámara...")
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
                self.cap.set(cv2.CAP_PROP_FPS, self.fps)
                
                # Verificar configuración actual
                actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
                actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
                
                print(f"Configuración actual de la cámara:")
                print(f"- Resolución: {actual_width}x{actual_height}")
                print(f"- FPS: {actual_fps}")

            print("Realizando lectura de prueba...")
            ret, frame = self.cap.read()
            if not ret or frame is None:
                raise RuntimeError("No se pudo obtener imagen de la cámara")
            
            print(f"Lectura exitosa, dimensiones del frame: {frame.shape}")
            
            print("Iniciando thread de captura...")
            self.running = True
            self.capture_thread = Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            print("=== Cámara iniciada exitosamente ===\n")
            
        except Exception as e:
            print(f"\n!!! Error al iniciar la cámara !!!")
            print(f"Detalles del error: {str(e)}")
            print(traceback.format_exc())
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            raise RuntimeError(f"Error al iniciar la cámara: {str(e)}")

    def _capture_loop(self):
        while self.running:
            current_time = time.time()
            if current_time - self.last_frame_time >= self.frame_interval:
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                    self.last_frame_time = current_time

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def get_jpeg(self):
        frame = self.get_frame()
        if frame is None:
            return None
        ret, jpeg = cv2.imencode('.jpg', frame)
        if ret:
            return jpeg.tobytes()
        return None

    def stop(self):
        self.running = False
        if self.capture_thread is not None:
            self.capture_thread.join()
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def __del__(self):
        self.stop()
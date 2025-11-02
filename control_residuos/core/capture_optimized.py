import cv2 
import numpy as np
from threading import Thread, Lock
import time
import traceback
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class CameraCapture:
    def __init__(self, camera_id=0, resolution=(640,480), fps=30):
        """
        Inicializa una instancia de captura de cámara optimizada para detección.
        Args:
            camera_id (int): ID de la cámara a utilizar
            resolution (tuple): Resolución deseada (width, height)
            fps (int): Frames por segundo deseados
        """
        self.camera_id = camera_id
        self.resolution = resolution 
        self.fps = fps
        self.cap = None
        self.frame = None
        self.processed_frame = None
        self.running = False
        self.lock = Lock()
        self.processed_lock = Lock()
        self.last_frame_time = 0
        self.frame_interval = 1.0 / fps
        self.frame_skip = 2  # Procesar 1 de cada N frames
        self.frame_count = 0
        self.capture_thread = None
        self.process_thread = None
        
        logging.info("\n=== Inicializando CameraCapture ===")
        logging.info(f"- ID de cámara: {camera_id}")
        logging.info(f"- Configuración optimizada para detección: {resolution[0]}x{resolution[1]} @ {fps}fps")
        logging.info(f"- Frame skip: {self.frame_skip} (procesando 1 de cada {self.frame_skip} frames)")

    def _configure_camera(self, cap):
        """
        Configura los parámetros de la cámara optimizados para detección.
        """
        try:
            logging.info("Configurando propiedades optimizadas de la cámara...")
            
            # Buffer mínimo para menor latencia
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Configurar resolución
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            
            # Configurar FPS
            cap.set(cv2.CAP_PROP_FPS, self.fps)
            
            # Formato MJPG para mejor rendimiento
            cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            # Verificar configuración actual
            actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            logging.info("Configuración actual de la cámara:")
            logging.info(f"- Resolución: {actual_width}x{actual_height}")
            logging.info(f"- FPS: {actual_fps}")
            logging.info("- Buffer Size: 1")
            logging.info("- Formato: MJPG")
            
            return True
        except Exception as e:
            logging.error(f"Error al configurar la cámara: {str(e)}")
            return False

    def start(self):
        """Inicia la captura de la cámara."""
        try:
            logging.info(f"\n=== Iniciando cámara {self.camera_id} ===")
            
            if self.cap is None:
                # Probar diferentes backends
                for backend in [cv2.CAP_ANY, cv2.CAP_DSHOW, cv2.CAP_MSMF]:
                    if backend == cv2.CAP_ANY:
                        self.cap = cv2.VideoCapture(self.camera_id)
                    else:
                        self.cap = cv2.VideoCapture(self.camera_id + backend)
                        
                    if self.cap.isOpened():
                        logging.info(f"Cámara abierta con backend {backend}")
                        break

                if not self.cap.isOpened():
                    raise RuntimeError("No se pudo abrir la cámara con ningún backend")
                
                # Configurar propiedades
                if not self._configure_camera(self.cap):
                    raise RuntimeError("Error al configurar la cámara")

                # Realizar lectura de prueba
                logging.info("Realizando lectura de prueba...")
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    raise RuntimeError("No se pudo obtener imagen de la cámara")
                
                logging.info(f"Lectura exitosa, dimensiones del frame: {frame.shape}")
            
            # Iniciar thread de captura
            logging.info("Iniciando thread de captura...")
            self.running = True
            self.capture_thread = Thread(target=self._capture_loop)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            logging.info("=== Cámara iniciada exitosamente ===\n")
            
        except Exception as e:
            logging.error("\n!!! Error al iniciar la cámara !!!")
            logging.error(f"Detalles del error: {str(e)}")
            logging.error(traceback.format_exc())
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            raise RuntimeError(f"Error al iniciar la cámara: {str(e)}")

    def _preprocess_frame(self, frame):
        """Preprocesa el frame para detección."""
        try:
            # Mantener en BGR para la visualización, YOLO convertirá internamente
            if frame.shape[:2] != self.resolution[::-1]:
                frame = cv2.resize(frame, self.resolution, 
                                interpolation=cv2.INTER_AREA)
            
            # Normalizar contraste
            frame = cv2.normalize(frame, None, 0, 255, cv2.NORM_MINMAX)
            
            return frame
            
        except Exception as e:
            logging.error(f"Error en preprocesamiento: {str(e)}")
            return frame

    def _capture_loop(self):
        """Thread principal de captura de frames."""
        frame_count = 0
        start_time = time.time()
        last_fps_time = start_time
        
        while self.running:
            current_time = time.time()
            
            if current_time - self.last_frame_time >= self.frame_interval:
                ret, frame = self.cap.read()
                if ret:
                    with self.lock:
                        self.frame = frame
                        
                    # Procesar solo 1 de cada N frames
                    self.frame_count += 1
                    if self.frame_count % self.frame_skip == 0:
                        processed = self._preprocess_frame(frame)
                        with self.processed_lock:
                            self.processed_frame = processed
                    
                    self.last_frame_time = current_time
                    
                    # Calcular y mostrar FPS cada segundo
                    frame_count += 1
                    if current_time - last_fps_time >= 1.0:
                        fps = frame_count / (current_time - last_fps_time)
                        logging.info(f"\rFPS captura: {fps:.1f}, " + 
                                   f"FPS proceso: {fps/self.frame_skip:.1f}")
                        frame_count = 0
                        last_fps_time = current_time
                        
                else:
                    logging.warning("No se pudo leer frame")

    def get_frame(self, processed=False):
        """
        Obtiene el último frame capturado.
        Args:
            processed (bool): Si True, devuelve el frame preprocesado para detección
        """
        if processed:
            with self.processed_lock:
                if self.processed_frame is None:
                    return None
                return self.processed_frame.copy()
        else:
            with self.lock:
                if self.frame is None:
                    return None
                return self.frame.copy()

    def get_jpeg(self, quality=95):
        """
        Obtiene el último frame en formato JPEG.
        Args:
            quality (int): Calidad de compresión JPEG (0-100)
        """
        frame = self.get_frame(processed=False)
        if frame is None:
            return None
            
        # Comprimir JPEG con calidad especificada
        encode_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        ret, jpeg = cv2.imencode('.jpg', frame, encode_params)
        if ret:
            return jpeg.tobytes()
        return None

    def stop(self):
        """Detiene la captura y libera los recursos."""
        logging.info(f"Deteniendo cámara {self.camera_id}...")
        self.running = False
        if self.capture_thread is not None:
            self.capture_thread.join()
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        logging.info("Cámara detenida")

    def __del__(self):
        """Destructor que asegura la liberación de recursos."""
        self.stop()
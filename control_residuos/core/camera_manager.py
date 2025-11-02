import cv2
import time
from datetime import datetime
import json
from typing import List, Dict, Tuple, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CameraManager:
    """
    Clase que maneja la detección y gestión de cámaras.
    
    Attributes:
        active_cameras (dict): Diccionario de cámaras activas (instancias de cv2.VideoCapture)
        available_cameras (list): Lista de cámaras disponibles y sus propiedades
    """
    
    def __init__(self):
        self.active_cameras = {}
        self.available_cameras = []
        
    def test_camera(self, camera_id: int, 
                   backend: Optional[int] = None, 
                   backend_name: str = "Default") -> Optional[Dict[str, Any]]:
        """
        Prueba una cámara específica con un backend determinado.
        
        Args:
            camera_id (int): ID de la cámara a probar
            backend (int, optional): Backend de OpenCV a usar. Defaults to None.
            backend_name (str, optional): Nombre descriptivo del backend. Defaults to "Default".
        
        Returns:
            dict: Información de la cámara si es exitoso, None si falla
        """
        try:
            logger.info(f"\nProbando cámara {camera_id} con {backend_name}...")
            
            # Inicializar la cámara
            if backend is None:
                cap = cv2.VideoCapture(camera_id)
            else:
                cap = cv2.VideoCapture(camera_id + backend)
                
            if not cap.isOpened():
                logger.warning(f"✗ No se pudo abrir la cámara")
                return None
                
            # Intentar leer un frame
            ret, frame = cap.read()
            if not ret or frame is None:
                logger.warning(f"✗ No se pudo leer frame")
                cap.release()
                return None
                
            # Obtener propiedades
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            
            # Crear información de la cámara
            camera_info = {
                'id': camera_id,
                'name': f'Cámara {"Integrada" if camera_id == 0 else "USB"} ({backend_name})',
                'type': 'integrated' if camera_id == 0 else 'usb',
                'resolution': f"{width}x{height}",
                'fps': fps,
                'backend': backend_name,
                'backend_id': backend if backend is not None else cv2.CAP_ANY,
                'last_check': datetime.now().isoformat()
            }
            
            logger.info(f"✓ Cámara detectada: {width}x{height} @ {fps}fps")
            cap.release()
            return camera_info
            
        except Exception as e:
            logger.error(f"✗ Error al probar cámara {camera_id} con {backend_name}: {str(e)}")
            if 'cap' in locals():
                cap.release()
            return None
    
    def list_cameras(self, max_cameras: int = 2) -> List[Dict[str, Any]]:
        """
        Busca todas las cámaras disponibles probando diferentes backends.
        
        Args:
            max_cameras (int, optional): Número máximo de cámaras a buscar. Defaults to 2.
        
        Returns:
            list: Lista de diccionarios con información de las cámaras encontradas
        """
        logger.info("\n=== Iniciando búsqueda de cámaras ===")
        start_time = time.time()
        self.available_cameras = []
        
        # Lista de backends a probar
        backends: List[Tuple[Optional[int], str]] = [
            (None, "Default"),  # None = cv2.CAP_ANY
            (cv2.CAP_DSHOW, "DirectShow"),
            (cv2.CAP_MSMF, "Media Foundation")
        ]
        logger.info(f"Backends configurados: {backends}")
        
        # Probar cada combinación de backend e índice
        for camera_id in range(max_cameras):
            for backend, name in backends:
                camera_info = self.test_camera(camera_id, backend, name)
                if camera_info:
                    # Solo agregar si no tenemos esta cámara con mejor FPS
                    better_camera_exists = False
                    for i, cam in enumerate(self.available_cameras):
                        if cam['id'] == camera_id:
                            if camera_info['fps'] > cam['fps']:
                                # Reemplazar cámara existente con la que tiene mejor FPS
                                logger.info(f"Reemplazando cámara {camera_id} con backend que tiene mejor FPS")
                                self.available_cameras[i] = camera_info
                            better_camera_exists = True
                            break
                            
                    if not better_camera_exists:
                        self.available_cameras.append(camera_info)
        
        end_time = time.time()
        search_time = end_time - start_time
        logger.info(f"\nBúsqueda completada en {search_time:.2f} segundos")
        logger.info(f"Cámaras encontradas: {len(self.available_cameras)}")
        
        return self.available_cameras
    
    def get_camera_info(self, camera_id: int) -> Optional[Dict[str, Any]]:
        """
        Retorna la información de una cámara específica.
        
        Args:
            camera_id (int): ID de la cámara

        Returns:
            dict: Información de la cámara o None si no existe
        """
        for cam in self.available_cameras:
            if cam['id'] == camera_id:
                return cam
        return None
    
    def to_json(self) -> str:
        """
        Convierte la información de las cámaras a JSON.
        
        Returns:
            str: Representación JSON de las cámaras disponibles
        """
        return json.dumps({
            'cameras': self.available_cameras,
            'total': len(self.available_cameras),
            'last_update': datetime.now().isoformat()
        }, indent=2)

    def get_camera(self, camera_id: int):
        """
        Obtiene una instancia de CameraCapture para una cámara específica.
        
        Args:
            camera_id (int): ID de la cámara a obtener
            
        Returns:
            CameraCapture: Instancia de la cámara o None si no está disponible
        """
        from .capture_optimized import CameraCapture
        
        try:
            # Si la cámara ya está en el diccionario de cámaras activas, devolverla
            if camera_id in self.active_cameras:
                return self.active_cameras[camera_id]
            
            # Crear nueva instancia de CameraCapture
            logger.info(f"\n=== Creando nueva instancia de cámara {camera_id} ===")
            camera = CameraCapture(camera_id=camera_id)
            
            # Intentar iniciar la cámara
            logger.info("Iniciando cámara...")
            camera.start()
            
            # Si la inicialización fue exitosa, guardar en el diccionario
            self.active_cameras[camera_id] = camera
            logger.info(f"Cámara {camera_id} iniciada exitosamente")
            
            return camera
            
        except Exception as e:
            logger.error(f"Error al obtener cámara {camera_id}: {str(e)}")
            if 'camera' in locals():
                try:
                    camera.stop()
                except:
                    pass
            return None
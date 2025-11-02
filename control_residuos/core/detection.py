import cv2
import numpy as np
import os
import sys
import time
import traceback
import threading
from threading import Thread, Lock
from datetime import datetime
from collections import deque
from .camera_manager import CameraManager
import logging

# Importar configuración central
from settings import *
logger = logging.getLogger(__name__)

# Configuración específica para YOLOv8
os.environ['YOLO_VERBOSE'] = 'True'

class WasteDetector:
    def __init__(self, camera_id, confidence_threshold=None, model_path=None):
        try:
            logger.info(f"\n=== Inicializando WasteDetector ===")
            logger.info(f"Parámetros recibidos:")
            logger.info(f"- camera_id: {camera_id}")
            logger.info(f"- confidence: {confidence_threshold}")
            logger.info(f"- model_path: {model_path}")
            
            # Usar valores de la configuración central si no se proporcionan
            model_path = model_path or YOLO_MODEL_PATH
            confidence_threshold = confidence_threshold or YOLO_CONFIDENCE
            
            logger.info(f"Usando configuración:")
            logger.info(f"- model_path final: {model_path}")
            logger.info(f"- confidence final: {confidence_threshold}")
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"No se encontró el modelo en: {model_path}")
            
            if not isinstance(camera_id, (int, str)):
                raise ValueError(f"camera_id debe ser int o str, no {type(camera_id)}")
                
            self._camera_id = int(camera_id)  # Asegurar que sea entero
            
            if not isinstance(confidence_threshold, (int, float)):
                raise ValueError(f"confidence debe ser float, no {type(confidence_threshold)}")
                
            self._confidence_threshold = float(confidence_threshold)
            self._active = False
            self._detections = deque(maxlen=10)
            logger.info(f"Modelo verificado en: {model_path}")
                
        except Exception as e:
            logger.error(f"Error en inicialización: {str(e)}")
            logger.error(traceback.format_exc())
            raise
        
        # Mapeo de clases a tipos orgánico/inorgánico
        self._class_mapping = {
            'cardboard': 'inorganic',
            'glass': 'inorganic',
            'metal': 'inorganic',
            'paper': 'inorganic',
            'plastic': 'inorganic',
            'trash': 'organic'  # Asumiendo que trash incluye residuos orgánicos
        }
        self._detection_lock = Lock()
        self._stats = {
            'total': 0,
            'organic': 0,
            'inorganic': 0
        }
        self._detection_thread = None
        self._camera = None
        self.model = None
        
        # Verificar que el archivo del modelo existe
        if not os.path.exists(model_path):
            error_msg = f"No se encontró el archivo del modelo en: {model_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # Cargar modelo YOLO
        logger.info("\nIniciando carga del modelo YOLO...")
        try:
            logger.info(f"Intentando cargar modelo desde: {model_path}")
            
            # Verificar GPU
            import torch
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Dispositivo de inferencia: {device}")
            
            # Importar e instanciar YOLO
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            
            # Verificar carga exitosa
            if not hasattr(self.model, 'names'):
                raise RuntimeError("El modelo no tiene atributo 'names'")
                
                # Verificar clases
                model_classes = set(self.model.names.values())
                expected_classes = set(self._class_mapping.keys())
                logger.info(f"Clases del modelo: {model_classes}")
                logger.info(f"Clases esperadas: {expected_classes}")
                
                # Verificar coincidencia de clases
                if not any(cls.lower() in expected_classes for cls in model_classes):
                    logger.warning("ADVERTENCIA: El modelo no tiene las clases esperadas")
                    logger.warning(f"Modelo: {model_classes}")
                    logger.warning(f"Esperadas: {expected_classes}")
                
                # Optimizar modelo para máximo rendimiento
                self.model.fuse()  # Fusionar capas
                if device == 'cpu':
                    self.model.cpu()  # Forzar CPU
                else:
                    self.model.to(device)
                
                # Configurar para mejor rendimiento
                self.model.conf = self._confidence_threshold
                self.model.iou = 0.45  # Menos estricto = más rápido
                self.model.max_det = 10  # Limitar detecciones
                self.model.agnostic = True  # NMS agnóstico
                self.model.half = True  # Half precision
                
                logger.info("Modelo optimizado para rendimiento máximo")
                logger.info("Configuración del modelo aplicada:")            # Configurar el modelo para máximo rendimiento
            self.model.fuse()  # Fusionar capas para optimización
            logger.info("Modelo optimizado para inferencia")
        except Exception as e:
            error_msg = f"Error al cargar el modelo YOLO: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise RuntimeError(error_msg)

    def start(self):
        try:
            logger.info("\n=== Iniciando WasteDetector ===")
            logger.info(f"Configuración: camera_id={self._camera_id}, confidence={self._confidence_threshold}")
            logger.info(f"Estado actual: active={self._active}")
            
            # 1. Verificar si ya está activo
            if self._active:
                logger.warning(f"El detector para la cámara {self._camera_id} ya está activo")
                return True
            
            # 2. Verificar modelo YOLO
            logger.info("Verificando estado del sistema...")
            if not hasattr(self, 'model') or self.model is None:
                logger.error("Error crítico: Modelo YOLO no inicializado")
                return False
            logger.info("[OK] Modelo YOLO verificado")
            
            # 3. Verificar cámaras activas
            from web.app import active_cameras
            available_cameras = list(active_cameras.keys())
            logger.info(f"Cámaras disponibles: {available_cameras}")
            
            if self._camera_id not in active_cameras:
                logger.error(f"Error crítico: La cámara {self._camera_id} no está en la lista de cámaras activas")
                logger.error(f"Cámaras activas: {available_cameras}")
                return False
            
            # 4. Obtener y verificar la cámara
            try:
                self._camera = active_cameras[self._camera_id]
                logger.info("[OK] Referencia a cámara obtenida")
            except Exception as e:
                logger.error(f"Error crítico al obtener la cámara: {str(e)}")
                return False
            
            # 5. Verificar funcionalidad de la cámara
            logger.info("Verificando funcionamiento de la cámara...")
            test_frame = None
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    test_frame = self._camera.get_frame()
                    if test_frame is not None:
                        if len(test_frame.shape) != 3:
                            logger.error(f"Frame inválido: dimensiones incorrectas {test_frame.shape}")
                            test_frame = None
                        elif test_frame.size == 0:
                            logger.error("Frame inválido: tamaño cero")
                            test_frame = None
                        else:
                            break
                except Exception as e:
                    logger.error(f"Error al obtener frame (intento {retry_count + 1}): {str(e)}")
                
                retry_count += 1
                if retry_count < max_retries:
                    logger.warning(f"Reintentando obtener frame ({retry_count}/{max_retries})...")
                    time.sleep(1)
            
            if test_frame is None:
                logger.error("Error crítico: No se pudo obtener un frame válido de la cámara")
                logger.error("Verifique la conexión y funcionamiento de la cámara")
                return False
                
            logger.info(f"[OK] Frame de prueba obtenido: shape={test_frame.shape}, dtype={test_frame.dtype}")
                
            # 6. Verificar modelo YOLO con una detección de prueba
            logger.info("Realizando detección de prueba...")
            try:
                test_results = self.model(test_frame, verbose=False)
                if not test_results:
                    logger.error("Error crítico: El modelo no generó resultados en la detección de prueba")
                    return False
                    
                # Verificar la estructura de resultados
                if not hasattr(test_results[0], 'boxes'):
                    logger.error("Error crítico: Resultados de prueba inválidos (sin boxes)")
                    return False
                    
                logger.info("[OK] Detección de prueba exitosa")
                logger.info(f"  Resultados: {len(test_results[0].boxes)} detecciones potenciales")
                
            except Exception as e:
                logger.error("Error crítico en detección de prueba:")
                logger.error(str(e))
                logger.error(traceback.format_exc())
                return False
            
            # 7. Reiniciar estado
            logger.info("Reiniciando estado del detector...")
            with self._detection_lock:
                self._stats = {'total': 0, 'organic': 0, 'inorganic': 0}
                self._detections.clear()
            logger.info("[OK] Estado reiniciado")
            
            # 8. Iniciar thread de detección
            logger.info("Iniciando thread de detección...")
            try:
                self._active = True
                self._detection_thread = Thread(target=self._detection_loop)
                self._detection_thread.daemon = True
                
                # Guardar el thread_id para poder terminarlo si es necesario
                self._detection_thread._thread_id = None
                def get_thread_id():
                    if not self._detection_thread._thread_id:
                        for tid, tobj in threading._active.items():
                            if tobj is self._detection_thread:
                                self._detection_thread._thread_id = tid
                                break
                
                self._detection_thread.start()
                
                # Esperar brevemente y verificar que el thread está vivo
                time.sleep(0.5)
                if not self._detection_thread.is_alive():
                    logger.error("Error crítico: El thread de detección no se inició correctamente")
                    self._active = False
                    return False
                    
                # Obtener el thread ID
                get_thread_id()
                
                logger.info("[OK] Thread de detección iniciado y verificado")
                logger.info("\n=== WasteDetector iniciado exitosamente ===")
                return True
                
            except Exception as e:
                logger.error("Error crítico al iniciar el thread de detección:")
                logger.error(str(e))
                logger.error(traceback.format_exc())
                self._active = False
                return False
                
        except Exception as e:
            logger.error(f"Error al iniciar detector: {str(e)}")
            logger.error(traceback.format_exc())
            self._active = False
            return False

    def stop(self):
        logger.info(f"Deteniendo detector de cámara {self._camera_id}")
        self._active = False
        try:
            # Primero liberar la cámara para que el thread de detección no intente usarla
            self._camera = None
            logger.info("Referencia a cámara liberada")

            # Ahora esperar a que el thread termine
            if self._detection_thread and self._detection_thread.is_alive():
                logger.info("Esperando a que el thread de detección termine...")
                self._detection_thread.join(timeout=5)
                if self._detection_thread.is_alive():
                    logger.warning("El thread de detección no terminó a tiempo")
                    # Forzar la terminación del thread
                    import ctypes
                    if hasattr(self._detection_thread, '_thread_id'):
                        thread_id = self._detection_thread._thread_id
                        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), 
                            ctypes.py_object(SystemExit))
                        if res > 1:
                            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
                            logger.error('Falló la terminación forzada del thread')
                            return False
                self._detection_thread = None
                logger.info("Thread de detección terminado")

            logger.info("Detector detenido correctamente")
            return True
        except Exception as e:
            logger.error(f"Error al detener el detector: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def _detection_loop(self):
        logger.info(f"=== Iniciando bucle de detección para cámara {self._camera_id} ===")
        logger.info(f"Configuración: confidence_threshold={self._confidence_threshold}")
        
        error_count = 0
        max_errors = 5
        frame_count = 0
        last_success_time = time.time()
        
        # Verificación inicial
        if not self.model:
            logger.error("Error crítico: Modelo no inicializado")
            self._active = False
            return
            
        if not self._camera:
            logger.error("Error crítico: Cámara no inicializada")
            self._active = False
            return
            
        while self._active:
            try:
                # Verificar errores consecutivos
                if error_count >= max_errors:
                    logger.error(f"Demasiados errores consecutivos ({max_errors}), deteniendo detector")
                    self._active = False
                    break
                
                time.sleep(0.01)  # Delay mínimo para permitir otros threads
                
                try:
                    # Obtener frame de la cámara activa y procesado
                    if not self._camera:
                        logger.error("Referencia a cámara perdida")
                        self._active = False
                        break
                        
                    # Usar frame preprocesado para detección
                    frame = self._camera.get_frame(processed=True)
                    
                    if frame is None:
                        error_count += 1
                        logger.warning(f"Frame nulo recibido (error {error_count}/{max_errors})")
                        time.sleep(0.5)
                        continue
                except:
                    logger.error("Error al acceder a la cámara")
                    self._active = False
                    break
                
                # Reiniciar contador de errores si llegamos aquí
                error_count = 0
                frame_count += 1
                
                # Log periódico de estado
                current_time = time.time()
                if current_time - last_success_time >= 10:  # Log cada 10 segundos
                    fps = frame_count / (current_time - last_success_time)
                    logger.info(f"Detector funcionando - FPS: {fps:.2f} - Frames procesados: {frame_count}")
                    last_success_time = current_time
                    frame_count = 0
                
                # Convertir a RGB para YOLO
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Optimizar detección YOLOv8
                results = self.model.predict(
                    source=frame_rgb,
                    verbose=False,           # Desactivar verbose para menos logs
                    conf=self._confidence_threshold,  # Usar el umbral configurado
                    iou=0.45,               # IOU menos estricto para mejor rendimiento
                    max_det=10,             # Aumentar detecciones máximas
                    agnostic_nms=True,      # NMS agnóstico para mejor rendimiento
                    stream=True,            # Modo stream para mejor rendimiento
                    device='cpu',           # Forzar CPU para estabilidad
                    half=True              # Usar half precision para mejor rendimiento
                )
                
                detections_in_frame = 0  # Contador para este frame
                
                # Procesar resultados
                for r in results:
                    if not r.boxes:
                        continue
                        
                    boxes = r.boxes.cpu().numpy()
                    for i, box in enumerate(boxes):
                        # Obtener confianza
                        conf = float(box.conf)
                        
                        # Usar el umbral configurado
                        if conf < self._confidence_threshold:
                            continue
                            
                        # Obtener clase y validar
                        cls_id = int(box.cls[0])
                        if cls_id not in self.model.names:
                            continue
                            
                        class_name = self.model.names[cls_id].lower()
                        
                        # Validar que la clase es reconocida
                        if class_name not in self._class_mapping:
                            logger.warning(f"Clase no reconocida: {class_name}")
                            continue
                        
                        # Debug: imprimir información de detección
                        logger.info(f"Detección válida: clase={class_name}, confianza={conf:.2f}")
                        
                        # Clasificar como orgánico/inorgánico usando el mapeo
                        tipo = self._class_mapping[class_name]
                        
                        try:
                            # Obtener coordenadas del bounding box
                            x1, y1, x2, y2 = box.xyxy[0].astype(int)
                            
                            # Validar coordenadas
                            if (x1 < 0 or y1 < 0 or 
                                x2 >= frame.shape[1] or y2 >= frame.shape[0] or
                                x2 <= x1 or y2 <= y1):
                                logger.warning(f"Coordenadas inválidas: [{x1},{y1},{x2},{y2}]")
                                continue
                                
                            # Debug: imprimir coordenadas
                            logger.info(f"Bounding box: [{x1},{y1},{x2},{y2}]")
                                
                            # Registrar detección
                            with self._detection_lock:
                                self._detections.append({
                                    'timestamp': datetime.now().isoformat(),
                                    'class': tipo,
                                    'confidence': conf,
                                    'bbox': [x1, y1, x2, y2],
                                    'original_class': class_name
                                })
                                
                                # Actualizar estadísticas
                                self._stats['total'] += 1
                                self._stats[tipo] += 1
                                detections_in_frame += 1
                                
                        except Exception as bbox_error:
                            logger.error(f"Error procesando bounding box: {str(bbox_error)}")
                            continue
                
                if detections_in_frame > 0:
                    logger.info(f"Frame procesado - {detections_in_frame} detecciones encontradas")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error en el bucle de detección ({error_count}/{max_errors}): {str(e)}")
                logger.error(traceback.format_exc())
                time.sleep(1)
                
        logger.info(f"Bucle de detección terminado para cámara {self._camera_id}")

    def get_last_detections(self):
        with self._detection_lock:
            return list(self._detections)

    def draw_detections(self, frame):
        if frame is None:
            return frame

        frame_copy = frame.copy()
        
        # Dibujar las últimas detecciones
        with self._detection_lock:
            for detection in self._detections:
                bbox = detection['bbox']
                confidence = detection['confidence']
                class_name = detection['class']
                original_class = detection.get('original_class', class_name)
                
                # Color verde para orgánico, rojo para inorgánico
                color = (0, 255, 0) if class_name == 'organic' else (0, 0, 255)
                
                # Dibujar bounding box con sombra para mejor visibilidad
                cv2.rectangle(frame_copy, 
                            (bbox[0], bbox[1]), 
                            (bbox[2], bbox[3]), 
                            (0, 0, 0), 
                            4)  # Borde negro exterior
                cv2.rectangle(frame_copy, 
                            (bbox[0], bbox[1]), 
                            (bbox[2], bbox[3]), 
                            color, 
                            2)  # Borde de color interior
                
                # Preparar etiqueta con más información
                label = f"{class_name} ({original_class})"
                conf_label = f"{confidence:.2f}"
                
                # Obtener tamaño del texto para el fondo
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 2
                (label_w, label_h), _ = cv2.getTextSize(label, font, font_scale, thickness)
                (conf_w, conf_h), _ = cv2.getTextSize(conf_label, font, font_scale, thickness)
                
                # Dibujar fondo negro para la etiqueta
                cv2.rectangle(frame_copy, 
                            (bbox[0], bbox[1] - label_h - conf_h - 10),
                            (bbox[0] + max(label_w, conf_w), bbox[1]),
                            (0, 0, 0),
                            -1)  # -1 para rellenar
                
                # Dibujar textos
                cv2.putText(frame_copy, 
                          label,
                          (bbox[0], bbox[1] - conf_h - 5),
                          font,
                          font_scale,
                          color,
                          thickness)
                          
                cv2.putText(frame_copy, 
                          conf_label,
                          (bbox[0], bbox[1] - 5),
                          font,
                          font_scale,
                          (255, 255, 255),
                          thickness)
                          
                # Dibujar contador en la esquina superior izquierda
                cv2.putText(frame_copy,
                          f"Total: {self._stats['total']} | Org: {self._stats['organic']} | Inorg: {self._stats['inorganic']}",
                          (10, 30),
                          font,
                          0.7,
                          (255, 255, 255),
                          2)

        return frame_copy

    def get_stats(self):
        """Obtiene las estadísticas actuales de detección"""
        with self._detection_lock:
            return {
                'total': self._stats['total'],
                'organic': self._stats['organic'],
                'inorganic': self._stats['inorganic'],
                'recent': list(self._detections)
            }
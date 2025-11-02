from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os, sys, traceback, time
import cv2
import logging

# Importar configuración central
from settings import *

# Configurar logging
logger = logging.getLogger(__name__)

# Agregar el directorio raíz al path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
logger.info(f"Directorio raíz agregado al path: {root_dir}")

from models.models import db, User, Detection, Camera, Stats, SystemConfig
from core.capture_optimized import CameraCapture

# Inicializar el diccionario de cámaras activas
active_cameras = {}

# Diccionario para almacenar los detectores activos
active_detectors = {}

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la aplicación
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/cameras')
@login_required
def cameras():
    return render_template('cameras.html')

@app.route('/api/cameras/list', methods=['GET'])
@login_required
def list_cameras():
    """Lista todas las cámaras disponibles usando el CameraManager optimizado"""
    try:
        print("\n=== Iniciando búsqueda de cámaras ===")
        start_time = time.time()
        
        available_cameras = []
        
        print("\nProbando cámara principal...")
        # Usar CameraCapture para probar la cámara
        cap = CameraCapture(camera_id=0)
        try:
            # Intentar iniciar la cámara
            cap.start()
            
            # Si la cámara se inicia correctamente, obtener su información
            camera_info = {
                'id': 0,
                'name': 'Cámara Principal',
                'type': 'integrated',
                'resolution': f"{cap.resolution[0]}x{cap.resolution[1]}",
                'fps': cap.fps,
                'backend': 'Default'
            }
            available_cameras.append(camera_info)
            print(f"✓ Cámara principal detectada: {camera_info['resolution']} @ {camera_info['fps']}fps")
            
        except Exception as e:
            print(f"No se pudo iniciar la cámara: {str(e)}")
        finally:
            if cap:
                cap.stop()
        
        end_time = time.time()
        print(f"\nBúsqueda completada en {end_time - start_time:.2f} segundos")
        print(f"Cámaras encontradas: {len(available_cameras)}")
        
        return jsonify({
            'success': True,
            'cameras': available_cameras
        })
    except Exception as e:
        print(f"Error al listar cámaras: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camera/<int:camera_id>/start', methods=['POST'])
@login_required
def start_camera(camera_id):
    print(f"\n=== Iniciando cámara {camera_id} ===")
    try:
        if camera_id not in active_cameras:
            print(f"1. Intentando iniciar cámara {camera_id}")
            
            # Usar configuración central
            print(f"2. Creando nueva instancia de CameraCapture para cámara {camera_id}")
            width = CAMERA_WIDTH
            height = CAMERA_HEIGHT
            fps = CAMERA_FPS
            
            print(f"2. Inicializando cámara con resolución {width}x{height} @ {fps} FPS")
            cap = CameraCapture(
                camera_id=camera_id, 
                resolution=(width, height), 
                fps=fps
            )
            
            print("3. Iniciando captura...")
            cap.start()
            
            # Esperar un momento para que el thread de captura se inicie
            print("4. Esperando a que el thread de captura se inicie...")
            time.sleep(2)  # Esperar 2 segundos
            
            print("5. Verificando captura inicial...")
            test_frame = cap.get_frame()
            if test_frame is None:
                raise RuntimeError("La cámara no está proporcionando frames")
            
            print(f"6. Captura exitosa - Frame shape: {test_frame.shape}")
            active_cameras[camera_id] = cap
            print(f"=== Cámara {camera_id} iniciada exitosamente ===")
            
            # Actualizar estado de la cámara en la base de datos
            camera = Camera.query.filter_by(id=camera_id).first()
            if not camera:
                camera = Camera(id=camera_id, name=f'Cámara {camera_id}')
            camera.status = 'active'
            camera.last_active = datetime.now()
            db.session.add(camera)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Cámara {camera_id} iniciada exitosamente'
            })
        else:
            return jsonify({
                'success': True,
                'message': f'Cámara {camera_id} ya está activa'
            })
    except Exception as e:
        error_msg = f"Error al iniciar cámara {camera_id}: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error al iniciar la cámara: {str(e)}'
        }), 500

@app.route('/api/camera/<int:camera_id>/stop', methods=['POST'])
@login_required
def stop_camera(camera_id):
    """Detiene la cámara y limpia los recursos asociados"""
    try:
        if camera_id in active_cameras:
            print(f"\n=== Deteniendo cámara {camera_id} ===")
            
            # Obtener la instancia de la cámara
            camera = active_cameras[camera_id]
            
            # Detener la cámara de forma segura
            camera.stop()
            
            # Eliminar la cámara del diccionario
            del active_cameras[camera_id]
            
            # Actualizar el estado en la base de datos
            try:
                cam_db = Camera.query.filter_by(id=camera_id).first()
                if cam_db:
                    cam_db.status = 'inactive'
                    cam_db.last_active = datetime.now()
                    db.session.commit()
            except Exception as db_error:
                print(f"Error al actualizar estado en BD: {str(db_error)}")
            
            print(f"=== Cámara {camera_id} detenida exitosamente ===\n")
            return jsonify({
                'success': True,
                'message': f'Cámara {camera_id} detenida exitosamente'
            })
        else:
            print(f"Cámara {camera_id} no está activa")
            return jsonify({
                'success': True,
                'message': f'Cámara {camera_id} no estaba activa'
            })
            
    except Exception as e:
        print(f"Error al detener cámara {camera_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al detener la cámara: {str(e)}'
        }), 500

@app.route('/detection')
@login_required
def detection():
    return render_template('detection.html')

@app.route('/analysis')
@login_required
def analysis():
    stats = Stats.get_detection_stats()
    daily_stats = Stats.get_daily_stats(days=7)
    return render_template('analysis.html', stats=stats, daily_stats=daily_stats)

@app.route('/api/camera/<int:camera_id>/feed')
@login_required
def camera_feed(camera_id):
    """Proporciona el video feed de una cámara específica"""
    def generate():
        app.logger.info(f"\n=== Iniciando feed de cámara {camera_id} ===")
        
        # Verificar que la cámara está activa
        if camera_id not in active_cameras:
            app.logger.error(f"Cámara {camera_id} no está activa")
            return
            
        camera = active_cameras[camera_id]
        
        app.logger.info(f"Feed iniciado para cámara {camera_id}")
        while True:
            try:
                # Obtener frame de la cámara
                jpeg_data = camera.get_jpeg(quality=80)
                
                if jpeg_data is None:
                    app.logger.warning(f"No se pudo obtener frame de cámara {camera_id}")
                    time.sleep(0.1)
                    continue
                    
                # Enviar frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg_data + b'\r\n\r\n')
                       
            except Exception as e:
                app.logger.error(f"Error en feed de cámara {camera_id}: {str(e)}")
                app.logger.error(traceback.format_exc())
                break
                
        app.logger.info(f"=== Feed de cámara {camera_id} terminado ===")
            
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/config')
@login_required
def config():
    config = SystemConfig.query.first()
    if not config:
        config = SystemConfig()
        db.session.add(config)
        db.session.commit()
    return render_template('config.html', config=config)

@app.route('/api/detection/stats')
@login_required
def get_detection_stats():
    """Obtiene las estadísticas de detección de la cámara activa"""
    # Obtener camera_id de la URL o del cuerpo de la solicitud
    if 'camera_id' in request.args:
        camera_id = request.args.get('camera_id', type=int)
    else:
        try:
            data = request.get_json(silent=True)
            camera_id = int(data.get('camera_id')) if data else None
        except (TypeError, ValueError):
            camera_id = None

    # Validar que se recibió un camera_id válido
    if camera_id is None:
        return jsonify({
            'success': False,
            'error': 'No se especificó ID de cámara'
        }), 400

    # Verificar que existe un detector activo para esta cámara
    try:
        detector = active_detectors.get(camera_id)
        if detector is None:
            # Si no hay detector activo, devolver datos vacíos
            return jsonify({
                'success': True,
                'data': {
                    'active': False,
                    'total': 0,
                    'organic': 0,
                    'inorganic': 0,
                    'recent': []
                }
            })
            
        # Obtener estadísticas del detector activo
        try:
            stats = detector.get_stats()
            stats['active'] = True  # Agregar estado activo
            return jsonify({
                'success': True,
                'data': stats
            })
        except Exception as e:
            # Error al obtener estadísticas
            app.logger.error(f"Error al obtener estadísticas: {str(e)}")
            app.logger.error(traceback.format_exc())
            return jsonify({
                'success': True,
                'data': {
                    'active': False,
                    'error': str(e),
                    'total': 0,
                    'organic': 0,
                    'inorganic': 0,
                    'recent': []
                }
            })
            
    except Exception as e:
        app.logger.error(f"Error al acceder al detector: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camera/<int:camera_id>/detection/stream')
@login_required
def detection_stream(camera_id):
    """Proporciona el stream de video con las detecciones superpuestas"""
    def generate():
        app.logger.info(f"\n=== Iniciando stream de detección para cámara {camera_id} ===")
        
        if camera_id not in active_cameras:
            app.logger.error(f"La cámara {camera_id} no está activa")
            return
            
        if camera_id not in active_detectors:
            app.logger.error(f"No hay detector activo para la cámara {camera_id}")
            return
            
        camera = active_cameras[camera_id]
        detector = active_detectors[camera_id]
        
        app.logger.info(f"Stream iniciado para cámara {camera_id}")
        while True:
            try:
                # Obtener frame con detecciones
                frame = camera.get_frame()
                if frame is None:
                    app.logger.warning(f"No se pudo obtener frame de cámara {camera_id}")
                    time.sleep(0.1)
                    continue
                    
                # Dibujar detecciones
                frame_with_detections = detector.draw_detections(frame)
                
                # Codificar frame
                success, jpg = cv2.imencode('.jpg', frame_with_detections, [cv2.IMWRITE_JPEG_QUALITY, 80])
                if not success:
                    app.logger.warning("Error al codificar frame")
                    continue
                    
                # Enviar frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpg.tobytes() + b'\r\n\r\n')
                       
            except Exception as e:
                app.logger.error(f"Error en stream de cámara {camera_id}: {str(e)}")
                app.logger.error(traceback.format_exc())
                break
                
        app.logger.info(f"=== Stream de detección para cámara {camera_id} terminado ===")
            
    return Response(generate(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/detection/stop', methods=['POST'])
@login_required
def stop_detection():
    """Detiene la detección en una cámara específica."""
    try:
        # Obtener camera_id de la URL o del body
        camera_id = request.args.get('camera_id', type=int)
        if camera_id is None:
            try:
                data = request.get_json(silent=True)
                camera_id = data.get('camera_id') if data else None
            except Exception:
                pass
            
        if camera_id is None:
            return jsonify({
                'success': False,
                'error': 'No se especificó ID de cámara'
            }), 400
            
        # Si el detector no existe, retornar éxito ya que está detenido
        if camera_id not in active_detectors:
            return jsonify({
                'success': True,
                'message': 'La detección ya estaba detenida'
            })
            
        # Detener el detector si existe
        try:
            detector = active_detectors[camera_id]
            success = detector.stop()
            
            if success:
                # Solo eliminar del diccionario si se detuvo exitosamente
                del active_detectors[camera_id]
                return jsonify({
                    'success': True,
                    'message': 'Detección detenida exitosamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Error al detener la detección'
                }), 500
                
        except Exception as stop_error:
            app.logger.error(f"Error al detener detector: {str(stop_error)}")
            app.logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': f'Error al detener el detector: {str(stop_error)}'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Error al detener detección: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/detection/start', methods=['POST'])
@login_required
def start_detection():
    """Inicia la detección de residuos en una cámara específica."""
    try:
        import os
        
        app.logger.info("\n=== Iniciando nueva detección ===")
        data = request.get_json()
        app.logger.info(f"Datos recibidos: {data}")
        
        if not data:
            app.logger.error("No se recibieron datos en la solicitud")
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos'
            }), 400
            
        # Verificar datos completos
        if 'camera_id' not in data:
            error_msg = "No se especificó ID de cámara"
            app.logger.error(error_msg)
            return jsonify({'success': False, 'error': error_msg}), 400
            
        camera_id = int(data.get('camera_id', 0))
        confidence = float(data.get('confidence_threshold', 0.5))
        
        app.logger.info(f"Parámetros recibidos: camera_id={camera_id}, confidence={confidence}")
        
        # Verificar que la cámara está activa y funcionando
        if camera_id not in active_cameras:
            error_msg = f"La cámara {camera_id} no está activa"
            app.logger.error(error_msg)
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
        
        # Verificar que la cámara está proporcionando frames
        camera = active_cameras[camera_id]
        test_frame = camera.get_frame()
        if test_frame is None:
            error_msg = f"La cámara {camera_id} no está proporcionando frames"
            app.logger.error(error_msg)
            return jsonify({
                'success': False,
                'error': error_msg
            }), 400
            
        app.logger.info("Cámara verificada, iniciando detector...")
        
        # Verificar el estado actual del detector
        if camera_id in active_detectors:
            app.logger.info(f"Detector ya existe para cámara {camera_id}, deteniéndolo primero...")
            try:
                if not active_detectors[camera_id].stop():
                    app.logger.error(f"Error al detener detector existente para cámara {camera_id}")
                del active_detectors[camera_id]
                app.logger.info(f"Detector anterior detenido y eliminado para cámara {camera_id}")
            except Exception as e:
                app.logger.error(f"Error al detener detector existente: {str(e)}")
                app.logger.error(traceback.format_exc())
            
        # Buscar e iniciar nuevo detector
        try:
            from core.detection import WasteDetector
            app.logger.info("Creando instancia de WasteDetector...")

            # Usar el modelo configurado
            app.logger.info(f"Usando modelo: {YOLO_MODEL_PATH}")
            if not os.path.exists(YOLO_MODEL_PATH):
                error_msg = "No se encontró el modelo YOLO configurado"
                app.logger.error(error_msg)
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500
                
            model_path = YOLO_MODEL_PATH

            # Crear e iniciar el detector
            app.logger.info("Creando detector...")
            detector = WasteDetector(
                camera_id=camera_id,
                confidence_threshold=confidence,
                model_path=model_path
            )
            
            app.logger.info("Iniciando detector...")
            if not detector.start():
                error_msg = "No se pudo iniciar el detector"
                app.logger.error(error_msg)
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500
                
            app.logger.info("Detector iniciado correctamente")
            active_detectors[camera_id] = detector
            
            return jsonify({
                'success': True,
                'message': 'Detector iniciado correctamente'
            })
            
        except Exception as e:
            error_msg = f"Error al crear/iniciar el detector: {str(e)}"
            app.logger.error(error_msg)
            app.logger.error(traceback.format_exc())
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
    except Exception as e:
        print(f"Error al iniciar detección: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Error al iniciar detección: {str(e)}'
        }), 500

def init_db():
    try:
        print("Iniciando la creación de la base de datos...")
        
        # Crear todas las tablas
        db.create_all()
        print("Tablas creadas exitosamente")
        
        # Crear usuario admin si no existe
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("Creando usuario admin...")
            admin = User(username='admin')
            admin.set_password('admin')  # Cambiar esta contraseña en producción
            db.session.add(admin)
            try:
                db.session.commit()
                print("Usuario admin creado exitosamente")
            except Exception as e:
                db.session.rollback()
                print(f"Error al crear usuario admin: {str(e)}")
                raise
        else:
            print("El usuario admin ya existe")
        
        # Verificar configuración del sistema
        if not SystemConfig.query.first():
            print("Creando configuración inicial del sistema...")
            config = SystemConfig()
            db.session.add(config)
            try:
                db.session.commit()
                print("Configuración inicial creada exitosamente")
            except Exception as e:
                db.session.rollback()
                print(f"Error al crear configuración inicial: {str(e)}")
                raise
        
        print("Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")
        print(traceback.format_exc())
        return False

if __name__ == '__main__':
    with app.app_context():
        if not init_db():
            print("Error al inicializar la base de datos. Abortando...")
            sys.exit(1)
    
    # Iniciar servidor
    if AUTO_PORT:
        port = None
        max_retries = 3
        
        for retry in range(max_retries):
            try:
                if port is None:
                    port = APP_PORT
                app.logger.info(f"\nIntentando iniciar servidor en puerto {port}...")
                app.run(
                    debug=DEBUG_MODE,
                    host=APP_HOST,
                    port=port,
                    use_reloader=False
                )
                break  # Si llegamos aquí, el servidor se inició correctamente
            except OSError as e:
                if "Address already in use" in str(e) and retry < max_retries - 1:
                    port += 1  # Intentar siguiente puerto
                    app.logger.warning(f"Puerto {port-1} en uso, intentando puerto {port}")
                else:
                    app.logger.error(f"Error al iniciar servidor: {str(e)}")
                    raise  # Re-lanzar el error si no podemos recuperarnos
    else:
        # Usar puerto configurado sin reintentos
        app.logger.info(f"\nIniciando servidor en puerto {APP_PORT}...")
        app.run(
            debug=DEBUG_MODE,
            host=APP_HOST,
            port=APP_PORT,
            use_reloader=False
        )
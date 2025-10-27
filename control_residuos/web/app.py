from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os, sys, traceback, time
import cv2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import db, User, Detection, Camera, Stats, SystemConfig
from core.capture import CameraCapture

# Inicializar las cámaras
cameras = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SERVER_NAME'] = '127.0.0.1:5000'  # Forzar localhost

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
    """Lista todas las cámaras disponibles"""
    try:
        print("\n=== Iniciando búsqueda de cámaras ===")
        print("Sistema operativo:", os.name)
        print("Backend OpenCV disponibles:", [getattr(cv2, x) for x in dir(cv2) if x.startswith('CAP_')])
        start_time = time.time()
        available_cameras = []
        TIMEOUT_PER_CAMERA = 3  # segundos máximos por cámara
        
        # Lista de backends a probar
        backends = [
            (None, "Default", 0),
            (cv2.CAP_DSHOW, "DirectShow", 0),
            (cv2.CAP_MSMF, "Media Foundation", 0),
            (None, "Default", 1),
            (cv2.CAP_DSHOW, "DirectShow", 1)
        ]
        
        for backend, name, camera_id in backends:
            try:
                print(f"\nProbando cámara {camera_id} con {name}...")
                
                # Inicializar la cámara
                if backend is None:
                    cap = cv2.VideoCapture(camera_id)
                else:
                    cap = cv2.VideoCapture(camera_id + backend)
                
                if not cap.isOpened():
                    print(f"✗ No se pudo abrir la cámara {camera_id} con {name}")
                    continue
                
                # Intentar leer un frame
                ret, frame = cap.read()
                if not ret or frame is None:
                    print(f"✗ No se pudo leer frame de cámara {camera_id} con {name}")
                    cap.release()
                    continue
                
                # Obtener propiedades
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                # Verificar que no tenemos esta cámara ya
                camera_exists = False
                for cam in available_cameras:
                    if cam['id'] == camera_id:
                        camera_exists = True
                        break
                
                if not camera_exists:
                    camera_info = {
                        'id': camera_id,
                        'name': f'Cámara {"Integrada" if camera_id == 0 else "USB"} ({name})',
                        'type': 'integrated' if camera_id == 0 else 'usb',
                        'resolution': f"{width}x{height}",
                        'fps': fps,
                        'backend': name
                    }
                    available_cameras.append(camera_info)
                    print(f"✓ Cámara {camera_id} detectada con {name}")
                    print(f"  - Resolución: {width}x{height}")
                    print(f"  - FPS: {fps}")
                
                cap.release()
                
                # Si encontramos una cámara que funciona bien, no necesitamos probar más backends para ese ID
                if camera_exists:
                    continue
                    
            except Exception as e:
                print(f"✗ Error al probar cámara {camera_id} con {name}: {str(e)}")
                if 'cap' in locals():
                    cap.release()
        
        # Intentar DirectShow para cámara integrada
        try:
            print("Probando cámara integrada con DirectShow...")
            cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    fps = int(cap.get(cv2.CAP_PROP_FPS))
                    print(f"✓ Cámara integrada encontrada: {width}x{height} @ {fps}fps")
                    available_cameras.append({
                        'id': 0,
                        'name': 'Cámara Integrada (DirectShow)',
                        'type': 'integrated',
                        'resolution': f"{width}x{height}",
                        'fps': fps,
                        'backend': 'DirectShow'
                    })
            cap.release()
        except Exception as e:
            print(f"Error con DirectShow: {str(e)}")

        # Si no funcionó DirectShow, intentar con el backend predeterminado
        if not available_cameras:
            try:
                print("Probando cámara integrada con backend predeterminado...")
                cap = cv2.VideoCapture(0)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        print(f"✓ Cámara integrada encontrada: {width}x{height} @ {fps}fps")
                        available_cameras.append({
                            'id': 0,
                            'name': 'Cámara Integrada (Default)',
                            'type': 'integrated',
                            'resolution': f"{width}x{height}",
                            'fps': fps,
                            'backend': 'Default'
                        })
                cap.release()
            except Exception as e:
                print(f"Error con backend predeterminado: {str(e)}")

        # Si aún no hay cámaras, intentar con Media Foundation
        if not available_cameras:
            try:
                print("Probando cámara integrada con Media Foundation...")
                cap = cv2.VideoCapture(0 + cv2.CAP_MSMF)
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                        fps = int(cap.get(cv2.CAP_PROP_FPS))
                        print(f"✓ Cámara integrada encontrada: {width}x{height} @ {fps}fps")
                        available_cameras.append({
                            'id': 0,
                            'name': 'Cámara Integrada (MSMF)',
                            'type': 'integrated',
                            'resolution': f"{width}x{height}",
                            'fps': fps,
                            'backend': 'Media Foundation'
                        })
                cap.release()
            except Exception as e:
                print(f"Error con Media Foundation: {str(e)}")
                
        end_time = time.time()
        print(f"\nBúsqueda completada en {end_time - start_time:.2f} segundos")
        print(f"Cámaras encontradas: {len(available_cameras)}")
        
        end_time = time.time()
        print(f"\nBúsqueda completada en {end_time - start_time:.2f} segundos")
        print(f"Cámaras encontradas: {len(available_cameras)}")
        return jsonify({
            'success': True,
            'cameras': available_cameras
        })
    except Exception as e:
        print(f"Error al listar cámaras: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/camera/<int:camera_id>/start', methods=['POST'])
@login_required
def start_camera(camera_id):
    print(f"\n=== Iniciando cámara {camera_id} ===")
    try:
        if camera_id not in cameras:
            print(f"1. Intentando iniciar cámara {camera_id}")
            
            # Intentar diferentes backends
            cap = None
            frame = None
            backend_used = None
            
            backends = [
                (cv2.CAP_DSHOW, "DirectShow"),
                (cv2.CAP_MSMF, "Media Foundation"),
                (cv2.CAP_ANY, "Default")
            ]
            
            for backend, name in backends:
                try:
                    print(f"\nProbando con {name}...")
                    if backend == cv2.CAP_ANY:
                        test_cap = cv2.VideoCapture(camera_id)
                    else:
                        test_cap = cv2.VideoCapture(camera_id + backend)
                        
                    if test_cap.isOpened():
                        ret, test_frame = test_cap.read()
                        if ret and test_frame is not None:
                            print(f"✓ Conexión exitosa con {name}")
                            cap = test_cap
                            frame = test_frame
                            backend_used = name
                            break
                        test_cap.release()
                except Exception as e:
                    print(f"Error con {name}: {str(e)}")
                    if test_cap:
                        test_cap.release()
                    continue
            
            if cap is None or frame is None:
                return jsonify({
                    'success': False,
                    'error': 'No se pudo conectar con la cámara'
                }), 500
            
            print(f"2. Creando nueva instancia de CameraCapture para cámara {camera_id}")
            config = SystemConfig.query.first()
            if not config:
                print("No se encontró configuración, usando valores predeterminados")
                width, height = 640, 480
                fps = 30
            else:
                print(f"Configuración encontrada: {config.resolution}, {config.fps} FPS")
                width, height = map(int, config.resolution.split('x'))
                fps = config.fps
            
            print(f"2. Inicializando cámara con resolución {width}x{height} @ {fps} FPS")
            cap = CameraCapture(
                camera_id=camera_id,
                resolution=(width, height),
                fps=fps
            )
            
            print("3. Iniciando captura...")
            cap.start()
            
            print("4. Verificando captura inicial...")
            test_frame = cap.get_frame()
            if test_frame is None:
                raise RuntimeError("La cámara no está proporcionando frames")
            
            print(f"5. Captura exitosa - Frame shape: {test_frame.shape}")
            cameras[camera_id] = cap
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
    if camera_id in cameras:
        cameras[camera_id].stop()
        del cameras[camera_id]
    return {'success': True}

def gen_frames(camera_id):
    print(f"\n=== Iniciando generación de frames para cámara {camera_id} ===")
    
    if camera_id not in cameras:
        print(f"Error: Cámara {camera_id} no está inicializada")
        return
    
    retry_count = 0
    max_retries = 3
    frame_count = 0
    last_log_time = time.time()
    log_interval = 5  # Loguear cada 5 segundos
    
    print(f"Comenzando bucle de captura para cámara {camera_id}")
    while True:
        current_time = time.time()
        try:
            frame = cameras[camera_id].get_jpeg()
            if frame is not None:
                frame_count += 1
                if current_time - last_log_time >= log_interval:
                    print(f"Cámara {camera_id}: {frame_count} frames generados en los últimos {log_interval} segundos")
                    frame_count = 0
                    last_log_time = current_time
                
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                retry_count = 0
            else:
                retry_count += 1
                print(f"Frame nulo recibido de cámara {camera_id}, intento {retry_count}")
                if retry_count >= max_retries:
                    print(f"Demasiados frames nulos, reiniciando cámara {camera_id}")
                    try:
                        cameras[camera_id].stop()
                        time.sleep(1)  # Esperar un segundo antes de reiniciar
                        cameras[camera_id].start()
                        retry_count = 0
                    except Exception as restart_error:
                        print(f"Error al reiniciar cámara: {str(restart_error)}")
                time.sleep(0.5)  # Esperar antes de intentar de nuevo
        except Exception as e:
            print(f"Error al obtener frame de cámara {camera_id}: {str(e)}")
            print(traceback.format_exc())
            time.sleep(1)  # Pausa más larga en caso de error

@app.route('/api/camera/<int:camera_id>/stream')
@login_required
def video_feed(camera_id):
    print(f"\n=== Iniciando stream de cámara {camera_id} ===")
    if camera_id not in cameras:
        print(f"Error: Cámara {camera_id} no está iniciada")
        return "Cámara no iniciada", 404
    
    try:
        # Intentar obtener un frame de prueba
        test_frame = cameras[camera_id].get_frame()
        if test_frame is None:
            print(f"Error: No se pudo obtener frame de prueba de la cámara {camera_id}")
            return "Error al obtener frame de la cámara", 500
            
        print(f"Frame de prueba obtenido correctamente, dimensiones: {test_frame.shape}")
        print("Iniciando streaming...")
        
        return Response(
            gen_frames(camera_id),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
    except Exception as e:
        print(f"Error al iniciar stream: {str(e)}")
        print(traceback.format_exc())
        return f"Error al iniciar stream: {str(e)}", 500

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

@app.route('/api/stats')
@login_required
def get_stats():
    return {
        'detections': Stats.get_detection_stats(),
        'cameras': Stats.get_camera_stats()
    }

@app.route('/api/stats/daily')
@login_required
def get_daily_stats():
    return Stats.get_daily_stats(days=7)

@app.route('/config')
@login_required
def config():
    config = SystemConfig.query.first()
    if not config:
        config = SystemConfig()
        db.session.add(config)
        db.session.commit()
    return render_template('config.html', config=config)

@app.route('/api/config/detection', methods=['POST'])
@login_required
def update_detection_config():
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'error': 'No se recibieron datos'}, 400
        
        config = SystemConfig.query.first()
        if not config:
            config = SystemConfig()
            db.session.add(config)
        
        try:
            config.confidence_threshold = float(data.get('confidence_threshold', 0.5))
            config.detection_interval = int(data.get('detection_interval', 5))
        except ValueError as e:
            return {'success': False, 'error': f'Error en el formato de los datos: {str(e)}'}, 400
        
        try:
            db.session.commit()
            return {'success': True, 'message': 'Configuración de detección actualizada correctamente'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error al guardar en la base de datos: {str(e)}'}, 500
    except Exception as e:
        return {'success': False, 'error': f'Error del servidor: {str(e)}'}, 500

@app.route('/api/config/camera', methods=['POST'])
@login_required
def update_camera_config():
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'error': 'No se recibieron datos'}, 400
        
        config = SystemConfig.query.first()
        if not config:
            config = SystemConfig()
            db.session.add(config)
        
        resolution = data.get('resolution')
        if resolution not in ['640x480', '1280x720', '1920x1080']:
            return {'success': False, 'error': 'Resolución no válida'}, 400
            
        try:
            fps = int(data.get('fps', 30))
            if fps < 1 or fps > 60:
                return {'success': False, 'error': 'FPS debe estar entre 1 y 60'}, 400
        except ValueError:
            return {'success': False, 'error': 'FPS debe ser un número entero'}, 400
            
        config.resolution = resolution
        config.fps = fps
        
        try:
            db.session.commit()
            return {'success': True, 'message': 'Configuración de cámara actualizada correctamente'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error al guardar en la base de datos: {str(e)}'}, 500
    except Exception as e:
        return {'success': False, 'error': f'Error del servidor: {str(e)}'}, 500

@app.route('/api/config/notification', methods=['POST'])
@login_required
def update_notification_config():
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'error': 'No se recibieron datos'}, 400
        
        config = SystemConfig.query.first()
        if not config:
            config = SystemConfig()
            db.session.add(config)
        
        email = data.get('notification_email', '').strip()
        if email and '@' not in email:
            return {'success': False, 'error': 'Correo electrónico no válido'}, 400
            
        config.enable_notifications = bool(data.get('enable_notifications', False))
        config.notification_email = email
        
        try:
            db.session.commit()
            return {'success': True, 'message': 'Configuración de notificaciones actualizada correctamente'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error al guardar en la base de datos: {str(e)}'}, 500
    except Exception as e:
        return {'success': False, 'error': f'Error del servidor: {str(e)}'}, 500

@app.route('/api/config/system', methods=['POST'])
@login_required
def update_system_config():
    try:
        data = request.get_json()
        if not data:
            return {'success': False, 'error': 'No se recibieron datos'}, 400
        
        config = SystemConfig.query.first()
        if not config:
            config = SystemConfig()
            db.session.add(config)
            
        try:
            storage_days = int(data.get('storage_days', 30))
            if storage_days < 1 or storage_days > 365:
                return {'success': False, 'error': 'Días de almacenamiento debe estar entre 1 y 365'}, 400
        except ValueError:
            return {'success': False, 'error': 'Días de almacenamiento debe ser un número entero'}, 400
            
        backup_frequency = data.get('backup_frequency')
        if backup_frequency not in ['daily', 'weekly', 'monthly']:
            return {'success': False, 'error': 'Frecuencia de respaldo no válida'}, 400
            
        config.storage_days = storage_days
        config.backup_frequency = backup_frequency
        
        try:
            db.session.commit()
            return {'success': True, 'message': 'Configuración del sistema actualizada correctamente'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Error al guardar en la base de datos: {str(e)}'}, 500
    except Exception as e:
        return {'success': False, 'error': f'Error del servidor: {str(e)}'}, 500

def create_admin():
    with app.app_context():
        db.create_all()
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin')  # Change this password in production
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_admin()
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash, Response, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os, sys, traceback, time
import cv2
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.models import db, User, Detection, Camera, Stats, SystemConfig
from core.capture import CameraCapture

@app.route('/api/cameras/list', methods=['GET'])
@login_required
def list_cameras():
    """Lista todas las cámaras disponibles"""
    try:
        print("\n=== Iniciando búsqueda de cámaras ===")
        print("Sistema operativo:", os.name)
        print("OpenCV versión:", cv2.__version__)
        
        cameras = []
        start_time = time.time()
        
        # Lista de combinaciones a probar
        test_configs = [
            (0, None, "Default"),
            (0, cv2.CAP_DSHOW, "DirectShow"),
            (0, cv2.CAP_MSMF, "Media Foundation"),
            (1, None, "Default"),
            (1, cv2.CAP_DSHOW, "DirectShow")
        ]
        
        print("\nIniciando pruebas de cámara...")
        for idx, backend, name in test_configs:
            try:
                print(f"\nProbando cámara {idx} con {name}...")
                
                # Inicializar la cámara con o sin backend específico
                if backend is None:
                    cap = cv2.VideoCapture(idx)
                else:
                    cap = cv2.VideoCapture(idx + backend)
                
                if not cap.isOpened():
                    print(f"✗ No se pudo abrir la cámara")
                    continue
                
                # Intentar leer un frame
                ret, frame = cap.read()
                if not ret or frame is None:
                    print(f"✗ No se pudo leer frame")
                    cap.release()
                    continue
                
                # Si llegamos aquí, la cámara funciona
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = int(cap.get(cv2.CAP_PROP_FPS))
                
                # Solo agregar si no existe ya esta cámara
                camera_info = {
                    'id': idx,
                    'name': f'Cámara {"Integrada" if idx == 0 else "USB"} ({name})',
                    'type': 'integrated' if idx == 0 else 'usb',
                    'resolution': f"{width}x{height}",
                    'fps': fps,
                    'backend': name
                }
                
                if not any(c['id'] == idx for c in cameras):
                    cameras.append(camera_info)
                    print(f"✓ Cámara detectada:")
                    print(f"  - Resolución: {width}x{height}")
                    print(f"  - FPS: {fps}")
                
                cap.release()
                
            except Exception as e:
                print(f"Error al probar cámara {idx} con {name}:", str(e))
        
        end_time = time.time()
        search_time = end_time - start_time
        print(f"\nBúsqueda completada en {search_time:.2f} segundos")
        print(f"Cámaras encontradas: {len(cameras)}")
        
        return jsonify({
            'success': True,
            'cameras': cameras,
            'search_time': search_time
        })
        
    except Exception as e:
        error_msg = str(e)
        print(f"Error al listar cámaras: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500
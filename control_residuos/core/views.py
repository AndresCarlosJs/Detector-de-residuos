from flask import jsonify, request
from .detection import detection_system

def start_detection():
    try:
        data = request.get_json()
        camera_id = data.get('camera_id')
        confidence_threshold = data.get('confidence_threshold', 0.5)
        
        if camera_id is None:
            return jsonify({'success': False, 'error': 'ID de cámara no proporcionado'}), 400
            
        success, message = detection_system.start(camera_id, confidence_threshold)
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def stop_detection():
    try:
        success, message = detection_system.stop()
        return jsonify({'success': success, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_detection_stats():
    try:
        stats = detection_system.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
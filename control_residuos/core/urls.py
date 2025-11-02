from flask import Blueprint
from . import views

bp = Blueprint('core', __name__)

# Rutas de detección
bp.add_url_rule('/api/detection/start', 'start_detection', views.start_detection, methods=['POST'])
bp.add_url_rule('/api/detection/stop', 'stop_detection', views.stop_detection, methods=['POST'])
bp.add_url_rule('/Create New API Tokenapi/detection/stats', 'get_detection_stats', views.get_detection_stats, methods=['GET'])
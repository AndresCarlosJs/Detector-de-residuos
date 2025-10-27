from web.app import app, db
from models.models import User, Camera, Detection
from datetime import datetime, timedelta
import random

def init_sample_data():
    with app.app_context():
        # Create cameras
        cameras = [
            Camera(name='Cámara Principal', status='active', last_active=datetime.now()),
            Camera(name='Cámara Secundaria', status='inactive', last_active=datetime.now() - timedelta(hours=2))
        ]
        db.session.add_all(cameras)
        db.session.commit()

        # Create some sample detections
        waste_types = ['organico', 'inorganico']
        for _ in range(10):
            detection = Detection(
                timestamp=datetime.now() - timedelta(minutes=random.randint(1, 60)),
                camera_id=random.randint(1, 2),
                waste_type=random.choice(waste_types),
                confidence=random.uniform(0.7, 0.99)
            )
            db.session.add(detection)
        
        db.session.commit()
        print("Datos de ejemplo creados exitosamente!")

if __name__ == '__main__':
    init_sample_data()
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), default='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

class Detection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    camera_id = db.Column(db.Integer, nullable=False)
    waste_type = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='inactive')
    last_active = db.Column(db.DateTime)

    @staticmethod
    def get_active_count():
        return Camera.query.filter_by(status='active').count()

    @staticmethod
    def get_all_cameras():
        return Camera.query.all()

class DailyStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    organic_count = db.Column(db.Integer, default=0)
    inorganic_count = db.Column(db.Integer, default=0)
    total_detections = db.Column(db.Integer, default=0)
    active_time = db.Column(db.Float, default=0.0)  # tiempo activo en horas

    @staticmethod
    def get_or_create(date):
        stats = DailyStats.query.filter_by(date=date).first()
        if not stats:
            stats = DailyStats(date=date)
            db.session.add(stats)
            db.session.commit()
        return stats

class SystemConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Detección
    confidence_threshold = db.Column(db.Float, default=0.5)
    detection_interval = db.Column(db.Integer, default=5)
    
    # Cámaras
    resolution = db.Column(db.String(20), default='640x480')
    fps = db.Column(db.Integer, default=30)
    
    # Notificaciones
    enable_notifications = db.Column(db.Boolean, default=False)
    notification_email = db.Column(db.String(120))
    
    # Sistema
    storage_days = db.Column(db.Integer, default=30)
    backup_frequency = db.Column(db.String(20), default='daily')
    
    @classmethod
    def get_config(cls):
        config = cls.query.first()
        if not config:
            config = cls()
            db.session.add(config)
            db.session.commit()
        return config

class Stats:
    @staticmethod
    def get_detection_stats():
        total_detections = Detection.query.count()
        organic_waste = Detection.query.filter_by(waste_type='organico').count()
        inorganic_waste = Detection.query.filter_by(waste_type='inorganico').count()
        return {
            'total': total_detections,
            'organic': organic_waste,
            'inorganic': inorganic_waste
        }

    @staticmethod
    def get_camera_stats():
        total_cameras = Camera.query.count()
        active_cameras = Camera.query.filter_by(status='active').count()
        return {
            'total': total_cameras,
            'active': active_cameras
        }
        
    @staticmethod
    def get_daily_stats(days=7):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days-1)
        
        stats = DailyStats.query.filter(
            DailyStats.date >= start_date,
            DailyStats.date <= end_date
        ).order_by(DailyStats.date).all()
        
        return {
            'dates': [stat.date.strftime('%Y-%m-%d') for stat in stats],
            'organic': [stat.organic_count for stat in stats],
            'inorganic': [stat.inorganic_count for stat in stats],
            'total': [stat.total_detections for stat in stats],
            'active_time': [stat.active_time for stat in stats]
        }

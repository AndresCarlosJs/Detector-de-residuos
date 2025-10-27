from web.app import app, db
from models.models import User, Camera, Detection, DailyStats, SystemConfig

def reset_db():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        # Create all tables
        db.create_all()
        
        # Create admin user
        admin = User(username='admin', role='admin')
        admin.set_password('admin')
        db.session.add(admin)
        
        # Create default system configuration
        config = SystemConfig()
        db.session.add(config)
        
        db.session.commit()
        print("Base de datos reinicializada exitosamente!")

if __name__ == '__main__':
    reset_db()
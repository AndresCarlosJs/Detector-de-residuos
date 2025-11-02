"""
Herramienta unificada para administración de la base de datos.
Permite inicializar, reiniciar, y cargar datos de ejemplo.
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from models.models import db, User, Camera, SystemConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_db():
    """Inicializa la base de datos y crea las tablas necesarias."""
    try:
        logger.info("Iniciando la creación de la base de datos...")
        
        # Crear todas las tablas
        db.create_all()
        logger.info("Tablas creadas exitosamente")
        
        # Crear usuario admin si no existe
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            logger.info("Creando usuario admin...")
            admin = User(username='admin')
            admin.set_password('admin')  # Cambiar esta contraseña en producción
            db.session.add(admin)
            try:
                db.session.commit()
                logger.info("Usuario admin creado exitosamente")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error al crear usuario admin: {str(e)}")
                raise
        else:
            logger.info("El usuario admin ya existe")
        
        # Verificar configuración del sistema
        if not SystemConfig.query.first():
            logger.info("Creando configuración inicial del sistema...")
            config = SystemConfig()
            db.session.add(config)
            try:
                db.session.commit()
                logger.info("Configuración inicial creada exitosamente")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error al crear configuración inicial: {str(e)}")
                raise
        
        logger.info("Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {str(e)}")
        return False

def reset_db():
    """Elimina todas las tablas y las vuelve a crear."""
    try:
        logger.info("Reiniciando base de datos...")
        db.drop_all()
        logger.info("Tablas eliminadas")
        return init_db()
    except Exception as e:
        logger.error(f"Error al reiniciar la base de datos: {str(e)}")
        return False

def load_sample_data():
    """Carga datos de ejemplo para pruebas."""
    try:
        logger.info("Cargando datos de ejemplo...")
        
        # Crear configuración si no existe
        if not SystemConfig.query.first():
            config = SystemConfig(
                resolution='640x480',
                fps=30,
                confidence_threshold=0.5,
                detection_interval=5
            )
            db.session.add(config)
        
        # Crear algunas cámaras de ejemplo
        cameras = [
            Camera(id=0, name='Cámara Principal', type='integrated'),
            Camera(id=1, name='Cámara USB', type='usb')
        ]
        
        for camera in cameras:
            if not Camera.query.get(camera.id):
                db.session.add(camera)
        
        try:
            db.session.commit()
            logger.info("Datos de ejemplo cargados exitosamente")
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error al guardar datos de ejemplo: {str(e)}")
            raise
            
    except Exception as e:
        logger.error(f"Error al cargar datos de ejemplo: {str(e)}")
        return False

if __name__ == '__main__':
    from web.app import app
    
    with app.app_context():
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            if command == 'init':
                init_db()
            elif command == 'reset':
                reset_db()
            elif command == 'sample':
                load_sample_data()
            else:
                print("Comando no válido. Usar: init, reset, o sample")
        else:
            print("Uso: python db_admin.py [init|reset|sample]")
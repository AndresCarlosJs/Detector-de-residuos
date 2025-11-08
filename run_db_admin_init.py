import os
import sys
import traceback

# Añadir control_residuos al path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTROL_DIR = os.path.join(PROJECT_ROOT, 'control_residuos')
if CONTROL_DIR not in sys.path:
    sys.path.insert(0, CONTROL_DIR)

try:
    from flask import Flask
    import settings
    # Import db_admin which defines init_db
    import db_admin
    from models.models import db

    app = Flask(__name__)
    # Copiar configuración relevante desde settings
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = getattr(settings, 'SQLALCHEMY_TRACK_MODIFICATIONS', False)
    app.config['SECRET_KEY'] = getattr(settings, 'SECRET_KEY', 'dev')

    # Inicializar la extensión db sin importar web.app
    db.init_app(app)

    with app.app_context():
        print('Iniciando db_admin.init_db() dentro de app context...')
        success = db_admin.init_db()
        if success:
            print('db_admin.init_db() completado con éxito')
            sys.exit(0)
        else:
            print('db_admin.init_db() devolvió False; revisar logs')
            sys.exit(2)

except Exception as e:
    print('ERROR: No se pudo ejecutar la inicialización de la BD.')
    traceback.print_exc()
    sys.exit(3)

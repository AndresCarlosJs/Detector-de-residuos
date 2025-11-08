import os
import sys
import traceback

# Asegurar que el directorio control_residuos esté en sys.path para que los imports relativos funcionen
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTROL_DIR = os.path.join(PROJECT_ROOT, 'control_residuos')
if CONTROL_DIR not in sys.path:
    sys.path.insert(0, CONTROL_DIR)

try:
    # Importar la app y el objeto db desde el paquete local
    import importlib
    web_app = importlib.import_module('web.app')
    models = importlib.import_module('models.models')
    app = web_app.app
    db = models.db

    print(f"Usando proyecto raiz: {PROJECT_ROOT}")
    print(f"Control dir añadido a sys.path: {CONTROL_DIR}")

    with app.app_context():
        try:
            # Intentar establecer una conexión al motor
            conn = db.engine.connect()
            print('CONEXION_EXITOSA: Se pudo conectar a la base de datos.')
            conn.close()
            sys.exit(0)
        except Exception as e:
            print('CONEXION_FALLIDA: No se pudo conectar a la base de datos.')
            traceback.print_exc()
            sys.exit(2)

except Exception as e:
    print('ERROR_AL_IMPORTAR: No se pudo importar la aplicación o los modelos.')
    traceback.print_exc()
    sys.exit(3)

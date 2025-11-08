import os
import sys
import traceback

# Añadir control_residuos al path para importar settings
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
CONTROL_DIR = os.path.join(PROJECT_ROOT, 'control_residuos')
if CONTROL_DIR not in sys.path:
    sys.path.insert(0, CONTROL_DIR)

try:
    import settings
    from sqlalchemy import create_engine

    uri = settings.SQLALCHEMY_DATABASE_URI
    print(f"Usando URI de settings: {uri}")

    try:
        engine = create_engine(uri)
        conn = engine.connect()
        print('CONEXION_EXITOSA: Se pudo conectar a la base de datos usando SQLAlchemy create_engine().')
        conn.close()
        sys.exit(0)
    except Exception as e:
        print('CONEXION_FALLIDA: No se pudo conectar a la base de datos con SQLAlchemy.')
        traceback.print_exc()
        sys.exit(2)

except Exception as e:
    print('ERROR_AL_IMPORTAR_SETTINGS: No se pudo importar settings.py o sqlalchemy.')
    traceback.print_exc()
    sys.exit(3)

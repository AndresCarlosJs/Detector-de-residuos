import os
import sys

# Agregar el directorio raíz al PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

print(f"Directorio actual: {current_dir}")
print(f"Directorio padre: {parent_dir}")

try:
    from web.app import app
except ImportError as e:
    print(f"Error al importar la aplicación: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

if __name__ == '__main__':
    print("Iniciando servidor...")
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000
    )
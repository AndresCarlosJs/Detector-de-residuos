#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de ejecucion simplificado para el sistema
"""

import os
import sys

# Agregar el directorio raiz al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Agregar el directorio de control_residuos al path
sys.path.insert(0, os.path.join(BASE_DIR, 'control_residuos'))

# Importar configuración y app
from settings import *
from web.app import app

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SISTEMA DE CONTROL DE RESIDUOS")
    print("="*60)
    print(f"\nServidor iniciado en http://{APP_HOST}:{APP_PORT}")
    print("Usuario: admin / Password: admin")
    print("\nPresiona CTRL+C para detener\n")
    app.run(
        debug=DEBUG_MODE, 
        host=APP_HOST, 
        port=APP_PORT, 
        use_reloader=False
    )

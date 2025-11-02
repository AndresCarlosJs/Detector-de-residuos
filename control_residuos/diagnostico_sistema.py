import os
import sys
import logging
import psycopg2
import traceback
from config import DB_CONFIG, MODEL_CONFIG

def verificar_directorio():
    print("\n=== Verificación de Directorios ===")
    directorio_actual = os.getcwd()
    print(f"Directorio actual: {directorio_actual}")
    
    # Verificar estructura de directorios
    directorios_requeridos = ['logs', 'instance', 'web/static', 'web/templates']
    for dir in directorios_requeridos:
        path = os.path.join(directorio_actual, dir)
        existe = os.path.exists(path)
        print(f"✓ {dir:15} {'EXISTE' if existe else 'NO EXISTE'}")

def verificar_modelo_yolo():
    print("\n=== Verificación del Modelo YOLO ===")
    modelo_path = MODEL_CONFIG['path']
    existe = os.path.exists(modelo_path)
    print(f"Modelo YOLO: {modelo_path}")
    print(f"Estado: {'✓ EXISTE' if existe else '✗ NO EXISTE'}")
    if existe:
        tamano = os.path.getsize(modelo_path) / (1024*1024)  # Convertir a MB
        print(f"Tamaño: {tamano:.2f} MB")

def verificar_base_datos():
    print("\n=== Verificación de Base de Datos ===")
    print("Configuración:")
    for key, value in DB_CONFIG.items():
        if key != 'password':  # No mostrar la contraseña
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: ****")
    
    try:
        # Intentar conexión
        print("\nIntentando conexión...")
        conn = psycopg2.connect(
            dbname=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port']
        )
        
        # Verificar tablas
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tablas = cur.fetchall()
        
        print("✓ Conexión exitosa")
        print("\nTablas encontradas:")
        for tabla in tablas:
            print(f"  - {tabla[0]}")
            
        cur.close()
        conn.close()
        print("\n✓ Verificación de base de datos completada")
        return True
        
    except Exception as e:
        print(f"\n✗ Error de conexión: {str(e)}")
        print("\nDetalles del error:")
        print(traceback.format_exc())
        return False

def verificar_dependencias():
    print("\n=== Verificación de Dependencias ===")
    dependencias = [
        ('flask', 'Flask'), 
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy'),
        ('ultralytics', 'ultralytics'),
        ('psycopg2', 'psycopg2'),
        ('sqlalchemy', 'sqlalchemy')
    ]
    
    for package, module in dependencias:
        try:
            __import__(module)
            print(f"✓ {package:15} instalado correctamente")
        except ImportError as e:
            print(f"✗ {package:15} NO instalado o con error: {str(e)}")

def main():
    print("=== Iniciando Diagnóstico del Sistema ===")
    
    verificar_directorio()
    verificar_modelo_yolo()
    verificar_dependencias()
    db_ok = verificar_base_datos()
    
    print("\n=== Resumen del Diagnóstico ===")
    if not db_ok:
        print("\n⚠️  Se encontraron problemas con la base de datos")
        print("Sugerencias:")
        print("1. Verificar que PostgreSQL está instalado y en ejecución")
        print("2. Verificar las credenciales en config.py")
        print("3. Asegurar que la base de datos 'residuos_db' existe")
        print("\nPara crear la base de datos, ejecutar en PostgreSQL:")
        print("CREATE DATABASE residuos_db;")
    else:
        print("\n✓ Todos los sistemas funcionando correctamente")

if __name__ == "__main__":
    main()
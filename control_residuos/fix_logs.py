import os
import re

def replace_in_file(filepath, old_pattern, new_pattern):
    try:
        # Leer el archivo
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Realizar el reemplazo
        new_content = content.replace(old_pattern, new_pattern)
        
        # Escribir el archivo
        with open(filepath, 'w', encoding='utf-8', newline='\n') as file:
            file.write(new_content)
            
        return True
    except Exception as e:
        print(f"Error al procesar {filepath}: {str(e)}")
        return False

def main():
    # Archivo a procesar
    detection_py = os.path.join('core', 'detection.py')
    
    # Lista de reemplazos a realizar
    replacements = [
        ('logger.info("✓ Modelo YOLO verificado")', 'logger.info("[OK] Modelo YOLO verificado")'),
        ('logger.info("✓ Referencia a cámara obtenida")', 'logger.info("[OK] Referencia a cámara obtenida")'),
        ('logger.info(f"✓ Frame de prueba obtenido:', 'logger.info(f"[OK] Frame de prueba obtenido:'),
        ('logger.info("✓ Detección de prueba exitosa")', 'logger.info("[OK] Detección de prueba exitosa")'),
        ('logger.info("✓ Estado reiniciado")', 'logger.info("[OK] Estado reiniciado")'),
        ('logger.info("✓ Thread de detección iniciado y verificado")', 'logger.info("[OK] Thread de detección iniciado y verificado")')
    ]
    
    print(f"Procesando {detection_py}...")
    
    # Realizar cada reemplazo
    for old, new in replacements:
        if replace_in_file(detection_py, old, new):
            print(f"Reemplazado: {old} -> {new}")
        else:
            print(f"Error al reemplazar: {old}")
    
    print("Proceso completado")

if __name__ == '__main__':
    main()
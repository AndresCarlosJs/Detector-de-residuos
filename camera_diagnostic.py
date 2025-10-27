import cv2
import platform
import sys
import os
import time

def print_section(title):
    print(f"\n{'='*20} {title} {'='*20}")

def test_camera_backends():
    print_section("Prueba de Backends de Cámara")
    
    backends = [
        (cv2.CAP_ANY, "Default"),
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation")
    ]
    
    for camera_id in range(4):  # Probar las primeras 4 cámaras
        print(f"\nProbando cámara {camera_id}:")
        for backend, name in backends:
            print(f"\nIntentando con {name}...")
            try:
                if backend == cv2.CAP_ANY:
                    cap = cv2.VideoCapture(camera_id)
                else:
                    cap = cv2.VideoCapture(camera_id + backend)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret:
                        print(f"✓ Éxito con {name}")
                        print(f"  - Resolución: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                        print(f"  - FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")
                        # Guardar un frame de prueba
                        filename = f"camera_{camera_id}_{name.lower()}_test.jpg"
                        cv2.imwrite(filename, frame)
                        print(f"  - Frame de prueba guardado como: {filename}")
                    else:
                        print(f"✗ No se pudo leer frame con {name}")
                else:
                    print(f"✗ No se pudo abrir la cámara con {name}")
                cap.release()
            except Exception as e:
                print(f"✗ Error con {name}: {str(e)}")

def check_system_info():
    print_section("Información del Sistema")
    print(f"Sistema Operativo: {platform.system()} {platform.release()}")
    print(f"Versión de Python: {sys.version}")
    print(f"Versión de OpenCV: {cv2.__version__}")
    print(f"Arquitectura: {platform.machine()}")
    print(f"Procesador: {platform.processor()}")

def check_running_processes():
    print_section("Procesos en Uso de Cámara")
    if platform.system() == 'Windows':
        try:
            import psutil
            camera_processes = []
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    # Lista de nombres comunes de procesos que pueden usar la cámara
                    camera_apps = ['zoom.exe', 'teams.exe', 'skype.exe', 'discord.exe', 'chrome.exe', 'firefox.exe', 'msedge.exe']
                    if proc.info['name'].lower() in camera_apps:
                        camera_processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if camera_processes:
                print("Procesos que podrían estar usando la cámara:")
                for proc in camera_processes:
                    print(f"- {proc}")
            else:
                print("No se detectaron procesos comunes que usen la cámara")
        except ImportError:
            print("No se pudo verificar procesos (psutil no instalado)")
    else:
        print("Verificación de procesos solo disponible en Windows")

def check_permissions():
    print_section("Verificación de Permisos")
    if platform.system() == 'Windows':
        try:
            import winreg
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\webcam", 0, winreg.KEY_READ)
                print("✓ Acceso al registro de permisos de cámara")
                winreg.CloseKey(key)
            except Exception as e:
                print(f"✗ Error al verificar permisos en el registro: {str(e)}")
        except ImportError:
            print("No se pudo verificar permisos del registro")
    else:
        print("Verificación de permisos solo disponible en Windows")

if __name__ == "__main__":
    print("\n=== Iniciando Diagnóstico de Cámara ===\n")
    
    try:
        check_system_info()
        check_permissions()
        check_running_processes()
        test_camera_backends()
        
        print("\n=== Diagnóstico Completado ===")
    except Exception as e:
        print(f"\n❌ Error durante el diagnóstico: {str(e)}")
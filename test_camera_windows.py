import cv2
import subprocess
import json

def get_camera_info():
    """Obtiene información sobre las cámaras usando PowerShell"""
    print("\n=== Buscando cámaras en Windows ===")
    
    try:
        # Comando PowerShell para listar dispositivos de cámara
        ps_command = """
        Get-PnpDevice | Where-Object {$_.Class -eq 'Camera' -or $_.Class -eq 'Image'} | Select-Object Status,Class,FriendlyName,InstanceId | ConvertTo-Json
        """
        
        # Ejecutar el comando PowerShell
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            devices = json.loads(result.stdout)
            if not isinstance(devices, list):
                devices = [devices]
            
            print("\nCámaras detectadas por Windows:")
            for device in devices:
                print(f"\n- Nombre: {device.get('FriendlyName', 'Desconocido')}")
                print(f"  Estado: {device.get('Status', 'Desconocido')}")
                print(f"  Clase: {device.get('Class', 'Desconocido')}")
                print(f"  ID: {device.get('InstanceId', 'Desconocido')}")
        else:
            print("No se encontraron cámaras en el sistema")
            
    except Exception as e:
        print(f"Error al obtener información de cámaras: {str(e)}")
    
    # Intentar abrir cada cámara con diferentes métodos
    print("\nProbando acceso a cámaras:")
    for i in range(10):  # Probar los primeros 10 índices
        try:
            # Probar con DirectShow
            cap = cv2.VideoCapture(i + cv2.CAP_DSHOW)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"\n✓ Cámara {i} (DirectShow):")
                    print(f"  Resolución: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                    print(f"  FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")
                    # Guardar frame de prueba
                    cv2.imwrite(f'camera_{i}_test.jpg', frame)
                    print(f"  Frame guardado como: camera_{i}_test.jpg")
            cap.release()
            
            # Probar con índice directo
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"\n✓ Cámara {i} (Direct):")
                    print(f"  Resolución: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                    print(f"  FPS: {int(cap.get(cv2.CAP_PROP_FPS))}")
            cap.release()
            
        except Exception as e:
            print(f"Error al probar cámara {i}: {str(e)}")
            continue

if __name__ == "__main__":
    get_camera_info()
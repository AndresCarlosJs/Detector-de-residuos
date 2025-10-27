import subprocess
import os
import sys
from pathlib import Path

def install_mkcert():
    try:
        # Verificar si mkcert está instalado
        subprocess.run(['mkcert', '-version'], capture_output=True)
        print("mkcert ya está instalado")
        return True
    except FileNotFoundError:
        print("mkcert no está instalado. Por favor, instala mkcert siguiendo estas instrucciones:")
        print("\n1. Usando Chocolatey (recomendado):")
        print("   Abre PowerShell como administrador y ejecuta:")
        print("   choco install mkcert")
        print("\n2. Manualmente:")
        print("   Descarga mkcert desde: https://github.com/FiloSottile/mkcert/releases")
        print("   Y añádelo al PATH del sistema")
        return False

def setup_certificates():
    cert_dir = Path(__file__).parent
    cert_path = cert_dir / "localhost.pem"
    key_path = cert_dir / "localhost-key.pem"

    if cert_path.exists() and key_path.exists():
        print("Los certificados ya existen")
        return str(cert_path), str(key_path)

    if not install_mkcert():
        sys.exit(1)

    # Crear directorio si no existe
    cert_dir.mkdir(parents=True, exist_ok=True)

    # Instalar la CA local
    subprocess.run(['mkcert', '-install'], check=True)

    # Generar certificados
    subprocess.run([
        'mkcert',
        '-cert-file', str(cert_path),
        '-key-file', str(key_path),
        'localhost',
        '127.0.0.1',
        '::1'
    ], check=True)

    print(f"\nCertificados generados exitosamente:")
    print(f"Certificado: {cert_path}")
    print(f"Llave privada: {key_path}")

    return str(cert_path), str(key_path)

if __name__ == '__main__':
    setup_certificates()
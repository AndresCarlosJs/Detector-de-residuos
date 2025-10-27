from OpenSSL import crypto
import os

def create_self_signed_cert():
    # Generar clave privada
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Generar certificado
    cert = crypto.X509()
    cert.get_subject().C = "ES"
    cert.get_subject().ST = "Estado"
    cert.get_subject().L = "Ciudad"
    cert.get_subject().O = "Control Residuos"
    cert.get_subject().OU = "Desarrollo"
    cert.get_subject().CN = "localhost"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Válido por un año
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    # Guardar certificado y clave privada
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

if __name__ == '__main__':
    create_self_signed_cert()
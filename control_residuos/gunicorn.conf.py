# Configuración de Gunicorn para producción
bind = '0.0.0.0:8000'
workers = 3  # Número recomendado es (2 x núcleos) + 1
worker_class = 'sync'
threads = 2
timeout = 60
keepalive = 5

# Configuración de logs
accesslog = 'logs/access.log'
errorlog = 'logs/error.log'
loglevel = 'info'

# Configuración de seguridad
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
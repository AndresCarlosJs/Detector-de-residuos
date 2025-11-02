import logging
import os
import sys
import codecs

def setup_logging(name, log_file=None):
    """
    Configura un logger con codificación UTF-8 y salida formateada.
    
    Args:
        name (str): Nombre del logger
        log_file (str, opcional): Ruta al archivo de log. Si no se proporciona,
                                solo se usa la salida estándar.
    
    Returns:
        logging.Logger: Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Formato consistente para todos los handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para consola con codificación UTF-8
    if sys.stdout.encoding != 'utf-8':
        if hasattr(sys.stdout, 'detach'):
            utf8_stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            console_handler = logging.StreamHandler(utf8_stdout)
        else:
            console_handler = logging.StreamHandler(sys.stdout)
    else:
        console_handler = logging.StreamHandler(sys.stdout)
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Si se especificó un archivo de log, agregar FileHandler
    if log_file:
        # Asegurar que el directorio existe
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Constantes para símbolos de estado
OK = "[OK]"
ERROR = "[ERROR]"
WARNING = "[WARN]"
INFO = "[INFO]"
# 🗑️ Sistema de Control de Residuos

Sistema web completo para detección y clasificación de residuos en tiempo real usando visión por computadora.

## 🎯 Características Principales

### ✨ Detección Inteligente
- ✅ **YOLOv8 Preentrenado**: Detección en tiempo real sin entrenar modelos
- ✅ **Múltiples Clases**: 16+ objetos detectables (comida, botellas, utensilios, etc.)
- ✅ **Clasificación Automática**: Orgánico vs Inorgánico
- ✅ **Confianza Configurable**: Ajuste fino de sensibilidad

### 📹 Gestión de Cámaras
- ✅ Múltiples cámaras simultáneas
- ✅ Streaming en tiempo real
- ✅ Resolución configurable (640x480, 1280x720, 1920x1080)
- ✅ FPS optimizado (hasta 30 FPS)
- ✅ Autodetección de backends (DirectShow, Media Foundation)

### 📊 Dashboard y Análisis
- ✅ Estadísticas en tiempo real
- ✅ Gráficos de tendencias
- ✅ Historial de detecciones
- ✅ Reportes diarios

### 🔐 Seguridad
- ✅ Autenticación de usuarios
- ✅ Roles (Admin/Usuario)
- ✅ Base de datos PostgreSQL
- ✅ API RESTful

## 🚀 Instalación

### Requisitos Previos

```bash
# Python 3.8+
python --version

# PostgreSQL
psql --version

# Node.js (opcional, para desarrollo frontend)
node --version
```

### Instalación Paso a Paso

```bash
# 1. Clonar repositorio
git clone <tu-repositorio>
cd ControlResiduos

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r control_residuos/requirements.txt

# 5. Configurar ajustes
# Edita control_residuos/settings.py según tus necesidades:
#   - Configuración de PostgreSQL
#   - Configuración del servidor web
#   - Configuración de YOLOv8
#   - Configuración de cámaras

# 6. Ejecutar aplicación
python run_app.py
```

## 🎮 Uso

### Primera Ejecución

1. **Acceder al sistema**: http://localhost:5000
2. **Credenciales por defecto**:
   - Usuario: `admin`
   - Contraseña: `admin`
3. **Cambiar contraseña** inmediatamente en producción

### Flujo de Trabajo

1. **Iniciar Cámara**
   - Ir a "Control de Cámaras"
   - Seleccionar cámara disponible
   - Clic en "Iniciar Cámara"

2. **Configurar Detección**
   - Ir a "Detección de Residuos"
   - Ajustar umbral de confianza (recomendado: 0.5)
   - Clic en "Iniciar Detección"

3. **Ver Resultados**
   - Observar streaming con bounding boxes
   - Revisar estadísticas en tiempo real
   - Ver historial en "Análisis y Estadísticas"

## 🔍 Detección YOLOv8

### Objetos Detectables

#### Residuos Orgánicos 🍎
- Bananas, Manzanas, Naranjas
- Broccoli, Zanahorias
- Sandwiches, Hot dogs
- Pizza, Donuts, Pastel

#### Residuos Inorgánicos 🍾
- Botellas, Vasos, Tazones
- Tenedores, Cuchillos, Cucharas

### Mapeo Automático

El sistema mapea automáticamente objetos detectados por COCO (80 clases) a categorías de residuos:

```
🍌 banana  → organic
🍎 apple   → organic
🍾 bottle  → inorganic
🥄 spoon   → inorganic
```

## 📁 Estructura del Proyecto

```
ControlResiduos/
├── control_residuos/
│   ├── core/                      # Lógica principal
│   │   ├── camera_manager.py      # Gestión de cámaras
│   │   ├── camera_backend.py      # Backends de cámara
│   │   ├── capture_optimized.py   # Captura optimizada
│   │   ├── detection.py           # Detección YOLOv8 ⭐
│   │   ├── views.py               # Endpoints API
│   │   └── ...
│   ├── models/
│   │   └── models.py              # Modelos de base de datos
│   ├── web/
│   │   ├── app.py                 # Aplicación Flask
│   │   ├── templates/             # HTML
│   │   │   ├── dashboard.html
│   │   │   ├── cameras.html
│   │   │   ├── detection.html
│   │   │   └── ...
│   │   └── static/                # CSS, JS
│   ├── config.py                  # Configuración
│   ├── init_db.py                 # Inicialización BD
│   └── run.py                     # Script de inicio
├── requirements.txt               # Dependencias
├── test_yolo_detection.py        # Prueba YOLOv8
├── DETECCIÓN_RESIDUOS.md         # Documentación detección
└── DATASETS_RESIDUOS.md          # Guía de datasets
```

## 🧪 Pruebas

### Prueba de Cámara
```bash
python test_camera_final.py
```

### Prueba de YOLOv8
```bash
python test_yolo_detection.py
```

### Prueba de Resolución
```bash
python test_resolucion.py
```

## 🛠️ Desarrollo

### Agregar Nuevas Clases

Edita `control_residuos/core/detection.py`:

```python
_class_mapping = {
    'cardboard': 'inorganic',
    'glass': 'inorganic',
    'metal': 'inorganic',
    'paper': 'inorganic',
    'plastic': 'inorganic',
    'trash': 'organic'
}
```

### Configuración Avanzada

Edita `control_residuos/settings.py`:

```python
# Configuración de la base de datos PostgreSQL
DB_HOST = 'localhost'
DB_PORT = 5432
DB_NAME = 'control_residuos'
DB_USER = 'postgres'
DB_PASSWORD = 'postgres'

# Configuración del servidor web
APP_HOST = '127.0.0.1'
APP_PORT = 5000
DEBUG_MODE = False

# Configuración de YOLOv8
YOLO_MODEL_PATH = 'yolov8n.pt'
YOLO_CONFIDENCE = 0.25

# Configuración de cámaras
MAX_CAMERAS = 4
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
```

## 📊 Base de Datos

### Modelos Principales

- **User**: Usuarios y autenticación
- **Camera**: Cámaras y estado
- **Detection**: Detecciones registradas
- **DailyStats**: Estadísticas diarias
- **SystemConfig**: Configuración del sistema

### Inicializar Datos de Prueba

```bash
python control_residuos/init_sample_data.py
```

## 🚀 Despliegue

### Desarrollo Local

```bash
python control_residuos/run.py
```

### Producción con Gunicorn

```bash
gunicorn -c control_residuos/gunicorn.conf.py control_residuos.web.app:app
```

### Docker (Próximamente)

```bash
docker-compose up -d
```

## 📈 Optimizaciones

- ✅ Buffer mínimo (latencia reducida)
- ✅ Threading para captura paralela
- ✅ YOLOv8n (modelo nano, rápido)
- ✅ Detección espaciada (cada 2 seg)
- ✅ MJPG codec para performance
- ✅ Resolución 640x480 por defecto

## 🐛 Solución de Problemas

### Cámara no se abre

```bash
# Verificar cámaras disponibles
python test_camera_final.py
```

### YOLOv8 no funciona

```bash
# Reinstalar
pip uninstall ultralytics
pip install ultralytics==8.0.196

# Verificar instalación
python -c "from ultralytics import YOLO; print('OK')"
```

### Base de datos error

```bash
# Reinicializar base de datos
python control_residuos/drop_database.py
python control_residuos/init_db.py
```

## 📚 Documentación Adicional

- **DETECCIÓN_RESIDUOS.md**: Guía completa de detección YOLOv8
- **DATASETS_RESIDUOS.md**: Lista de datasets y cómo integrarlos

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/NuevaFuncion`)
3. Commit cambios (`git commit -am 'Agregar nueva función'`)
4. Push a la rama (`git push origin feature/NuevaFuncion`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver `LICENSE` para más detalles.

## 👥 Autores

- Tu nombre aquí

## 🙏 Agradecimientos

- [Ultralytics](https://ultralytics.com/) - YOLOv8
- [OpenCV](https://opencv.org/) - Visión por computadora
- [Flask](https://flask.palletsprojects.com/) - Framework web
- [COCO Dataset](https://cocodataset.org/) - Dataset de objetos

## 📞 Contacto

Para preguntas o soporte:
- Email: tu-email@ejemplo.com
- Issues: Abre un issue en GitHub
- Documentación: Ver archivos .md en el proyecto

---

**¡Gracias por usar el Sistema de Control de Residuos!** 🎉


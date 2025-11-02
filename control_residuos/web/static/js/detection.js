// Variables globales
let detectionActive = false;
let selectedCamera = null;
let statisticsInterval = null;

// Elementos DOM
const cameraSelect = document.getElementById('detection-camera');
const confidenceThreshold = document.getElementById('confidence-threshold');
const startButton = document.getElementById('start-detection');
const stopButton = document.getElementById('stop-detection');
const detectionStream = document.getElementById('detection-stream');
const detectionPlaceholder = document.getElementById('detection-placeholder');

// Función para actualizar la lista de cámaras
async function updateCameraList() {
    try {
        const response = await fetch('/api/cameras/list');
        const data = await response.json();
        
        if (data.success) {
            // Limpiar lista actual
            cameraSelect.innerHTML = '';
            
            // Agregar cámaras disponibles
            data.cameras.forEach(camera => {
                const option = document.createElement('option');
                option.value = camera.id;
                option.textContent = `${camera.name} (${camera.resolution})`;
                cameraSelect.appendChild(option);
            });
            
            // Habilitar/deshabilitar el selector según haya cámaras
            cameraSelect.disabled = data.cameras.length === 0;
            startButton.disabled = data.cameras.length === 0;
            
            if (data.cameras.length === 0) {
                showAlert('No hay cámaras disponibles', 'warning');
            }
        } else {
            showAlert('Error al obtener lista de cámaras', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error de conexión', 'error');
    }
}

// Función para iniciar la detección
async function startDetection() {
    try {
        const cameraId = parseInt(cameraSelect.value);
        const confidence = parseFloat(confidenceThreshold.value);
        
        console.log('Iniciando detección para cámara:', cameraId);
        
        // Iniciar cámara si no está activa
        const startResponse = await fetch(`/api/camera/${cameraId}/start`, {
            method: 'POST'
        });
        
        if (!startResponse.ok) {
            const error = await startResponse.json();
            throw new Error(error.error || 'Error al iniciar la cámara');
        }
        
        console.log('Cámara iniciada, iniciando detección...');
        
        // Iniciar detección
        const detectionResponse = await fetch(`/api/detection/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                camera_id: cameraId,
                confidence_threshold: confidence
            })
        });
        
        if (!detectionResponse.ok) {
            const error = await detectionResponse.json();
            throw new Error(error.error || 'Error al iniciar la detección');
        }
        
        // Actualizar UI
        detectionActive = true;
        selectedCamera = cameraId;
        updateControlState();
        
        // Pequeño delay para asegurar que el detector esté listo
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Iniciar stream de video con detecciones
        const streamUrl = `/api/camera/${cameraId}/detection/stream?t=${Date.now()}`;
        console.log('Iniciando stream de detección:', streamUrl);
        
        // Asegurar que la imagen anterior se limpie
        detectionStream.src = '';
        
        // Configurar manejadores de eventos para la imagen
        detectionStream.onload = () => console.log('Stream cargado correctamente');
        detectionStream.onerror = (e) => console.error('Error al cargar stream:', e);
        
        // Cargar nuevo stream
        detectionStream.src = streamUrl;
        detectionStream.classList.remove('d-none');
        detectionPlaceholder.classList.add('d-none');
        
        // Iniciar actualización de estadísticas
        startStatisticsUpdate();
        
        showAlert('Detección iniciada', 'success');
        
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error al iniciar la detección', 'error');
        stopDetection();
    }
}

// Función para detener la detección
async function stopDetection() {
    try {
        if (selectedCamera !== null) {
            // Detener detección
            await fetch(`/api/detection/stop?camera_id=${selectedCamera}`, {
                method: 'POST'
            });
            
            // Detener cámara
            await fetch(`/api/camera/${selectedCamera}/stop`, {
                method: 'POST'
            });
        }
    } catch (error) {
        console.error('Error al detener:', error);
    } finally {
        // Limpiar UI
        detectionActive = false;
        selectedCamera = null;
        detectionStream.src = '';
        detectionStream.classList.add('d-none');
        detectionPlaceholder.classList.remove('d-none');
        updateControlState();
        stopStatisticsUpdate();
    }
}

// Función para actualizar estadísticas
async function updateStatistics() {
    try {
        if (selectedCamera === null) return;
        
        const response = await fetch(`/api/detection/stats?camera_id=${selectedCamera}`);
        const data = await response.json();
        
        if (data.success) {
            const stats = data.data;
            // Actualizar contadores
            document.querySelector('[data-stat="total"]').textContent = stats.total || 0;
            document.querySelector('[data-stat="organic"]').textContent = stats.organic || 0;
            document.querySelector('[data-stat="inorganic"]').textContent = stats.inorganic || 0;
            
            // Actualizar tabla de detecciones recientes
            const tbody = document.querySelector('#recent-detections');
            if (stats.recent && Array.isArray(stats.recent)) {
                tbody.innerHTML = stats.recent.map(detection => `
                    <tr>
                        <td>${new Date(detection.timestamp).toLocaleTimeString()}</td>
                        <td>Cámara ${detection.camera_id}</td>
                        <td>${detection.class}</td>
                        <td>${(detection.confidence * 100).toFixed(1)}%</td>
                    </tr>
                `).join('');
            }
        }
    } catch (error) {
        console.error('Error al actualizar estadísticas:', error);
    }
}

// Función para iniciar actualización de estadísticas
function startStatisticsUpdate() {
    updateStatistics();  // Actualización inicial
    statisticsInterval = setInterval(updateStatistics, 1000);  // Actualizar cada segundo
}

// Función para detener actualización de estadísticas
function stopStatisticsUpdate() {
    if (statisticsInterval) {
        clearInterval(statisticsInterval);
        statisticsInterval = null;
    }
}

// Función para actualizar estado de controles
function updateControlState() {
    cameraSelect.disabled = detectionActive;
    confidenceThreshold.disabled = detectionActive;
    startButton.disabled = detectionActive;
    stopButton.disabled = !detectionActive;
}

// Función para mostrar alertas
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-cerrar después de 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    updateCameraList();
    updateControlState();
});

startButton.addEventListener('click', startDetection);
stopButton.addEventListener('click', stopDetection);

// Actualizar valor mostrado del umbral de confianza
confidenceThreshold.addEventListener('input', (e) => {
    document.getElementById('confidence-value').textContent = e.target.value;
});

// Manejar cambios en la selección de cámara
cameraSelect.addEventListener('change', async () => {
    if (!detectionActive) {
        updateControlState();
    }
});
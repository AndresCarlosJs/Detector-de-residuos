// Control de cámaras
function showMessage(message, type = 'danger') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    // Eliminar alertas anteriores
    document.querySelectorAll('.alert').forEach(alert => alert.remove());
    document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
}

function getBrowserName() {
    if (navigator.userAgent.indexOf("Chrome") != -1) return "Chrome";
    if (navigator.userAgent.indexOf("Edge") != -1) return "Edge";
    if (navigator.userAgent.indexOf("Firefox") != -1) return "Firefox";
    if (navigator.userAgent.indexOf("Safari") != -1) return "Safari";
    return "Unknown";
}

function showPermissionInstructions() {
    const browser = getBrowserName();
    let instructions = '';
    
    switch(browser) {
        case "Chrome":
            instructions = `
                <div class="alert alert-info" role="alert">
                    <h5>Permitir acceso a la cámara en Chrome:</h5>
                    <p>Por razones de seguridad, Chrome solo permite acceso a la cámara en:</p>
                    <ul>
                        <li>Sitios HTTPS seguros</li>
                        <li>localhost (127.0.0.1)</li>
                    </ul>
                    <p>Para acceder a la cámara:</p>
                    <ol>
                        <li>Asegúrate de estar usando la URL: <strong>http://127.0.0.1:5000</strong></li>
                        <li>Si estás en otra URL, copia y pega la URL anterior en tu navegador</li>
                        <li>Una vez en la URL correcta, haz clic en el icono del candado <i class="fas fa-lock"></i> en la barra de direcciones</li>
                        <li>Busca "Cámara" en el menú</li>
                        <li>Cambia la configuración a "Permitir"</li>
                        <li>Recarga la página</li>
                    </ol>
                </div>`;
            break;
        case "Firefox":
            instructions = `
                <div class="alert alert-info" role="alert">
                    <h5>Permitir acceso a la cámara en Firefox:</h5>
                    <ol>
                        <li>Haz clic en el icono de información <i class="fas fa-info-circle"></i> junto a la URL</li>
                        <li>Haz clic en "Permisos del sitio"</li>
                        <li>Encuentra "Usar la cámara" y selecciona "Permitir"</li>
                        <li>Recarga la página</li>
                    </ol>
                </div>`;
            break;
        case "Edge":
            instructions = `
                <div class="alert alert-info" role="alert">
                    <h5>Permitir acceso a la cámara en Edge:</h5>
                    <ol>
                        <li>Haz clic en el icono del candado <i class="fas fa-lock"></i> junto a la URL</li>
                        <li>Busca "Permisos del sitio"</li>
                        <li>Activa el permiso de "Cámara"</li>
                        <li>Recarga la página</li>
                    </ol>
                </div>`;
            break;
        default:
            instructions = `
                <div class="alert alert-info" role="alert">
                    <h5>Permitir acceso a la cámara:</h5>
                    <p>Busca en la configuración de tu navegador la sección de permisos y permite el acceso a la cámara para este sitio.</p>
                </div>`;
    }
    
    document.querySelector('.container').insertAdjacentHTML('afterbegin', instructions);
}

async function checkCameraPermissions() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        stream.getTracks().forEach(track => track.stop());
        return true;
    } catch (error) {
        console.error('Error al verificar permisos de cámara:', error);
        if (error.name === 'NotAllowedError') {
            showMessage('Acceso a la cámara bloqueado por el navegador', 'warning');
            showPermissionInstructions();
        } else if (error.name === 'NotFoundError') {
            showMessage('No se detectó ninguna cámara en el dispositivo.', 'warning');
        } else if (error.name === 'NotReadableError') {
            showMessage('La cámara está siendo usada por otra aplicación. Cierra otras aplicaciones que puedan estar usando la cámara.', 'warning');
        } else {
            showMessage(`Error al acceder a la cámara: ${error.message}`);
        }
        return false;
    }
}
async function loadAvailableCameras() {
    const cameraSelect = document.getElementById('camera-select');
    const startTime = Date.now();
    
    // Mostrar mensaje de búsqueda con animación
    cameraSelect.innerHTML = '<option value="">⌛ Buscando cámaras...</option>';
    cameraSelect.disabled = true;
    showMessage('Buscando cámaras disponibles...', 'info');

    try {
        console.log('Solicitando lista de cámaras al servidor...');
        const response = await fetch('/api/cameras/list');
        console.log('Respuesta recibida:', response.status);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Datos recibidos:', data);
        
        cameraSelect.innerHTML = ''; // Limpiar opciones existentes
        
        if (data.success) {
            if (data.cameras && data.cameras.length > 0) {
                data.cameras.forEach(camera => {
                    const option = document.createElement('option');
                    option.value = camera.id;
                    option.textContent = `${camera.name} (${camera.resolution}, ${camera.fps} FPS)`;
                    option.dataset.type = camera.type;
                    option.dataset.backend = camera.backend;
                    cameraSelect.appendChild(option);
                });
                const searchTime = ((Date.now() - startTime) / 1000).toFixed(1);
            showMessage(`Se encontraron ${data.cameras.length} cámara(s) en ${searchTime} segundos`, 'success');
            } else {
                cameraSelect.innerHTML = '<option value="">No hay cámaras disponibles</option>';
                showMessage('No se encontraron cámaras. Por favor, conecta una cámara y haz clic en el botón de actualizar.', 'warning');
            }
        } else {
            cameraSelect.innerHTML = '<option value="">Error al cargar cámaras</option>';
            showMessage(`Error al cargar la lista de cámaras: ${data.error || 'Error desconocido'}`, 'danger');
        }
    } catch (error) {
        console.error('Error al cargar cámaras:', error);
        cameraSelect.innerHTML = '<option value="">Error al cargar cámaras</option>';
        showMessage(`Error al comunicarse con el servidor: ${error.message}. Intenta recargar la página.`, 'danger');
    } finally {
        cameraSelect.disabled = false;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const startButton = document.getElementById('start-camera');
    const stopButton = document.getElementById('stop-camera');
    const cameraSelect = document.getElementById('camera-select');
    const refreshButton = document.getElementById('refresh-cameras');
    
    let activeCamera = null;
    let retryCount = 0;
    const maxRetries = 3;
    
    // Cargar la lista de cámaras al inicio
    loadAvailableCameras();
    
    // Evento para el botón de actualizar cámaras
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            refreshButton.disabled = true;
            refreshButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
            loadAvailableCameras().finally(() => {
                refreshButton.disabled = false;
                refreshButton.innerHTML = '<i class="fas fa-sync-alt"></i>';
            });
        });
    }

    startButton.addEventListener('click', async function() {
        // Verificar permisos primero
        if (!await checkCameraPermissions()) {
            return;
        }

        const cameraId = parseInt(cameraSelect.value);
        startButton.disabled = true;
        startButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Iniciando...';
        
        try {
            showMessage('Intentando iniciar la cámara...', 'info');
            const response = await fetch(`/api/camera/${cameraId}/start`, {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.success) {
                // Mostrar el stream
                const placeholder = document.getElementById(`camera-${cameraId}-placeholder`);
                const stream = document.getElementById(`camera-${cameraId}-stream`);
                
                if (placeholder && stream) {
                    // Primero configurar los eventos
                    stream.onload = function() {
                        console.log('Stream cargado correctamente');
                        placeholder.style.display = 'none';
                        stream.style.display = 'block';
                        retryCount = 0;
                        document.getElementById(`camera-${cameraId}-status`).textContent = 'Conectada';
                    };
                    
                    stream.onerror = function() {
                        console.error('Error al cargar el stream');
                        showMessage('Error al cargar el stream de la cámara. Intentando reconectar...', 'warning');
                        stream.style.display = 'none';
                        placeholder.style.display = 'flex';
                        document.getElementById(`camera-${cameraId}-status`).textContent = 'Error';
                        
                        if (retryCount < maxRetries) {
                            retryCount++;
                            console.log(`Reintento ${retryCount} de ${maxRetries}`);
                            setTimeout(() => {
                                console.log('Reintentando conexión...');
                                stream.src = `/api/camera/${cameraId}/stream?retry=${retryCount}&t=${new Date().getTime()}`;
                            }, 2000);
                        } else {
                            showMessage('No se pudo establecer la conexión con la cámara después de varios intentos.', 'danger');
                            document.getElementById(`camera-${cameraId}-status`).textContent = 'Desconectada';
                        }
                    };
                    
                    // Luego intentar cargar el stream
                    console.log('Intentando cargar stream de cámara...');
                    stream.src = `/api/camera/${cameraId}/stream?t=${new Date().getTime()}`;
                    activeCamera = cameraId;
                    showMessage('Cámara iniciada exitosamente', 'success');
                }
            } else {
                showMessage('Error al iniciar la cámara: ' + (data.error || 'Error desconocido'), 'danger');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('Error al comunicarse con el servidor: ' + error.message, 'danger');
        } finally {
            startButton.disabled = false;
            startButton.innerHTML = 'Iniciar Cámara';
        }
    });

    stopButton.addEventListener('click', async function() {
        if (activeCamera !== null) {
            try {
                // Detener la cámara
                const response = await fetch(`/api/camera/${activeCamera}/stop`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    // Ocultar el stream
                    const placeholder = document.getElementById(`camera-${activeCamera}-placeholder`);
                    const stream = document.getElementById(`camera-${activeCamera}-stream`);
                    
                    if (placeholder && stream) {
                        placeholder.style.display = 'flex';
                        stream.style.display = 'none';
                        stream.src = '';
                    }
                    activeCamera = null;
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error al comunicarse con el servidor');
            }
        }
    });
});
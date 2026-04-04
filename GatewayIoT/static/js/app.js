const socket = io();
const sensorsGrid = document.getElementById('sensors-grid');
const logOutput = document.getElementById('log-output');
const lastUpdate = document.getElementById('last-update');
const configForm = document.getElementById('config-form');
const startRealBtn = document.getElementById('start-real-btn');
const startSimBtn = document.getElementById('start-sim-btn');
const stopBtn = document.getElementById('stop-btn');

// State for sensors to avoid re-rendering everything
let sensorValues = {};
let sensorsConfig = []; // Store the names/units from config

// --- Socket.IO Events ---

socket.on('connect', () => {
    addLog('system', 'Conectado al servidor WebSocket');
});

socket.on('data', (data) => {
    lastUpdate.textContent = `Última actualización: ${new Date().toLocaleTimeString()}`;
    updateSensors(data.values);
    addLog('serial', `Recibido: ${data.raw}`);
});

socket.on('status', (data) => {
    const badge = document.getElementById(`${data.service}-status`);
    if (badge) {
        badge.className = `status-badge ${data.state}`;
        badge.querySelector('.label').textContent = data.message || data.state;
    }
    const logType = data.state === 'error' ? 'error' : 'system';
    addLog(logType, `[${data.service.toUpperCase()}] ${data.message}`);
});

// --- UI Updates ---

function updateSensors(values) {
    // If number of sensors changed, clear and rebuild
    if (values.length !== Object.keys(sensorValues).length) {
        sensorsGrid.innerHTML = '';
        sensorValues = {};
    }

    values.forEach((val, idx) => {
        const id = `sensor-${idx}`;
        let card = document.getElementById(id);
        const config = sensorsConfig[idx] || { name: `Sensor ${idx + 1}`, unit: '' };
        
        if (!card) {
            card = document.createElement('div');
            card.id = id;
            card.className = 'sensor-card';
            card.innerHTML = `
                <div class="sensor-label" id="${id}-label">${config.name}</div>
                <div class="sensor-val" id="${id}-val">--</div>
                <div class="sensor-unit" id="${id}-unit">${config.unit}</div>
            `;
            sensorsGrid.appendChild(card);
        }
        
        // Update label/unit if they changed in config
        document.getElementById(`${id}-label`).textContent = config.name;
        document.getElementById(`${id}-unit`).textContent = config.unit;

        const valEl = document.getElementById(`${id}-val`);
        if (sensorValues[idx] !== val) {
            valEl.textContent = val;
            valEl.style.color = 'var(--accent-primary)';
            setTimeout(() => { valEl.style.color = 'white'; }, 500);
            sensorValues[idx] = val;
        }
    });
}

function addLog(type, message) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    const time = new Date().toLocaleTimeString();
    entry.textContent = `[${time}] ${message}`;
    logOutput.appendChild(entry);
    logOutput.scrollTop = logOutput.scrollHeight;
    
    // Keep only last 100 logs
    while (logOutput.children.length > 100) {
        logOutput.removeChild(logOutput.firstChild);
    }
}

// --- Config Handling ---

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        
        // Map nested object to form inputs
        document.getElementById('serial-port').value = config.serial.port;
        document.getElementById('serial-baud').value = config.serial.baud;
        document.getElementById('mqtt-broker').value = config.mqtt.broker;
        document.getElementById('mqtt-user').value = config.mqtt.username;
        document.getElementById('mqtt-pass').value = config.mqtt.password;
        document.getElementById('mqtt-topic').value = config.mqtt.base_topic;

        // Load sensor rows
        sensorsConfig = config.sensors || [];
        renderSensorRows();
    } catch (err) {
        addLog('error', 'Error cargando configuración');
    }
}

configForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(configForm);
    
    // Convert FormData to nested JSON
    const config = {
        serial: {
            port: formData.get('serial.port'),
            baud: parseInt(formData.get('serial.baud'))
        },
        mqtt: {
            broker: formData.get('mqtt.broker'),
            username: formData.get('mqtt.username'),
            password: formData.get('mqtt.password'),
            base_topic: formData.get('mqtt.base_topic'),
            port: 1883
        },
        sensors: getSensorRowsData()
    };

    try {
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        if (response.ok) {
            addLog('system', 'Configuración guardada. Reinicie el servidor para aplicar cambios de puerto.');
            alert('Configuración guardada satisfactoriamente.');
        }
    } catch (err) {
        addLog('error', 'Error al guardar configuración');
    }
});

function renderSensorRows() {
    const list = document.getElementById('sensor-config-list');
    list.innerHTML = '';
    sensorsConfig.forEach((s, idx) => {
        const row = document.createElement('div');
        row.className = 'sensor-config-item';
        row.innerHTML = `
            <input type="text" placeholder="Nombre (ej. Temperatura)" value="${s.name}" class="s-name">
            <input type="text" placeholder="Unidad (ej. °C)" value="${s.unit}" class="s-unit">
            <button type="button" class="btn-remove" onclick="removeSensorRow(${idx})">×</button>
        `;
        list.appendChild(row);
    });
}

function getSensorRowsData() {
    const rows = document.querySelectorAll('.sensor-config-item');
    return Array.from(rows).map(row => ({
        name: row.querySelector('.s-name').value,
        unit: row.querySelector('.s-unit').value
    }));
}

function removeSensorRow(idx) {
    sensorsConfig = getSensorRowsData();
    sensorsConfig.splice(idx, 1);
    renderSensorRows();
}

document.getElementById('add-sensor-row').onclick = () => {
    sensorsConfig = getSensorRowsData();
    sensorsConfig.push({ name: '', unit: '' });
    renderSensorRows();
};

window.removeSensorRow = removeSensorRow;

// --- Bridge Controls ---

async function checkBridgeStatus() {
    try {
        const response = await fetch('/api/bridge/status');
        const status = await response.json();
        updateControlButtons(status.running, status.simulation ? 'simulation' : 'real');
        
        if (status.running) {
            addLog('system', `Bridge detectado: ${status.simulation ? 'Simulación' : 'Real'}`);
        }
    } catch (err) {
        console.error('Error verificando estado:', err);
    }
}

async function startBridge(mode) {
    try {
        addLog('system', `Iniciando bridge en modo ${mode}...`);
        const response = await fetch('/api/bridge/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode })
        });
        const result = await response.json();
        
        if (result.status === 'started' || result.status === 'already_running') {
            updateControlButtons(true, mode);
        }
    } catch (err) {
        addLog('error', `Error al iniciar: ${err.message}`);
    }
}

async function stopBridge() {
    try {
        addLog('system', 'Deteniendo bridge...');
        const response = await fetch('/api/bridge/stop', { method: 'POST' });
        const result = await response.json();
        
        if (result.status === 'stopped') {
            updateControlButtons(false);
        }
    } catch (err) {
        addLog('error', `Error al detener: ${err.message}`);
    }
}

function updateControlButtons(running, mode) {
    startRealBtn.disabled = running;
    startSimBtn.disabled = running;
    stopBtn.disabled = !running;

    if (running) {
        startRealBtn.classList.toggle('active', mode === 'real');
        startSimBtn.classList.toggle('active', mode === 'simulation');
    } else {
        startRealBtn.classList.remove('active');
        startSimBtn.classList.remove('active');
    }
}

startRealBtn.addEventListener('click', () => startBridge('real'));
startSimBtn.addEventListener('click', () => startBridge('simulation'));
stopBtn.addEventListener('click', () => stopBridge());

document.getElementById('clear-logs').onclick = () => {
    logOutput.innerHTML = '';
};

// Initial load
loadConfig();
checkBridgeStatus();

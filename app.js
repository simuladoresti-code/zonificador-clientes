const API_URL = "https://zonificador-clientes-7.onrender.com";
const TIMEOUT = 300000;

let procesando = false;
let map = null;
let charts = {};
let clientesData = [];
let poligonosData = [];
let clientesAsignados = [];

// ===== INICIALIZACIÓN =====
document.addEventListener('DOMContentLoaded', () => {
    inicializarUI();
    verificarServidorActivo();
});

function inicializarUI() {
    // Event listeners para tabs
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const tabName = item.getAttribute('data-tab');
            cambiarTab(tabName);
        });
    });

    // Inicializar mapa
    setTimeout(() => {
        if (!map && document.getElementById('mapContainer')) {
            inicializarMapa();
        }
    }, 500);
}

// ===== NAVEGACIÓN DE TABS =====
function cambiarTab(tabName) {
    // Ocultar todos los tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Mostrar tab seleccionado
    const tab = document.getElementById(tabName);
    if (tab) {
        tab.classList.add('active');
    }

    // Actualizar menu activo
    document.querySelectorAll('.menu-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Si es el mapa, redimensionar
    if (tabName === 'map' && map) {
        setTimeout(() => map.invalidateSize(), 200);
    }

    // Si es analytics, recrear gráficos
    if (tabName === 'analytics' && clientesAsignados.length > 0) {
        setTimeout(() => {
            actualizarGraficos();
        }, 300);
    }
}

// ===== VERIFICACIÓN DE SERVIDOR =====
function verificarServidorActivo() {
    fetch(API_URL)
        .then(r => r.json())
        .then(() => {
            const indicator = document.getElementById('serverStatus');
            const statusText = document.getElementById('statusText');
            if (indicator) indicator.classList.add('active');
            if (statusText) statusText.textContent = '● Activo';
        })
        .catch(() => {
            const statusText = document.getElementById('statusText');
            if (statusText) statusText.textContent = '● Desconectado';
        });
}

// ===== SPINNER Y PROGRESO =====
function mostrarSpinner(mostrar = true, texto = "Procesando...") {
    const spinner = document.getElementById("loadingSpinner");
    const spinnerText = document.getElementById("spinnerText");

    if (mostrar && spinner) {
        if (spinnerText) spinnerText.textContent = texto;
        spinner.style.display = "flex";
    } else if (spinner) {
        spinner.style.display = "none";
    }
}

function mostrarProgreso(mostrar = true) {
    const container = document.getElementById("progressContainer");
    if (!container) return;

    if (mostrar) {
        container.style.display = "block";
        actualizarProgreso(0);
    } else {
        container.style.display = "none";
    }
}

function actualizarProgreso(porcentaje) {
    const bar = document.getElementById("progressBar");
    const text = document.getElementById("progressText");

    if (bar) bar.style.width = porcentaje + "%";
    if (text) text.textContent = `${porcentaje}%`;
}

function simularProgreso() {
    const intervalo = setInterval(() => {
        const bar = document.getElementById("progressBar");
        if (!bar) return;

        const actual = parseInt(bar.style.width) || 0;
        if (actual >= 90) {
            clearInterval(intervalo);
            return;
        }

        const incremento = Math.random() * 20;
        const nuevo = Math.min(actual + incremento, 90);
        actualizarProgreso(Math.round(nuevo));
    }, 300);

    return intervalo;
}

// ===== LOGS =====
function agregarLog(mensaje) {
    const logs = document.getElementById("logs");
    if (!logs) return;

    // Si está vacío, limpiar
    if (logs.querySelector('.log-empty')) {
        logs.innerHTML = '';
    }

    const fecha = new Date().toLocaleString();
    const p = document.createElement("p");
    p.textContent = `[${fecha}] ${mensaje}`;
    logs.appendChild(p);

    // Limitar logs
    if (logs.children.length > 100) {
        logs.removeChild(logs.firstChild);
    }

    logs.scrollTop = logs.scrollHeight;
}

function limpiarLogs() {
    const logs = document.getElementById("logs");
    if (logs) {
        logs.innerHTML = '<p class="log-empty">No hay eventos registrados</p>';
    }
}

// ===== MANEJO DE ARCHIVOS =====
function validarArchivos(clientes, poligonos) {
    if (!clientes || !poligonos) {
        throw new Error("Debes seleccionar ambos archivos KMZ");
    }

    if (!clientes.name.endsWith('.kmz') || !poligonos.name.endsWith('.kmz')) {
        throw new Error("Los archivos deben tener extensión .kmz");
    }

    const maxSize = 50 * 1024 * 1024;
    if (clientes.size > maxSize || poligonos.size > maxSize) {
        throw new Error("Los archivos no pueden superar 50MB");
    }

    return true;
}

async function hacerFetch(url, opciones = {}) {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);

        const response = await fetch(url, {
            ...opciones,
            signal: controller.signal,
            headers: {
                ...opciones.headers,
                'Accept': 'application/json'
            }
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        return response;
    } catch (error) {
        throw error;
    }
}

// ===== SUBIR ARCHIVOS =====
async function subirArchivos() {
    if (procesando) return;

    const btn = document.getElementById("btnSubir");
    const btnProcesar = document.getElementById("btnProcesar");
    let progreso;

    try {
        procesando = true;
        if (btn) btn.disabled = true;
        if (btnProcesar) btnProcesar.disabled = true;

        const clientes = document.getElementById("clientesFile").files[0];
        const poligonos = document.getElementById("poligonosFile").files[0];

        validarArchivos(clientes, poligonos);

        agregarLog(`📤 Iniciando subida: ${clientes.name} y ${poligonos.name}`);

        mostrarSpinner(true, "Subiendo archivos...");
        mostrarProgreso(true);

        progreso = simularProgreso();

        const formData = new FormData();
        formData.append("clientes", clientes);
        formData.append("poligonos", poligonos);

        const estado = document.getElementById("estado");
        if (estado) estado.innerHTML = '⏳ Subiendo archivos...';

        const response = await hacerFetch(API_URL + "/subir", {
            method: "POST",
            body: formData
        });

        clearInterval(progreso);

        const data = await response.json();
        actualizarProgreso(100);

        if (estado) estado.innerHTML = '✅ Archivos subidos correctamente';
        agregarLog("✅ Archivos subidos correctamente");

        setTimeout(() => {
            mostrarSpinner(false);
            mostrarProgreso(false);
        }, 500);

    } catch (error) {
        if (progreso) clearInterval(progreso);
        mostrarSpinner(false);
        mostrarProgreso(false);

        let mensajeError = error.message;
        if (error.name === 'AbortError') {
            mensajeError = "Tiempo de espera agotado";
        } else if (error.message.includes("Failed to fetch")) {
            mensajeError = "No se puede conectar al servidor";
        }

        const estado = document.getElementById("estado");
        if (estado) estado.innerHTML = `❌ Error: ${mensajeError}`;

        agregarLog(`❌ Error en subida: ${mensajeError}`);
        alert(`Error: ${mensajeError}`);

    } finally {
        procesando = false;
        if (btn) btn.disabled = false;
        if (btnProcesar) btnProcesar.disabled = false;
    }
}

// ===== PROCESAR DATOS =====
async function actualizarDatos() {
    if (procesando) return;

    const btn = document.getElementById("btnProcesar");
    const btnSubir = document.getElementById("btnSubir");
    let progreso;

    try {
        procesando = true;
        if (btn) btn.disabled = true;
        if (btnSubir) btnSubir.disabled = true;

        const inicio = Date.now();

        agregarLog("⚙️ Iniciando procesamiento de datos");

        mostrarSpinner(true, "Procesando archivos...");
        mostrarProgreso(true);

        progreso = simularProgreso();

        const estado = document.getElementById("estado");
        if (estado) estado.innerHTML = '⏳ Procesando archivos...';

        const response = await hacerFetch(API_URL + "/actualizar");
        clearInterval(progreso);

        const data = await response.json();
        const fin = Date.now();
        const tiempo = ((fin - inicio) / 1000).toFixed(2);

        clientesData = data.clientes || [];
        poligonosData = data.poligonos || [];
        clientesAsignados = data.clientes_asignados || [];

        // Actualizar KPIs
        const clientesCount = document.getElementById("clientesCount");
        const poligonosCount = document.getElementById("poligonosCount");
        const tiempoEl = document.getElementById("tiempo");
        const cobertura = document.getElementById("cobertura");
        const fechaEjecucion = document.getElementById("fechaEjecucion");
        const clientesAsignadosEl = document.getElementById("clientesAsignados");
        const clientesSinAsignarEl = document.getElementById("clientesSinAsignar");

        if (clientesCount) clientesCount.innerText = data.clientes || 0;
        if (poligonosCount) poligonosCount.innerText = data.poligonos || 0;
        if (tiempoEl) tiempoEl.innerText = tiempo + "s";
        if (fechaEjecucion) fechaEjecucion.innerText = new Date().toLocaleDateString();

        // Calcular cobertura
        const asignados = clientesAsignados.filter(c => c.poligono).length;
        const porcentajeCobertura = Math.round((asignados / (data.clientes || 1)) * 100);
        if (cobertura) cobertura.innerText = porcentajeCobertura + "%";
        if (clientesAsignadosEl) clientesAsignadosEl.innerText = asignados;
        if (clientesSinAsignarEl) clientesSinAsignarEl.innerText = (data.clientes || 0) - asignados;

        // Actualizar última sincronización
        const lastSync = document.getElementById("lastSync");
        if (lastSync) {
            lastSync.innerHTML = `<i class="fas fa-sync-alt"></i><span>Última actualización: ${new Date().toLocaleString()}</span>`;
        }

        actualizarProgreso(100);

        if (estado) estado.innerHTML = '✅ Procesamiento completado correctamente';
        document.getElementById("btnDescargar").style.display = "inline-flex";

        // Actualizar visualizaciones
        actualizarMapa();
        actualizarTablaEstadisticas();
        actualizarGraficos();

        agregarLog(`✅ Procesamiento finalizado en ${tiempo}s`);
        agregarLog(`📊 Clientes: ${data.clientes}, Polígonos: ${data.poligonos}, Asignados: ${asignados}`);

        setTimeout(() => {
            mostrarSpinner(false);
            mostrarProgreso(false);
        }, 500);

    } catch (error) {
        if (progreso) clearInterval(progreso);
        mostrarSpinner(false);
        mostrarProgreso(false);

        let mensajeError = error.message;
        if (error.name === 'AbortError') {
            mensajeError = "Tiempo de espera agotado";
        }

        const estado = document.getElementById("estado");
        if (estado) estado.innerHTML = `❌ Error: ${mensajeError}`;

        agregarLog(`❌ Error en procesamiento: ${mensajeError}`);
        alert(`Error: ${mensajeError}`);

    } finally {
        procesando = false;
        if (btn) btn.disabled = false;
        if (btnSubir) btnSubir.disabled = false;
    }
}

// ===== DESCARGAR EXCEL =====
function descargarExcel() {
    try {
        agregarLog("📥 Descargando Excel...");
        window.open(API_URL + "/descargar", "_blank");
        agregarLog("✅ Excel descargado");
    } catch (error) {
        agregarLog("❌ Error al descargar Excel");
        alert("Error al descargar el archivo");
    }
}

// ===== MAPA LEAFLET =====
function inicializarMapa() {
    const container = document.getElementById('mapContainer');
    if (!container) return;

    if (map) {
        map.remove();
    }

    map = L.map('mapContainer').setView([-33.8688, -70.7678], 10);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
        className: 'map-tiles'
    }).addTo(map);
}

function actualizarMapa() {
    if (!map || !clientesAsignados.length) return;

    // Limpiar marcadores anteriores
    map.eachLayer(layer => {
        if (layer instanceof L.Marker || layer instanceof L.Polyline) {
            map.removeLayer(layer);
        }
    });

    // Agregar marcadores de clientes
    clientesAsignados.forEach(cliente => {
        const color = cliente.poligono ? '#3388ff' : '#ff6b6b';
        const icon = L.circleMarker([cliente.lat, cliente.lon], {
            radius: 5,
            fillColor: color,
            color: color,
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.8
        });

        icon.bindPopup(`
            <strong>${cliente.nombre || 'Cliente'}</strong><br>
            Zona: ${cliente.poligono || 'Sin asignar'}<br>
            Lat: ${cliente.lat.toFixed(4)}<br>
            Lon: ${cliente.lon.toFixed(4)}
        `);

        icon.addTo(map);
    });

    // Ajustar vista
    if (clientesAsignados.length > 0) {
        const bounds = L.latLngBounds(
            clientesAsignados.map(c => [c.lat, c.lon])
        );
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

// ===== GRÁFICOS =====
function actualizarGraficos() {
    actualizarGraficoDistribucion();
    actualizarGraficoCobertura();
}

function actualizarGraficoDistribucion() {
    const ctx = document.getElementById('distributionChart');
    if (!ctx) return;

    // Agrupar por polígono
    const distribucion = {};
    clientesAsignados.forEach(cliente => {
        const zona = cliente.poligono || 'Sin asignar';
        distribucion[zona] = (distribucion[zona] || 0) + 1;
    });

    const labels = Object.keys(distribucion);
    const datos = Object.values(distribucion);

    if (charts.distribution) {
        charts.distribution.destroy();
    }

    charts.distribution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Clientes por Zona',
                data: datos,
                backgroundColor: [
                    '#3388ff',
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#8b5cf6',
                    '#ec4899'
                ],
                borderRadius: 5,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                },
                x: {
                    ticks: { color: '#cbd5e1' },
                    grid: { color: 'rgba(255,255,255,0.05)' }
                }
            }
        }
    });
}

function actualizarGraficoCobertura() {
    const ctx = document.getElementById('coverageChart');
    if (!ctx) return;

    const asignados = clientesAsignados.filter(c => c.poligono).length;
    const total = clientesAsignados.length;
    const sinAsignar = total - asignados;

    if (charts.coverage) {
        charts.coverage.destroy();
    }

    charts.coverage = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Asignados', 'Sin Asignar'],
            datasets: [{
                data: [asignados, sinAsignar],
                backgroundColor: ['#10b981', '#ef4444'],
                borderColor: '#1e293b',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#cbd5e1' }
                }
            }
        }
    });
}

// ===== TABLA DE ESTADÍSTICAS =====
function actualizarTablaEstadisticas() {
    const tbody = document.getElementById('statsTableBody');
    if (!tbody) return;

    // Agrupar por polígono
    const estadisticas = {};
    clientesAsignados.forEach(cliente => {
        const zona = cliente.poligono || 'Sin asignar';
        if (!estadisticas[zona]) {
            estadisticas[zona] = {
                count: 0,
                lats: [],
                lons: []
            };
        }
        estadisticas[zona].count++;
        estadisticas[zona].lats.push(cliente.lat);
        estadisticas[zona].lons.push(cliente.lon);
    });

    tbody.innerHTML = '';

    Object.entries(estadisticas).forEach(([zona, datos]) => {
        const promLat = (datos.lats.reduce((a, b) => a + b, 0) / datos.lats.length).toFixed(4);
        const promLon = (datos.lons.reduce((a, b) => a + b, 0) / datos.lons.length).toFixed(4);
        const porcentaje = ((datos.count / clientesAsignados.length) * 100).toFixed(1);

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${zona}</strong></td>
            <td>${datos.count}</td>
            <td>${porcentaje}%</td>
            <td>${promLat}</td>
            <td>${promLon}</td>
        `;
        tbody.appendChild(tr);
    });
}

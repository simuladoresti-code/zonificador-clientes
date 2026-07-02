const API_URL = "https://zonificador-clientes-7.onrender.com";
const TIMEOUT = 300000; // 5 minutos timeout
let procesando = false;

// Función para mostrar spinner
function mostrarSpinner(mostrar = true, texto = "Procesando...") {
    const spinner = document.getElementById("loadingSpinner");
    const spinnerText = document.getElementById("spinnerText");
    
    if (mostrar) {
        spinnerText.textContent = texto;
        spinner.style.display = "flex";
    } else {
        spinner.style.display = "none";
    }
}

// Función para mostrar barra de progreso
function mostrarProgreso(mostrar = true) {
    const container = document.getElementById("progressContainer");
    
    if (mostrar) {
        container.style.display = "block";
        actualizarProgreso(0);
    } else {
        container.style.display = "none";
    }
}

// Actualizar barra de progreso
function actualizarProgreso(porcentaje) {
    const bar = document.getElementById("progressBar");
    const text = document.getElementById("progressText");
    
    bar.style.width = porcentaje + "%";
    text.textContent = `Procesando... ${porcentaje}%`;
}

// Simulación de progreso
function simularProgreso(duracion = 3000) {
    const intervalo = setInterval(() => {
        const actual = parseInt(document.getElementById("progressBar").style.width) || 0;
        
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

// Agregar log de forma segura (sin XSS)
function agregarLog(mensaje) {
    const logs = document.getElementById("logs");
    const fecha = new Date().toLocaleString();
    
    // Crear elemento de forma segura
    const p = document.createElement("p");
    p.textContent = `[${fecha}] ${mensaje}`;
    logs.appendChild(p);
    
    // Limitar cantidad de logs
    const maxLogs = 100;
    if (logs.children.length > maxLogs) {
        logs.removeChild(logs.firstChild);
    }
    
    // Auto-scroll al final
    logs.scrollTop = logs.scrollHeight;
}

// Validar archivos
function validarArchivos(clientes, poligonos) {
    if (!clientes || !poligonos) {
        throw new Error("Debes seleccionar ambos archivos KMZ");
    }
    
    if (!clientes.name.endsWith('.kmz') || !poligonos.name.endsWith('.kmz')) {
        throw new Error("Los archivos deben tener extensión .kmz");
    }
    
    const maxSize = 50 * 1024 * 1024; // 50MB
    if (clientes.size > maxSize || poligonos.size > maxSize) {
        throw new Error("Los archivos no pueden superar 50MB");
    }
    
    return true;
}

// Subir archivos
async function subirArchivos() {
    if (procesando) return;
    
    const btn = document.getElementById("btnSubir");
    const btnProcesar = document.getElementById("btnProcesar");
    let progreso;
    
    try {
        procesando = true;
        
        // Desabilitar botones
        btn.disabled = true;
        btnProcesar.disabled = true;
        btn.textContent = "Subiendo...";
        
        const clientes = document.getElementById("clientesFile").files[0];
        const poligonos = document.getElementById("poligonosFile").files[0];
        
        // Validar archivos
        validarArchivos(clientes, poligonos);
        
        agregarLog(`Iniciando subida: ${clientes.name} y ${poligonos.name}`);
        
        // Mostrar spinner
        mostrarSpinner(true, "Subiendo archivos...");
        mostrarProgreso(true);
        
        progreso = simularProgreso();
        
        const formData = new FormData();
        formData.append("clientes", clientes);
        formData.append("poligonos", poligonos);
        
        document.getElementById("estado").innerHTML = 
            "⏳ Subiendo archivos (esto puede tardar un momento)...";
        
        // Fetch con timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);
        
        const response = await fetch(API_URL + "/subir", {
            method: "POST",
            body: formData,
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        clearInterval(progreso);
        
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }
        
        const data = await response.json();
        
        actualizarProgreso(100);
        
        document.getElementById("estado").innerHTML = 
            `✅ ${data.mensaje || "Archivos subidos correctamente"}`;
        
        agregarLog("✅ Archivos subidos correctamente");
        
        setTimeout(() => {
            mostrarSpinner(false);
            mostrarProgreso(false);
        }, 500);
        
    } catch (error) {
        console.error("Error en subida:", error);
        
        if (progreso) clearInterval(progreso);
        mostrarSpinner(false);
        mostrarProgreso(false);
        
        let mensajeError = error.message;
        if (error.name === 'AbortError') {
            mensajeError = "Tiempo de espera agotado. El servidor tarda demasiado.";
        }
        
        document.getElementById("estado").innerHTML = 
            `❌ Error: ${mensajeError}`;
        
        agregarLog(`❌ Error en subida: ${mensajeError}`);
        
        alert(`Error: ${mensajeError}`);
        
    } finally {
        procesando = false;
        btn.disabled = false;
        btnProcesar.disabled = false;
        btn.textContent = "Subir Archivos";
    }
}

// Actualizar datos
async function actualizarDatos() {
    if (procesando) return;
    
    const btn = document.getElementById("btnProcesar");
    const btnSubir = document.getElementById("btnSubir");
    let progreso;
    
    try {
        procesando = true;
        
        // Desabilitar botones
        btn.disabled = true;
        btnSubir.disabled = true;
        btn.textContent = "Procesando...";
        
        const inicio = Date.now();
        
        agregarLog("Iniciando procesamiento de datos");
        
        // Mostrar spinner
        mostrarSpinner(true, "Procesando archivos...");
        mostrarProgreso(true);
        
        progreso = simularProgreso();
        
        document.getElementById("estado").innerHTML = 
            "⏳ Procesando archivos (esto puede tardar un momento)...";
        
        // Fetch con timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), TIMEOUT);
        
        const response = await fetch(API_URL + "/actualizar", {
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        clearInterval(progreso);
        
        if (!response.ok) {
            throw new Error(`Error del servidor: ${response.status}`);
        }
        
        const data = await response.json();
        
        const fin = Date.now();
        const tiempo = ((fin - inicio) / 1000).toFixed(2);
        
        // Actualizar KPIs
        document.getElementById("clientes").innerText = data.clientes || 0;
        document.getElementById("poligonos").innerText = data.poligonos || 0;
        document.getElementById("fecha").innerText = new Date().toLocaleString();
        document.getElementById("tiempo").innerText = tiempo + "s";
        
        actualizarProgreso(100);
        
        document.getElementById("estado").innerHTML = 
            "✅ Procesamiento completado correctamente";
        
        // Mostrar botón de descarga
        document.getElementById("btnDescargar").style.display = "inline-block";
        
        agregarLog(`✅ Procesamiento finalizado en ${tiempo}s`);
        agregarLog(`📊 Clientes: ${data.clientes}, Polígonos: ${data.poligonos}`);
        
        setTimeout(() => {
            mostrarSpinner(false);
            mostrarProgreso(false);
        }, 500);
        
    } catch (error) {
        console.error("Error en procesamiento:", error);
        
        if (progreso) clearInterval(progreso);
        mostrarSpinner(false);
        mostrarProgreso(false);
        
        let mensajeError = error.message;
        if (error.name === 'AbortError') {
            mensajeError = "Tiempo de espera agotado. El servidor tarda demasiado.";
        }
        
        document.getElementById("estado").innerHTML = 
            `❌ Error: ${mensajeError}`;
        
        agregarLog(`❌ Error en procesamiento: ${mensajeError}`);
        
        alert(`Error: ${mensajeError}`);
        
    } finally {
        procesando = false;
        btn.disabled = false;
        btnSubir.disabled = false;
        btn.textContent = "Procesar Datos";
    }
}

// Descargar Excel
function descargarExcel() {
    try {
        agregarLog("📥 Descargando Excel...");
        window.open(API_URL + "/descargar", "_blank");
        agregarLog("✅ Excel descargado");
    } catch (error) {
        console.error("Error en descarga:", error);
        agregarLog("❌ Error al descargar Excel");
        alert("Error al descargar el archivo");
    }
}

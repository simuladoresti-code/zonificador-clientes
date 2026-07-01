const API_URL = "https://zonificador-clientes-7.onrender.com";

let totalDescargas = 0;

function agregarLog(mensaje) {
    const logs = document.getElementById("logs");
    const fecha = new Date().toLocaleString();

    logs.innerHTML += `<p>[${fecha}] ${mensaje}</p>`;
}

async function guardarConfig() {
    const clientes = document.getElementById("clientesLink").value;
    const poligonos = document.getElementById("poligonosLink").value;

    const response = await fetch(API_URL + "/config", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            clientes,
            poligonos
        })
    });

    const data = await response.json();

    document.getElementById("estado").innerHTML = data.mensaje;
    agregarLog("Configuración guardada");
}

function probarLinks() {
    const clientes = document.getElementById("clientesLink").value;

    if (clientes) {
        document.getElementById("mapFrame").src = clientes;
        agregarLog("Vista previa cargada");
    }
}

async function actualizarDatos() {
    const inicio = Date.now();

    document.getElementById("estado").innerHTML = "Procesando...";
    agregarLog("Inicio de actualización");

    const response = await fetch(API_URL + "/actualizar");
    const data = await response.json();

    const fin = Date.now();
    const tiempo = ((fin - inicio) / 1000).toFixed(2);

    document.getElementById("clientes").innerText = data.clientes;
    document.getElementById("poligonos").innerText = data.poligonos;
    document.getElementById("conPoligono").innerText = data.con_poligono;
    document.getElementById("sinPoligono").innerText = data.sin_poligono;
    document.getElementById("fecha").innerText = new Date().toLocaleString();
    document.getElementById("tiempo").innerText = tiempo + "s";

    document.getElementById("estado").innerHTML = "Actualización completada";
    document.getElementById("btnDescargar").style.display = "inline-block";

    agregarLog("Actualización completada");
}

function descargarExcel() {
    window.open(API_URL + "/descargar", "_blank");
    totalDescargas++;

    agregarLog("Excel descargado");
}
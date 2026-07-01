const API_URL = "https://zonificador-clientes-7.onrender.com";

function agregarLog(mensaje) {
    const logs = document.getElementById("logs");
    const fecha = new Date().toLocaleString();

    logs.innerHTML += `<p>[${fecha}] ${mensaje}</p>`;
}

async function subirArchivos() {
    const clientes = document.getElementById("clientesFile").files[0];
    const poligonos = document.getElementById("poligonosFile").files[0];

    if (!clientes || !poligonos) {
        alert("Selecciona ambos archivos KMZ");
        return;
    }

    const formData = new FormData();
    formData.append("clientes", clientes);
    formData.append("poligonos", poligonos);

    document.getElementById("estado").innerHTML = "Subiendo archivos...";

    const response = await fetch(API_URL + "/subir", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    document.getElementById("estado").innerHTML = data.mensaje;
    agregarLog("Archivos subidos correctamente");
}

async function actualizarDatos() {
    const inicio = Date.now();

    document.getElementById("estado").innerHTML = "Procesando archivos...";
    agregarLog("Inicio de procesamiento");

    const response = await fetch(API_URL + "/actualizar");
    const data = await response.json();

    const fin = Date.now();
    const tiempo = ((fin - inicio) / 1000).toFixed(2);

    document.getElementById("clientes").innerText = data.clientes;
    document.getElementById("poligonos").innerText = data.poligonos;
    document.getElementById("fecha").innerText = new Date().toLocaleString();
    document.getElementById("tiempo").innerText = tiempo + "s";

    document.getElementById("estado").innerHTML =
        "Procesamiento completado";

    document.getElementById("btnDescargar").style.display =
        "inline-block";

    agregarLog("Procesamiento finalizado");
}

function descargarExcel() {
    window.open(API_URL + "/descargar", "_blank");
    agregarLog("Excel descargado");
}

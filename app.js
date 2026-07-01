const API_URL = "https://zonificador-clientes-7.onrender.com";

function agregarLog(mensaje) {
    const logs = document.getElementById("logs");
    const fecha = new Date().toLocaleString();

    logs.innerHTML += `<p>[${fecha}] ${mensaje}</p>`;
}

async function guardarConfig() {
    const mapa = document.getElementById("mapaLink").value;

    const response = await fetch(API_URL + "/config", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            mapa
        })
    });

    const data = await response.json();

    document.getElementById("estado").innerHTML = data.mensaje;
    agregarLog("Mapa guardado");
}

function probarLinks() {
    const mapa = document.getElementById("mapaLink").value;

    if (mapa) {
        const idMapa = mapa.split("mid=")[1].split("&")[0];

        document.getElementById("mapFrame").src =
            `https://www.google.com/maps/d/embed?mid=${idMapa}`;

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

    agregarLog("Proceso completado");
}

function descargarExcel() {
    window.open(API_URL + "/descargar", "_blank");
    agregarLog("Excel descargado");
}

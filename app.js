const API_URL = "https://zonificador-clientes-7.onrender.com";

async function actualizarDatos() {
    document.getElementById("estado").innerHTML = "Procesando archivos...";

    const response = await fetch(API_URL + "/actualizar");
    const data = await response.json();

    if (data.estado === "ok") {
        document.getElementById("clientes").innerText = data.clientes;
        document.getElementById("poligonos").innerText = data.poligonos;

        document.getElementById("estado").innerHTML =
            "Archivo actualizado correctamente";

        document.getElementById("btnDescargar").style.display = "inline-block";
    }
}

function descargarExcel() {
    window.open(API_URL + "/descargar", "_blank");
}

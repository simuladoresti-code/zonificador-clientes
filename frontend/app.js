const API_URL = "https://zonificador-clientes-7.onrender.com";

function actualizarDatos() {
    const estado = document.getElementById("estado");

    estado.innerHTML = "Procesando información...";

    window.open(API_URL + "/actualizar", "_blank");

    document.getElementById("fecha").innerText =
        new Date().toLocaleString();

    estado.innerHTML = "Actualización completada.";
}

function descargarExcel() {
    window.open(API_URL + "/actualizar", "_blank");
}

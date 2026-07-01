const API = "https://zonificador-clientes.onrender.com";

function log(msg) {
    const el = document.getElementById("logs");
    const time = new Date().toLocaleString();
    el.innerHTML += `<p>[${time}] ${msg}</p>`;
}

async function actualizar() {
    document.getElementById("loader").classList.remove("hidden");
    log("Inicio actualización");

    const start = Date.now();

    const res = await fetch(API + "/actualizar");
    const data = await res.json();

    const end = Date.now();

    document.getElementById("clientes").innerText = data.clientes;
    document.getElementById("poligonos").innerText = data.poligonos;
    document.getElementById("sinPoligono").innerText = data.sin_poligono;
    document.getElementById("tiempo").innerText = ((end-start)/1000).toFixed(2) + "s";

    document.getElementById("loader").classList.add("hidden");

    log("Actualización completa");
}

function descargar() {
    window.open(API + "/descargar", "_blank");
    log("Descarga Excel");
}

async function guardarConfig() {
    const mapa = document.getElementById("mapaLink").value;

    await fetch(API + "/config", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({mapa})
    });

    log("Config guardada");

    const id = mapa.split("mid=")[1].split("&")[0];

    document.getElementById("mapaFrame").src =
        `https://www.google.com/maps/d/embed?mid=${id}`;
}

function buscar(valor) {
    log("Buscando: " + valor);
}

function showTab(tab) {
    log("Tab: " + tab);
}

function exportLogs() {
    const text = document.getElementById("logs").innerText;
    const blob = new Blob([text], {type:"text/plain"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "logs.txt";
    a.click();
}

async function checkServer() {
    try {
        const r = await fetch(API + "/actualizar");
        document.getElementById("serverStatus").innerText = "🟢 Online";
    } catch {
        document.getElementById("serverStatus").innerText = "🔴 Offline";
    }
}

checkServer();

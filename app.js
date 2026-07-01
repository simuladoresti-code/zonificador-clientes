const API = "https://zonificador-clientes.onrender.com";

async function actualizar() {

    const res = await fetch(API + "/actualizar");
    const data = await res.json();

    document.getElementById("c").innerText = data.clientes;
    document.getElementById("cp").innerText = data.con_poligono;
    document.getElementById("sp").innerText = data.sin_poligono;

    document.getElementById("estado").innerText = "OK";
}

function descargar() {
    window.open(API + "/actualizar", "_blank");
}

async function guardar() {
    const mapa = document.getElementById("mapa").value;

    await fetch(API + "/config", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({mapa})
    });

    document.getElementById("estado").innerText = "Mapa guardado";
}

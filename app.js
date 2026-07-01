const API = "https://zonificador-clientes.onrender.com";

function extraerMid(texto) {

    if (texto.includes("mid=")) {
        return texto.split("mid=")[1].split("&")[0];
    }

    return texto;
}

async function generar() {

    const input = document.getElementById("mid").value;
    const mid = extraerMid(input);

    if (!mid) {
        alert("Ingresa MID válido");
        return;
    }

    document.getElementById("estado").innerText = "Procesando...";

    try {

        const url = `${API}/actualizar?mid=${mid}`;

        const res = await fetch(url);

        if (!res.ok) {
            const err = await res.json();
            document.getElementById("estado").innerText = err.error;
            return;
        }

        const blob = await res.blob();

        const link = document.createElement("a");
        link.href = window.URL.createObjectURL(blob);
        link.download = "zonificacion.xlsx";
        link.click();

        document.getElementById("estado").innerText = "Descargado ✔";

    } catch (e) {
        document.getElementById("estado").innerText = "Error ❌";
    }
}

const API = "https://zonificador-clientes.onrender.com";

function extraerMid(texto) {
    // acepta link completo o mid directo
    if (texto.includes("mid=")) {
        return texto.split("mid=")[1].split("&")[0];
    }
    return texto;
}

async function procesar() {

    const input = document.getElementById("mid").value;
    const mid = extraerMid(input);

    if (!mid) {
        alert("Ingresa un MID válido");
        return;
    }

    document.getElementById("estado").innerText = "Procesando...";

    try {
        const url = `${API}/actualizar?mid=${mid}`;

        const res = await fetch(url);

        if (!res.ok) {
            throw new Error("Error en servidor");
        }

        // 🔥 IMPORTANTE: backend devuelve ARCHIVO, no JSON
        const blob = await res.blob();

        const downloadUrl = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = downloadUrl;
        a.download = "zonificacion.xlsx";
        document.body.appendChild(a);
        a.click();
        a.remove();

        document.getElementById("estado").innerText = "Excel descargado ✔";

    } catch (err) {
        console.error(err);
        document.getElementById("estado").innerText = "Error al procesar ❌";
    }
}

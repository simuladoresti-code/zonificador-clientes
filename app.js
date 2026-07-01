const API = "https://zonificador-clientes.onrender.com";

async function generar() {

    document.getElementById("estado").innerText = "Procesando...";

    try {

        const res = await fetch(`${API}/actualizar`);

        if (!res.ok) {
            const err = await res.json();
            document.getElementById("estado").innerText = err.error;
            return;
        }

        const blob = await res.blob();

        const a = document.createElement("a");
        a.href = URL.createObjectURL(blob);
        a.download = "zonificacion.xlsx";
        a.click();

        document.getElementById("estado").innerText = "Descargado ✔";

    } catch (e) {
        document.getElementById("estado").innerText = "Error conexión";
    }
}

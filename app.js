const API = "https://zonificador-clientes.onrender.com";

async function enviar() {

    const clientes = document.getElementById("clientes").files[0];
    const poligonos = document.getElementById("poligonos").files[0];

    if (!clientes || !poligonos) {
        alert("Sube ambos archivos");
        return;
    }

    const formData = new FormData();
    formData.append("clientes", clientes);
    formData.append("poligonos", poligonos);

    document.getElementById("estado").innerText = "Procesando...";

    const res = await fetch(`${API}/actualizar`, {
        method: "POST",
        body: formData
    });

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

    document.getElementById("estado").innerText = "Listo ✔";
}

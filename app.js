async function generar() {

    const clientes = document.getElementById("clientes").files[0];
    const poligonos = document.getElementById("poligonos").files[0];

    const formData = new FormData();
    formData.append("clientes", clientes);
    formData.append("poligonos", poligonos);

    const res = await fetch("https://zonificador-clientes.onrender.com/actualizar", {
        method: "POST",
        body: formData
    });

    const blob = await res.blob();

    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "zonificacion.xlsx";
    a.click();
}

from flask import Flask, jsonify, request, send_file
from processor import procesar_datos
import os

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify({"mensaje": "Servidor activo"})


@app.route("/subir", methods=["POST"])
def subir():

    clientes = request.files["clientes"]
    poligonos = request.files["poligonos"]

    clientes.save("clientes.kmz")
    poligonos.save("poligonos.kmz")

    return jsonify({
        "mensaje": "Archivos subidos correctamente"
    })


@app.route("/actualizar")
def actualizar():

    archivo, total_clientes, total_poligonos = procesar_datos(
        "clientes.kmz",
        "poligonos.kmz"
    )

    return jsonify({
        "estado": "ok",
        "clientes": total_clientes,
        "poligonos": total_poligonos
    })


@app.route("/descargar")
def descargar():
    return send_file(
        "clientes_actualizados.xlsx",
        as_attachment=True
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

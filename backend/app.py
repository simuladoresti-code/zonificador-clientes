from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from processor import procesar_datos
import os

app = Flask(__name__)

# Configurar CORS para permitir solicitudes desde GitHub Pages y otros orígenes
CORS(app, resources={
    r"/*": {
        "origins": [
            "https://simuladoresti-code.github.io",
            "http://localhost:*",
            "http://127.0.0.1:*"
        ],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


@app.route("/")
def home():
    return jsonify({"mensaje": "Servidor activo"})


@app.route("/subir", methods=["POST", "OPTIONS"])
def subir():

    clientes = request.files["clientes"]
    poligonos = request.files["poligonos"]

    clientes.save("clientes.kmz")
    poligonos.save("poligonos.kmz")

    return jsonify({
        "mensaje": "Archivos subidos correctamente"
    })


@app.route("/actualizar", methods=["GET", "OPTIONS"])
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


@app.route("/descargar", methods=["GET", "OPTIONS"])
def descargar():
    return send_file(
        "clientes_actualizados.xlsx",
        as_attachment=True
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

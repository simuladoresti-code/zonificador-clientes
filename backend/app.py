from flask import Flask, jsonify, request, send_file
from processor import procesar_datos
import json
import os

app = Flask(__name__)

CONFIG_FILE = "config.json"


def leer_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    return jsonify({"mensaje": "Servidor activo"})


@app.route("/config", methods=["POST"])
def config():
    data = request.json
    guardar_config(data)
    return jsonify({"mensaje": "Mapa guardado correctamente"})


@app.route("/actualizar")
def actualizar():
    config = leer_config()

    archivo, clientes, poligonos, con_poligono, sin_poligono = procesar_datos(
        config["mapa"]
    )

    return jsonify({
        "estado": "ok",
        "clientes": clientes,
        "poligonos": poligonos,
        "con_poligono": con_poligono,
        "sin_poligono": sin_poligono
    })


@app.route("/descargar")
def descargar():
    return send_file(
        "clientes_actualizados.xlsx",
        as_attachment=True
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)from flask import Flask, jsonify, request, send_file
from processor import procesar_datos
import json
import os

app = Flask(__name__)

CONFIG_FILE = "config.json"


def leer_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def guardar_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    return jsonify({"mensaje": "Servidor activo"})


@app.route("/config", methods=["POST"])
def config():
    data = request.json
    guardar_config(data)
    return jsonify({"mensaje": "Mapa guardado correctamente"})


@app.route("/actualizar")
def actualizar():
    config = leer_config()

    archivo, clientes, poligonos, con_poligono, sin_poligono = procesar_datos(
        config["mapa"]
    )

    return jsonify({
        "estado": "ok",
        "clientes": clientes,
        "poligonos": poligonos,
        "con_poligono": con_poligono,
        "sin_poligono": sin_poligono
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

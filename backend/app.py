from flask import Flask, jsonify, send_file
from processor import procesar_datos
import os

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"mensaje": "Servidor activo"})

@app.route("/actualizar")
def actualizar():
    archivo = procesar_datos()
    return send_file(archivo, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

from flask import Flask, jsonify, request, send_file
import pandas as pd
import os

app = Flask(__name__)

# =========================
# CONFIG
# =========================
PORT = int(os.environ.get("PORT", 5000))


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "OK",
        "message": "Zonificador API funcionando 🚀"
    })


# =========================
# ACTUALIZAR DATOS
# =========================
@app.route("/actualizar", methods=["GET"])
def actualizar():

    # 🔹 AQUÍ luego conectas Google My Maps real
    data = {
        "COD NUEVO": ["1001", "1002", "1003"],
        "codigo": ["001", "002", "003"],
        "cliente": ["Cliente A", "Cliente B", "Cliente C"],
        "poligono": ["Zona Norte", "Zona Sur", ""]
    }

    df = pd.DataFrame(data)

    # 🔹 métricas
    total_clientes = len(df)
    con_poligono = df[df["poligono"] != ""].shape[0]
    sin_poligono = df[df["poligono"] == ""].shape[0]
    total_poligonos = df["poligono"].nunique()

    # 🔹 generar Excel
    archivo = "clientes_actualizados.xlsx"
    df.to_excel(archivo, index=False)

    return jsonify({
        "clientes": total_clientes,
        "poligonos": total_poligonos,
        "con_poligono": con_poligono,
        "sin_poligono": sin_poligono,
        "archivo": archivo
    })


# =========================
# DESCARGAR EXCEL
# =========================
@app.route("/descargar", methods=["GET"])
def descargar():

    archivo = "clientes_actualizados.xlsx"

    if not os.path.exists(archivo):
        return jsonify({"error": "Archivo no existe"}), 404

    return send_file(
        archivo,
        as_attachment=True,
        download_name="zonificacion_clientes.xlsx"
    )


# =========================
# CONFIG MAPA
# =========================
@app.route("/config", methods=["POST"])
def config():

    data = request.get_json()
    mapa = data.get("mapa", "")

    # aquí luego lo guardas en DB o archivo
    return jsonify({
        "mensaje": "Mapa guardado correctamente",
        "mapa": mapa
    })


# =========================
# MAIN (IMPORTANTE PARA RENDER)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

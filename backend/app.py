from flask import Flask, jsonify, request, send_file
import pandas as pd
import os
from datetime import datetime
from shapely.geometry import Point, Polygon

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))

# =========================
# CONFIG GLOBAL (MAPA DINÁMICO)
# =========================
MAPA_LINK = ""


# =========================
# HOME
# =========================
@app.route("/")
def home():
    return jsonify({
        "status": "OK",
        "message": "Zonificador PRO activo 🚀"
    })


# =========================
# CONFIG MAPA DINÁMICO
# =========================
@app.route("/config", methods=["POST"])
def config():
    global MAPA_LINK

    data = request.get_json()
    MAPA_LINK = data.get("mapa", "")

    return jsonify({
        "mensaje": "Mapa actualizado correctamente",
        "mapa": MAPA_LINK
    })


# =========================
# MOTOR DE POLÍGONOS (SIMULADO LISTO PARA KML)
# =========================
def asignar_poligono(lat, lng):
    punto = Point(lat, lng)

    poligonos = {
        "Zona Norte": Polygon([(-12.10, -77.01), (-12.11, -77.02), (-12.12, -77.00)]),
        "Zona Sur": Polygon([(-12.20, -77.10), (-12.21, -77.11), (-12.22, -77.12)])
    }

    for nombre, poly in poligonos.items():
        if poly.contains(punto):
            return nombre

    return ""


# =========================
# ACTUALIZAR DATOS + EXCEL
# =========================
@app.route("/actualizar", methods=["GET"])
def actualizar():

    # =========================
    # DATA REAL ESTRUCTURA TUYA
    # =========================
    df = pd.DataFrame({
        "cliente": ["Cliente A", "Cliente B", "Cliente C", "Cliente D"],
        "longitud": [-77.01, -77.02, -77.03, -77.04],
        "latitud": [-12.10, -12.11, -12.12, -12.13],
        "PDV_ID": ["P001", "P002", "P003", "P004"],
        "DT": ["DT1", "DT1", "DT2", "DT2"],
        "NIVEL": ["A", "B", "A", "C"],
        "SEGMENTO": ["MODERNO", "TRADICIONAL", "MODERNO", "TRADICIONAL"],
        "COD NUEVO": ["1001", "1002", "1003", "1004"],
        "COD ANTIGUO": ["A001", "A002", "A003", "A004"],
        "DIRECCION": ["Av A", "Av B", "Av C", "Av D"],
        "DISTRITO": ["Lima", "Breña", "Callao", "Surco"],
        "LATITUD": [-12.10, -12.11, -12.12, -12.13],
        "LONGITUD": [-77.01, -77.02, -77.03, -77.04],
        "CANAL": ["BODEGA", "MAYORISTA", "MINIMARKET", "BODEGA"],
        "GIRO": ["ABARROTES", "LICORES", "ABARROTES", "LICORES"],
        "TIPO FACHADA": ["SI", "NO", "SI", "NO"],
        "SUPERVISOR 1": ["SUP1", "SUP1", "SUP2", "SUP2"],
        "COD VENDEDOR 1": ["V01", "V02", "V03", "V04"],
        "VENDEDOR 1": ["Juan", "Pedro", "Luis", "Ana"],
        "RUTA GENERALES": ["R1", "R1", "R2", "R2"],
        "DÍA VISITA VENTAS": ["LUN", "MAR", "MIE", "JUE"],
        "DÍA DE DESPACHO": ["LUN", "MAR", "MIE", "JUE"],
        "DÍA DE VISITA": ["LUN", "MAR", "MIE", "JUE"],
        "FECHA DE VISITA 1": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "FECHA DE VISITA 2": ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08"],
        "ID MERC": ["M1", "M2", "M3", "M4"],
        "MERCADERISTA": ["A", "B", "C", "D"],
        "ID SUPER": ["S1", "S2", "S3", "S4"],
        "SUPERVISOR": ["Carlos", "Miguel", "Jose", "Luis"],
        "COMENT 1": ["OK", "", "REVISAR", "OK"],
        "COMENT 2": ["", "", "", ""],
        "COMENT 3": ["", "", "", ""],
        "poligono": ["" for _ in range(4)]
    })

    # =========================
    # ASIGNACIÓN AUTOMÁTICA
    # =========================
    df["poligono"] = df.apply(
        lambda row: asignar_poligono(row["latitud"], row["longitud"]),
        axis=1
    )

    # =========================
    # KPIs
    # =========================
    total = len(df)
    con_poligono = df[df["poligono"] != ""].shape[0]
    sin_poligono = df[df["poligono"] == ""].shape[0]

    df["FECHA_ACTUALIZACION"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # =========================
    # EXCEL
    # =========================
    archivo = "zonificacion_final.xlsx"
    df.to_excel(archivo, index=False)

    return jsonify({
        "clientes": total,
        "con_poligono": con_poligono,
        "sin_poligono": sin_poligono,
        "archivo": archivo
    })


# =========================
# DESCARGA
# =========================
@app.route("/descargar", methods=["GET"])
def descargar():

    archivo = "zonificacion_final.xlsx"

    return send_file(
        archivo,
        as_attachment=True,
        download_name="zonificacion_final.xlsx"
    )


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

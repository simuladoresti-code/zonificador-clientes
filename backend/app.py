from flask import Flask, jsonify, request, send_file
import requests
import pandas as pd
from shapely.geometry import Point, Polygon
from datetime import datetime
import os

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))


# =========================
# 🔥 DESCARGAR KML DESDE MY MAPS
# =========================
def get_kml(mid):
    url = f"https://www.google.com/maps/d/kml?mid={mid}"
    r = requests.get(url)

    if r.status_code != 200:
        raise Exception("No se pudo descargar KML")

    return r.content


# =========================
# 🔥 PARSER UNIVERSAL (SIN CAPAS)
# =========================
from fastkml import kml

def parse_kml(kml_data):

    k = kml.KML()
    k.from_string(kml_data)

    clientes = []
    poligonos = []

    def walk(features):

        for f in features:

            if hasattr(f, "features"):
                walk(f.features())

            else:

                geom = getattr(f, "geometry", None)
                name = getattr(f, "name", "SIN_NOMBRE")

                if not geom:
                    continue

                # =====================
                # CLIENTES (POINT)
                # =====================
                if geom.geom_type == "Point":
                    clientes.append({
                        "nombre": name,
                        "lat": geom.y,
                        "lng": geom.x
                    })

                # =====================
                # POLÍGONOS (POLYGON)
                # =====================
                elif geom.geom_type == "Polygon":
                    coords = list(geom.exterior.coords)

                    poligonos.append({
                        "nombre": name,
                        "polygon": Polygon(coords)
                    })

    walk(k.features())

    return clientes, poligonos


# =========================
# 🔥 ASIGNACIÓN DE ZONA
# =========================
def asignar_zona(lat, lng, poligonos):

    punto = Point(lng, lat)

    for zona in poligonos:
        if zona["polygon"].contains(punto):
            return zona["nombre"]

    return "SIN ZONA"


# =========================
# 🚀 ENDPOINT PRINCIPAL
# =========================
@app.route("/actualizar", methods=["GET"])
def actualizar():

    mid = request.args.get("mid")

    if not mid:
        return jsonify({"error": "Falta MID del mapa"}), 400

    # =====================
    # 1. KML
    # =====================
    kml_data = get_kml(mid)

    # =====================
    # 2. PARSE
    # =====================
    clientes, poligonos = parse_kml(kml_data)

    # =====================
    # 3. DATAFRAME CLIENTES
    # =====================
    df = pd.DataFrame(clientes)

    # =====================
    # 4. ASIGNAR ZONAS
    # =====================
    df["poligono"] = df.apply(
        lambda r: asignar_zona(r["lat"], r["lng"], poligonos),
        axis=1
    )

    # =====================
    # 5. KPIs
    # =====================
    total = len(df)
    con = df[df["poligono"] != "SIN ZONA"].shape[0]
    sin = df[df["poligono"] == "SIN ZONA"].shape[0]

    df["fecha_proceso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # =====================
    # 6. EXCEL
    # =====================
    file = "zonificacion.xlsx"
    df.to_excel(file, index=False)

    return send_file(
        file,
        as_attachment=True,
        download_name="zonificacion_final.xlsx"
    )


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return jsonify({"status": "OK"})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

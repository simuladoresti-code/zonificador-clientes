from flask import Flask, jsonify, request, send_file
import requests
import pandas as pd
from shapely.geometry import Point, Polygon
from fastkml import kml
from datetime import datetime
import os

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))


# =========================
# 🔥 DESCARGA KML DESDE GOOGLE MY MAPS
# =========================
def obtener_kml(mid):
    url = f"https://www.google.com/maps/d/kml?mid={mid}"
    r = requests.get(url)
    return r.content


# =========================
# 🔥 PARSEO KML (CLIENTES + POLÍGONOS)
# =========================
def parse_kml(kml_data):

    k = kml.KML()
    k.from_string(kml_data)

    clientes = []
    poligonos = {}

    def walk_features(features):
        for f in features:
            name = getattr(f, "name", None)

            if hasattr(f, "features"):
                walk_features(f.features())
            else:

                geom = f.geometry

                # =====================
                # POINT = CLIENTE
                # =====================
                if geom and geom.geom_type == "Point":
                    clientes.append({
                        "nombre": name,
                        "lng": geom.x,
                        "lat": geom.y
                    })

                # =====================
                # POLYGON = ZONA
                # =====================
                if geom and geom.geom_type == "Polygon":
                    coords = list(geom.exterior.coords)
                    poly = Polygon(coords)
                    poligonos[name] = poly

    walk_features(k.features())

    return clientes, poligonos


# =========================
# 🔥 ASIGNAR ZONA
# =========================
def asignar_zona(lat, lng, poligonos):
    punto = Point(lng, lat)

    for nombre, poly in poligonos.items():
        if poly.contains(punto):
            return nombre

    return "SIN ZONA"


# =========================
# 🚀 MAIN: PROCESO COMPLETO
# =========================
@app.route("/actualizar", methods=["GET"])
def actualizar():

    mid = request.args.get("mid")

    if not mid:
        return jsonify({"error": "Falta mid del mapa"}), 400

    # =====================
    # 1. KML
    # =====================
    kml_data = obtener_kml(mid)

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
    # 5. KPI
    # =====================
    total = len(df)
    con_zona = df[df["poligono"] != "SIN ZONA"].shape[0]
    sin_zona = df[df["poligono"] == "SIN ZONA"].shape[0]

    df["FECHA"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
# HEALTH
# =========================
@app.route("/")
def home():
    return jsonify({"status": "OK"})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

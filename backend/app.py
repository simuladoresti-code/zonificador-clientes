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
# DESCARGAR KML
# =========================
def get_kml(mid):
    url = f"https://www.google.com/maps/d/kml?mid={mid}"
    r = requests.get(url)

    if r.status_code != 200:
        raise Exception("No se pudo descargar KML")

    return r.content


# =========================
# PARSER KML
# =========================
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
                name = getattr(f, "name", "SIN")

                if not geom:
                    continue

                if geom.geom_type == "Point":
                    clientes.append({
                        "cliente": name,
                        "lat": geom.y,
                        "lng": geom.x
                    })

                elif geom.geom_type == "Polygon":
                    coords = list(geom.exterior.coords)
                    poligonos.append({
                        "nombre": name,
                        "polygon": Polygon(coords)
                    })

    walk(k.features())

    return clientes, poligonos


# =========================
# MATCH
# =========================
def asignar(lat, lng, poligonos):
    p = Point(lng, lat)

    for z in poligonos:
        if z["polygon"].contains(p):
            return z["nombre"]

    return "SIN ZONA"


# =========================
# MAIN
# =========================
@app.route("/actualizar", methods=["GET"])
def actualizar():

    try:
        mid = request.args.get("mid")

        if not mid:
            return jsonify({"error": "Falta MID"}), 400

        # 1. KML
        kml_data = get_kml(mid)

        # 2. PARSE
        clientes, poligonos = parse_kml(kml_data)

        # 3. DF
        df = pd.DataFrame(clientes)

        if df.empty:
            return jsonify({"error": "No hay clientes en el KML"}), 400

        # 4. ZONAS
        df["poligono"] = df.apply(
            lambda r: asignar(r["lat"], r["lng"], poligonos),
            axis=1
        )

        # 5. TEMP FILE (IMPORTANTE EN RENDER)
        file_path = "/tmp/zonificacion.xlsx"

        df.to_excel(file_path, index=False)

        return send_file(
            file_path,
            as_attachment=True,
            download_name="zonificacion.xlsx"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"status": "OK"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)

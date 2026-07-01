from flask import Flask, send_file, jsonify
import pandas as pd
from shapely.geometry import Point, Polygon
from fastkml import kml
from datetime import datetime
import os

app = Flask(__name__)

KML_PATH = "data/mapa.kml"


# =========================
# LEER KML LOCAL
# =========================
def load_kml_file():

    if not os.path.exists(KML_PATH):
        raise Exception("No existe mapa.kml en /data")

    with open(KML_PATH, "rb") as f:
        return f.read()


# =========================
# PARSE KML
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

                if geom is None:
                    continue

                # CLIENTES
                if geom.geom_type == "Point":
                    clientes.append({
                        "cliente": name,
                        "lat": geom.y,
                        "lng": geom.x
                    })

                # POLIGONOS
                elif geom.geom_type == "Polygon":
                    coords = list(geom.exterior.coords)

                    poligonos.append({
                        "nombre": name,
                        "polygon": Polygon(coords)
                    })

    walk(k.features())

    return clientes, poligonos


# =========================
# MATCH GEO
# =========================
def asignar_zona(lat, lng, poligonos):

    punto = Point(lng, lat)

    for p in poligonos:
        if p["polygon"].contains(punto):
            return p["nombre"]

    return "SIN ZONA"


# =========================
# ENDPOINT
# =========================
@app.route("/actualizar", methods=["GET"])
def actualizar():

    try:

        # 1. CARGAR KML LOCAL
        kml_data = load_kml_file()

        # 2. PARSE
        clientes, poligonos = parse_kml(kml_data)

        if not clientes:
            return jsonify({"error": "No hay clientes en el KML"}), 400

        # 3. DATAFRAME
        df = pd.DataFrame(clientes)

        # 4. CRUCE
        df["poligono"] = df.apply(
            lambda r: asignar_zona(r["lat"], r["lng"], poligonos),
            axis=1
        )

        df["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 5. EXCEL
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
    app.run(host="0.0.0.0", port=5000)

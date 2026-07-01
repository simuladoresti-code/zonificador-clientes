from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pandas as pd
from shapely.geometry import Point, Polygon
from fastkml import kml
import zipfile
import io
from datetime import datetime

app = Flask(__name__)
CORS(app)


# =========================
# LEER KML / KMZ
# =========================
def read_kml(file):

    filename = file.filename
    data = file.read()

    # KMZ → extraer KML
    if filename.endswith(".kmz"):
        z = zipfile.ZipFile(io.BytesIO(data))
        kml_file = [f for f in z.namelist() if f.endswith(".kml")][0]
        return z.read(kml_file)

    return data


# =========================
# PARSE CLIENTES
# =========================
def parse_clientes(kml_data):

    k = kml.KML()
    k.from_string(kml_data)

    clientes = []

    def walk(features):
        for f in features:

            if hasattr(f, "features"):
                walk(f.features())

            else:
                geom = getattr(f, "geometry", None)
                name = getattr(f, "name", "SIN")

                if geom and geom.geom_type == "Point":
                    clientes.append({
                        "cliente": name,
                        "lat": geom.y,
                        "lng": geom.x
                    })

    walk(k.features())
    return clientes


# =========================
# PARSE POLIGONOS
# =========================
def parse_poligonos(kml_data):

    k = kml.KML()
    k.from_string(kml_data)

    poligonos = []

    def walk(features):
        for f in features:

            if hasattr(f, "features"):
                walk(f.features())

            else:
                geom = getattr(f, "geometry", None)
                name = getattr(f, "name", "SIN ZONA")

                if geom and geom.geom_type == "Polygon":
                    coords = list(geom.exterior.coords)

                    poligonos.append({
                        "nombre": name,
                        "polygon": Polygon(coords)
                    })

    walk(k.features())
    return poligonos


# =========================
# ASIGNAR ZONA
# =========================
def asignar(lat, lng, poligonos):

    punto = Point(lng, lat)

    for p in poligonos:
        if p["polygon"].contains(punto):
            return p["nombre"]

    return "SIN ZONA"


# =========================
# ENDPOINT PRINCIPAL
# =========================
@app.route("/actualizar", methods=["POST"])
def actualizar():

    try:

        if "clientes" not in request.files or "poligonos" not in request.files:
            return jsonify({"error": "Faltan archivos KML/KMZ"}), 400

        clientes_file = request.files["clientes"]
        poligonos_file = request.files["poligonos"]

        clientes_kml = read_kml(clientes_file)
        poligonos_kml = read_kml(poligonos_file)

        clientes = parse_clientes(clientes_kml)
        poligonos = parse_poligonos(poligonos_kml)

        if len(clientes) == 0:
            return jsonify({"error": "No se detectaron clientes"}), 400

        df = pd.DataFrame(clientes)

        df["poligono"] = df.apply(
            lambda r: asignar(r["lat"], r["lng"], poligonos),
            axis=1
        )

        df["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        path = "/tmp/zonificacion.xlsx"
        df.to_excel(path, index=False)

        return send_file(path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return jsonify({"status": "OK"})


if __name__ == "__main__":
    app.run()

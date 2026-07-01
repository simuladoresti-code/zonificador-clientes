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
# LEER KML / KMZ (ROBUSTO)
# =========================
def read_kml(file):

    data = file.read()
    filename = file.filename.lower()

    try:

        # -------------------------
        # KMZ
        # -------------------------
        if filename.endswith(".kmz"):

            z = zipfile.ZipFile(io.BytesIO(data))

            # buscar TODOS los kml dentro
            kml_files = [f for f in z.namelist() if f.endswith(".kml")]

            if not kml_files:
                raise Exception("KMZ no contiene archivos KML")

            # usar el primero (más seguro para MyMaps)
            kml_data = z.read(kml_files[0])

            return kml_data

        # -------------------------
        # KML normal
        # -------------------------
        return data

    except Exception as e:
        print("ERROR KMZ:", str(e))
        raise Exception(f"Error leyendo archivo: {str(e)}")


# =========================
# CLIENTES (POINTS)
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
                name = getattr(f, "name", "SIN NOMBRE")

                if geom and geom.geom_type == "Point":
                    clientes.append({
                        "cliente": name,
                        "lat": geom.y,
                        "lng": geom.x
                    })

    walk(k.features())
    return clientes


# =========================
# POLÍGONOS
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
# ASIGNACIÓN DE ZONA
# =========================
def asignar_zona(lat, lng, poligonos):

    punto = Point(lng, lat)

    for p in poligonos:
        try:
            if p["polygon"].contains(punto):
                return p["nombre"]
        except:
            continue

    return "SIN ZONA"


# =========================
# ENDPOINT PRINCIPAL
# =========================
@app.route("/actualizar", methods=["POST"])
def actualizar():

    try:

        print("🚀 INICIO PROCESO")

        if "clientes" not in request.files or "poligonos" not in request.files:
            return jsonify({"error": "Faltan archivos"}), 400

        clientes_file = request.files["clientes"]
        poligonos_file = request.files["poligonos"]

        print("CLIENTES:", clientes_file.filename)
        print("POLIGONOS:", poligonos_file.filename)

        # -------------------------
        # LEER ARCHIVOS
        # -------------------------
        clientes_kml = read_kml(clientes_file)
        poligonos_kml = read_kml(poligonos_file)

        # -------------------------
        # PARSE
        # -------------------------
        clientes = parse_clientes(clientes_kml)
        poligonos = parse_poligonos(poligonos_kml)

        print("CLIENTES DETECTADOS:", len(clientes))
        print("POLIGONOS DETECTADOS:", len(poligonos))

        if len(clientes) == 0:
            return jsonify({"error": "No se detectaron clientes en el KML"}), 400

        # -------------------------
        # DATAFRAME
        # -------------------------
        df = pd.DataFrame(clientes)

        df["poligono"] = df.apply(
            lambda r: asignar_zona(r["lat"], r["lng"], poligonos),
            axis=1
        )

        df["fecha_proceso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # -------------------------
        # EXPORT EXCEL
        # -------------------------
        path = "/tmp/zonificacion.xlsx"
        df.to_excel(path, index=False)

        print("✅ EXCEL GENERADO")

        return send_file(path, as_attachment=True)

    except Exception as e:

        print("❌ ERROR BACKEND:", str(e))

        return jsonify({
            "error": str(e)
        }), 500


# =========================
# HEALTH CHECK
# =========================
@app.route("/")
def home():
    return jsonify({"status": "OK", "message": "Zonificador activo"})


# =========================
# RUN LOCAL
# =========================
if __name__ == "__main__":
    app.run(debug=True)

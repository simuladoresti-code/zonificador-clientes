import requests
import zipfile
import os
import pandas as pd
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon

MAP_ID = "1KhMBbBH-KMzsH8kuZ_QmLiqJKUclL8E"
KML_URL = f"https://www.google.com/maps/d/kml?mid={MAP_ID}"

def limpiar():
    if os.path.exists("mapa.kmz"):
        os.remove("mapa.kmz")

    if os.path.exists("mapa_extraido"):
        import shutil
        shutil.rmtree("mapa_extraido")

def descargar_kml():
    response = requests.get(KML_URL)

    with open("mapa.kmz", "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile("mapa.kmz", "r") as zip_ref:
        zip_ref.extractall("mapa_extraido")

def buscar_kml():
    for root, dirs, files in os.walk("mapa_extraido"):
        for file in files:
            if file.endswith(".kml"):
                return os.path.join(root, file)
    return None

def extraer_datos(kml_path):
    tree = ET.parse(kml_path)
    root = tree.getroot()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    clientes = []
    poligonos = []

    for placemark in root.findall(".//kml:Placemark", ns):

        nombre = placemark.find("kml:name", ns)

        point = placemark.find(".//kml:Point/kml:coordinates", ns)
        polygon = placemark.find(".//kml:Polygon//kml:coordinates", ns)

        if point is not None:
            coords = point.text.strip().split(",")

            clientes.append({
                "cliente": nombre.text if nombre is not None else "Sin nombre",
                "longitud": float(coords[0]),
                "latitud": float(coords[1])
            })

        if polygon is not None:
            coords_text = polygon.text.strip().split()

            coords = []
            for c in coords_text:
                parts = c.split(",")
                coords.append((float(parts[0]), float(parts[1])))

            poligonos.append({
                "nombre": nombre.text if nombre is not None else "Sin nombre",
                "poligono": Polygon(coords)
            })

    return clientes, poligonos

def asignar_zonas(clientes, poligonos):
    resultado = []

    for cliente in clientes:
        punto = Point(cliente["longitud"], cliente["latitud"])
        zona = "Sin zona"

        for p in poligonos:
            if p["poligono"].contains(punto):
                zona = p["nombre"]
                break

        cliente["zona"] = zona
        resultado.append(cliente)

    return resultado

def procesar_datos():
    limpiar()
    descargar_kml()
    archivo_kml = buscar_kml()

    clientes, poligonos = extraer_datos(archivo_kml)

    resultado = asignar_zonas(clientes, poligonos)

    df = pd.DataFrame(resultado)

    archivo_salida = "clientes_actualizados.xlsx"
    df.to_excel(archivo_salida, index=False)

    return archivo_salida

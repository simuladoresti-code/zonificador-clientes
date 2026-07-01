import requests
import zipfile
import os
import pandas as pd
import xml.etree.ElementTree as ET

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

def extraer_clientes(kml_path):
    tree = ET.parse(kml_path)
    root = tree.getroot()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    clientes = []

    for placemark in root.findall(".//kml:Placemark", ns):
        nombre = placemark.find("kml:name", ns)
        point = placemark.find(".//kml:Point/kml:coordinates", ns)

        if point is not None:
            coords = point.text.strip().split(",")

            clientes.append({
                "cliente": nombre.text if nombre is not None else "Sin nombre",
                "longitud": float(coords[0]),
                "latitud": float(coords[1]),
                "zona": "Pendiente"
            })

    return clientes

def procesar_datos():
    limpiar()
    descargar_kml()
    archivo_kml = buscar_kml()

    if not archivo_kml:
        raise Exception("No se encontró archivo KML")

    clientes = extraer_clientes(archivo_kml)

    df = pd.DataFrame(clientes)

    archivo_salida = "clientes_actualizados.xlsx"
    df.to_excel(archivo_salida, index=False)

    return archivo_salida

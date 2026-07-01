import requests
import zipfile
import os
import shutil
import pandas as pd
import xml.etree.ElementTree as ET
from shapely.geometry import Point, Polygon

# ID de tu Google My Maps
MAP_ID = "1KhMBbBH-KMzsH8kuZ_QmLiqJKUclL8E"

# URL de descarga KMZ
KML_URL = f"https://www.google.com/maps/d/kml?mid={MAP_ID}"


# limpiar archivos anteriores
def limpiar():
    if os.path.exists("mapa.kmz"):
        os.remove("mapa.kmz")

    if os.path.exists("mapa_extraido"):
        shutil.rmtree("mapa_extraido")


# descargar kmz
def descargar_kml():
    response = requests.get(KML_URL)

    if response.status_code != 200:
        raise Exception("Error descargando el mapa")

    with open("mapa.kmz", "wb") as f:
        f.write(response.content)

    with zipfile.ZipFile("mapa.kmz", "r") as zip_ref:
        zip_ref.extractall("mapa_extraido")


# buscar archivo kml
def buscar_kml():
    for root, dirs, files in os.walk("mapa_extraido"):
        for file in files:
            if file.endswith(".kml"):
                return os.path.join(root, file)

    return None


# extraer clientes y poligonos
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

        # CLIENTES (PUNTOS)
        if point is not None:
            coords = point.text.strip().split(",")

            cliente_data = {
                "cliente": nombre.text if nombre is not None else "Sin nombre",
                "longitud": float(coords[0]),
                "latitud": float(coords[1])
            }

            # traer todos los campos del cliente
            extended_data = placemark.findall(".//kml:Data", ns)

            for data in extended_data:
                campo = data.attrib.get("name")
                valor = data.find("kml:value", ns)

                if campo and valor is not None:
                    cliente_data[campo] = valor.text

            clientes.append(cliente_data)

        # POLIGONOS
        if polygon is not None:
            coords_text = polygon.text.strip().split()

            lista_coords = []

            for c in coords_text:
                partes = c.split(",")
                lista_coords.append(
                    (float(partes[0]), float(partes[1]))
                )

            poligonos.append({
                "nombre": nombre.text if nombre is not None else "Sin nombre",
                "poligono": Polygon(lista_coords)
            })

    return clientes, poligonos


# asignar poligonos a clientes
def asignar_poligonos(clientes, poligonos):
    resultado = []

    for cliente in clientes:
        punto = Point(cliente["longitud"], cliente["latitud"])
        nombre_poligono = "Sin poligono"

        for p in poligonos:
            if p["poligono"].contains(punto):
                nombre_poligono = p["nombre"]
                break

        cliente["poligono"] = nombre_poligono

        resultado.append(cliente)

    return resultado


# proceso principal
def procesar_datos():
    limpiar()
    descargar_kml()

    archivo_kml = buscar_kml()

    if not archivo_kml:
        raise Exception("No se encontró archivo KML")

    clientes, poligonos = extraer_datos(archivo_kml)

    resultado = asignar_poligonos(clientes, poligonos)

    df = pd.DataFrame(resultado)

    archivo_salida = "clientes_actualizados.xlsx"

    df.to_excel(archivo_salida, index=False)

    return archivo_salida

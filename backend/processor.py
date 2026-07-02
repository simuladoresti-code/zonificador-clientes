import zipfile
import xml.etree.ElementTree as ET
import pandas as pd
from shapely.geometry import Point, Polygon


def extraer_kml(kmz_path, carpeta_temp):
    with zipfile.ZipFile(kmz_path, "r") as kmz:
        kmz.extractall(carpeta_temp)

    return f"{carpeta_temp}/doc.kml"


def leer_clientes(kml_path):
    """
    Lee clientes del KML extrayendo TODAS las propiedades disponibles
    """
    tree = ET.parse(kml_path)
    root = tree.getroot()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    clientes = []

    for placemark in root.findall(".//kml:Placemark", ns):
        # Nombre del cliente
        nombre_elem = placemark.find("kml:name", ns)
        nombre = nombre_elem.text if nombre_elem is not None else ""

        # Coordenadas
        point = placemark.find(".//kml:Point/kml:coordinates", ns)

        if point is not None:
            coords = point.text.strip().split(",")
            lon = float(coords[0])
            lat = float(coords[1])

            # Extraer propiedades extendidas (ExtendedData)
            cliente_data = {
                "nombre": nombre,
                "lat": lat,
                "lon": lon
            }

            # Leer todos los campos de ExtendedData si existen
            extended_data = placemark.find("kml:ExtendedData", ns)
            if extended_data is not None:
                for data_elem in extended_data.findall("kml:Data", ns):
                    nombre_campo = data_elem.get("name")
                    valor_elem = data_elem.find("kml:value", ns)
                    if nombre_campo and valor_elem is not None:
                        cliente_data[nombre_campo] = valor_elem.text if valor_elem.text else ""

            clientes.append(cliente_data)

    return clientes


def leer_poligonos(kml_path):
    tree = ET.parse(kml_path)
    root = tree.getroot()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}

    poligonos = []

    for placemark in root.findall(".//kml:Placemark", ns):
        nombre = placemark.find("kml:name", ns)

        poly = placemark.find(
            ".//kml:Polygon//kml:coordinates",
            ns
        )

        if poly is not None:
            puntos = []

            coords = poly.text.strip().split()

            for coord in coords:
                lon, lat, *_ = coord.split(",")
                puntos.append((float(lon), float(lat)))

            poligonos.append({
                "nombre": nombre.text if nombre is not None else "",
                "polygon": Polygon(puntos)
            })

    return poligonos


def asignar_poligono(clientes, poligonos):
    """
    Asigna polígono a cada cliente manteniendo TODAS sus propiedades originales
    """
    resultado = []

    for cliente in clientes:
        punto = Point(cliente["lon"], cliente["lat"])
        zona = ""

        for pol in poligonos:
            if pol["polygon"].contains(punto):
                zona = pol["nombre"]
                break

        # Copiar cliente con todas sus propiedades
        cliente_resultado = cliente.copy()
        # Agregar polígono al final
        cliente_resultado["poligono"] = zona

        resultado.append(cliente_resultado)

    return resultado


def procesar_datos(clientes_kmz, poligonos_kmz):

    clientes_kml = extraer_kml(clientes_kmz, "clientes_temp")
    poligonos_kml = extraer_kml(poligonos_kmz, "poligonos_temp")

    clientes = leer_clientes(clientes_kml)
    poligonos = leer_poligonos(poligonos_kml)

    resultado = asignar_poligono(clientes, poligonos)

    df = pd.DataFrame(resultado)

    archivo = "clientes_actualizados.xlsx"
    df.to_excel(archivo, index=False)

    return archivo, len(clientes), len(poligonos)

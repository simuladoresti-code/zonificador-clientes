import zipfile
import pandas as pd


def procesar_datos(clientes_kmz, poligonos_kmz):

    with zipfile.ZipFile(clientes_kmz, "r") as kmz:
        kmz.extractall("clientes_temp")

    with zipfile.ZipFile(poligonos_kmz, "r") as kmz:
        kmz.extractall("poligonos_temp")

    # aquí parseas KML
    # cruzas puntos vs polígonos

    data = {
        "COD NUEVO": ["1001"],
        "cliente": ["Cliente A"],
        "poligono": ["Zona Norte"]
    }

    df = pd.DataFrame(data)

    df.to_excel("clientes_actualizados.xlsx", index=False)

    return "clientes_actualizados.xlsx", len(df), 1

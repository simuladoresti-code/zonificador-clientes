import pandas as pd


def procesar_datos(link_mapa):

    # aquí luego conectas tu lógica real
    # clientes + polígonos salen del mismo mapa

    data = {
        "COD NUEVO": ["1001", "1002", "1003"],
        "codigo": ["001", "002", "003"],
        "cliente": ["Cliente A", "Cliente B", "Cliente C"],
        "poligono": ["Zona Norte", "Zona Sur", ""]
    }

    df = pd.DataFrame(data)

    con_poligono = df[df["poligono"] != ""].shape[0]
    sin_poligono = df[df["poligono"] == ""].shape[0]

    archivo = "clientes_actualizados.xlsx"
    df.to_excel(archivo, index=False)

    return archivo, len(df), 2, con_poligono, sin_poligono

    archivo_salida = "clientes_actualizados.xlsx"

    df.to_excel(archivo_salida, index=False)

    return archivo_salida

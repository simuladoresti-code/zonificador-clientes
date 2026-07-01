import pandas as pd

def procesar_datos(link_mapa):

    # 🔹 SIMULACIÓN (luego conectas scraping Google My Maps)
    data = {
        "COD NUEVO": ["1001", "1002", "1003"],
        "codigo": ["001", "002", "003"],
        "cliente": ["Cliente A", "Cliente B", "Cliente C"],
        "poligono": ["Zona Norte", "Zona Sur", ""]
    }

    df = pd.DataFrame(data)

    # 🔹 métricas reales
    total_clientes = len(df)
    con_poligono = df[df["poligono"] != ""].shape[0]
    sin_poligono = df[df["poligono"] == ""].shape[0]

    total_poligonos = df["poligono"].nunique()

    # 🔹 export Excel
    archivo = "clientes_actualizados.xlsx"
    df.to_excel(archivo, index=False)

    return {
        "archivo": archivo,
        "clientes": total_clientes,
        "poligonos": total_poligonos,
        "con_poligono": con_poligono,
        "sin_poligono": sin_poligono
    }

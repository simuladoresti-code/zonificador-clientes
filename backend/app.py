@app.route("/actualizar")
def actualizar():

    archivo, clientes, poligonos = procesar_datos(
        "clientes.kmz",
        "poligonos.kmz"
    )

    return jsonify({
        "estado": "ok",
        "clientes": clientes,
        "poligonos": poligonos
    })

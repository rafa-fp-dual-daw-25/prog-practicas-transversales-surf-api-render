from click import option
import json
import os

ARCHIVO_DB = "playas.json"


def cargar_playas():
    if os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_playa(playas_dict):
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(playas_dict, f, ensure_ascii=False, indent=4)


def generar_selector_html(diccionario_playas):
    brasil = ""
    espana = ""

    playas_ordenadas = sorted(diccionario_playas.items(), key=lambda x: x[1]['nombre'])

    for id_p, info in playas_ordenadas:
        option = f'<option value="{id_p}">{info["nombre"]}</option>'

        if info["pais"] == "Brasil":
            brasil += option
        else:
            espana += option

    return f"""
        <optgroup label="Brasil">
            {brasil}
        </optgroup>
        <optgroup label="España">
            {espana}
        </optgroup>
    """


def transformar_grados_a_direccion(grados: float):
    if grados is None:
        return "N/A"

    direcciones = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]
    indice = int((grados + 22.5) / 45) % 8

    return direcciones[indice]

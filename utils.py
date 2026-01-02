import json
import os

ARCHIVO_DB = "playas.json"


def cargar_playas():
    """
    Leer el archivo JSON local para recuperar las playas guardadas.
    Si el archivo no existe, retornar un diccionario vacío para evitar errores.
    """
    if os.path.exists(ARCHIVO_DB):
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_playa(playas_dict):
    """
    Sobrescribir el archivo JSON con el estado actual del diccionario.
    ensure_ascii=False permite guardar tildes y ñ correctamente.
    indent=4 hace que el archivo sea legible para humanos.
    """
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(playas_dict, f, ensure_ascii=False, indent=4)


def generar_selector_html(diccionario_playas):
    """
    Construir las opciones del <select> HTML dinámicamente.
    Separar por países y ordenar alfabéticamente por nombre para mejorar UX.
    """
    brasil = ""
    espana = ""
    portugal = ""

    # Ordenar diccionario por la clave 'nombre' antes de iterar
    playas_ordenadas = sorted(diccionario_playas.items(), key=lambda x: x[1]['nombre'])

    for id_p, info in playas_ordenadas:
        option = f'<option value="{id_p}">{info["nombre"]}</option>'

        if info["pais"] == "Brasil":
            brasil += option
        elif info["pais"] == "Portugal":
            portugal += option
        else:
            espana += option

    # Retornar string con grupos de opciones (optgroup)
    return f"""
        <optgroup label="Brasil">
            {brasil}
        </optgroup>
        <optgroup label="España">
            {espana}
        </optgroup>
        <optgroup label="Portugal">
            {portugal}
        </optgroup>
    """


def transformar_grados_a_direccion(grados: float):
    """
    Convertir grados meteorológicos (0-360) a texto cardinal (Norte, Sur, etc).
    """
    if grados is None:
        return "N/A"

    direcciones = ["Norte", "Noreste", "Este", "Sureste", "Sur", "Suroeste", "Oeste", "Noroeste"]

    # Fórmula matemática para dividir los 360º en 8 sectores
    indice = int((grados + 22.5) / 45) % 8

    return direcciones[indice]

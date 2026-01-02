from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from utils import cargar_playas, guardar_playa, generar_selector_html, transformar_grados_a_direccion
import requests

app = FastAPI()

# Configurar carpeta "static" para servir CSS y JS al navegador
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurar motor de plantillas Jinja2 para renderizar HTML dinámico
templates = Jinja2Templates(directory="templates")

# Cargar base de datos inicial (JSON) en memoria RAM al arrancar la app
PLAYAS = cargar_playas()


# Definir esquema de datos para validación de entrada (POST)
class PlayaNueva(BaseModel):
    id: str
    nombre: str
    lat: float
    long: float
    pais: str


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    """
    Ruta principal: Generar el HTML inicial con el selector de playas cargado.
    """
    opciones = generar_selector_html(PLAYAS)

    # Renderizar index.html inyectando las opciones generadas
    return templates.TemplateResponse("index.html", {
        "request": request,
        "opciones_dinamicas": opciones
    })


@app.get("/surf/{playa}")
def get_surf_forecast(playa: str):
    """
    Consultar APIs externas de Open-Meteo para obtener datos de olas y viento.
    """
    playa_id = playa.lower()

    # Validar si la playa existe en nuestro registro
    if playa_id not in PLAYAS:
        raise HTTPException(status_code=404, detail="Playa no encontrada")

    coords = PLAYAS[playa_id]

    # Construir URLs para las APIs externas (Marine API y Forecast API)
    url_olas = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={coords['lat']}&longitude={coords['long']}"
        f"&current=wave_height,wave_direction,wave_period"
        f"&timezone=auto"
    )

    url_viento = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coords['lat']}&longitude={coords['long']}"
        f"&current=wind_speed_10m,wind_direction_10m"
        f"&timezone=auto"
    )

    # Realizar peticiones HTTP síncronas a los servicios externos
    try:
        response_olas = requests.get(url_olas).json()
        response_viento = requests.get(url_viento).json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error conectando con Open-Meteo")

    # Extraer datos específicos de la respuesta JSON
    datos_olas = response_olas.get("current", {})
    datos_viento = response_viento.get("current", {})

    # Convertir direcciones numéricas a texto legible
    dir_olas_txt = transformar_grados_a_direccion(datos_olas.get("wave_direction"))
    dir_viento_txt = transformar_grados_a_direccion(datos_viento.get("wind_direction_10m"))

    # Estructurar respuesta final para el frontend
    return {
        "playa": coords["nombre"],
        "latitud": coords["lat"],
        "longitud": coords["long"],
        "prevision_actual": {
            "olas": {
                "altura_metros": datos_olas.get("wave_height"),
                "direccion_grados": datos_olas.get("wave_direction"),
                "direccion_texto": dir_olas_txt,
                "periodo_segundos": datos_olas.get("wave_period")
            },
            "viento": {
                "velocidad_kmh": datos_viento.get("wind_speed_10m"),
                "direccion_grados": datos_viento.get("wind_direction_10m"),
                "direccion_texto": dir_viento_txt
            },
            "momento_lectura": datos_olas.get("time")
        }
    }


@app.post("/playas/add")
def agregar_playa(playa: PlayaNueva):
    """
    Recibir una nueva playa, validarla y guardarla en memoria y disco.
    """
    playa_id = playa.id.lower().strip()

    if playa_id in PLAYAS:
        raise HTTPException(status_code=400, detail="El ID de esta playa ya existe.")

    # Actualizar diccionario en memoria
    PLAYAS[playa_id] = {
        "lat": playa.lat,
        "long": playa.long,
        "nombre": playa.nombre,
        "pais": playa.pais
    }

    # Persistir cambios en archivo JSON
    guardar_playa(PLAYAS)

    return {"mensaje": f"Playa {playa.nombre} añadida correctamente"}


# Lista de seguridad: IDs que no se permite borrar
PLAYAS_PROTEGIDAS = [
    "lanzada", "patos", "pantin", "razo", "doninos", "mundaka",
    "zarautz", "somo", "rodiles", "quemao", "maresias", "joaquina",
    "arpoador", "cacimba", "guarda", "saquarema", "itacare",
    "campeche", "itamambuca", "pipa",
    "nazare", "peniche", "ericeira", "carcavelos", "sagres",
    "arrifana", "espinho", "figueira", "viana", "matosinhos"
]


@app.delete("/playas/delete/{playa_id}")
def eliminar_playa(playa_id: str):
    """
    Eliminar una playa creada por el usuario.
    Bloquear intento si es una playa protegida (original del sistema).
    """
    playa_id = playa_id.lower().strip()

    if playa_id in PLAYAS_PROTEGIDAS:
        raise HTTPException(
            status_code=403,
            detail="No se pueden eliminar las playas originales del sistema."
        )

    if playa_id not in PLAYAS:
        raise HTTPException(status_code=404, detail="La playa no existe.")

    # Borrar de memoria y actualizar archivo
    del PLAYAS[playa_id]
    guardar_playa(PLAYAS)

    return {"mensaje": f"La playa con ID '{playa_id}' ha sido eliminada correctamente."}

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

# Diccionario con coordenadas de playas famosas
PLAYAS = {
    "pantin": {"lat": 43.63, "long": -8.11, "nombre": "Pantín, Galicia"},
    "joaquina": {"lat": -27.63, "long": -48.45, "nombre": "Praia da Joaquina, Brasil"},
    "arpoador": {"lat": -22.99, "long": -43.19, "nombre": "Arpoador, Rio de Janeiro"}
}


@app.get("/")
def read_root():
    html_content = """
    <html>
        <head>
            <title>Surf API 🌊</title>
        </head>
        <body>
            <h1>¡Bienvenido a la Surf API! 🌊🏄</h1>
            <form action="" method="post">
                <label for="playas">Elige tu pico favorito:</label>
                <select id="playas" name="playas">
                    <option value="" disabled selected>-- Selecciona una playa --</option>
                    <option value="playa1">Playa 1</option>
                    <option value="playa2">Playa 2</option>
                    <option value="playa3">Playa 3</option>
                </select>
                <br><br>
                <input type="submit" value="Enviar">
            </form>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/surf/{playa}")
def get_surf_forecast(playa: str):
    # Validar si la playa existe en nuestro diccionario
    playa_id = playa.lower()
    if playa_id not in PLAYAS:
        raise HTTPException(status_code=404, detail="Playa no encontrada")

    coords = PLAYAS[playa_id]

    # LLAMADA AL EXPERTO EN AGUA (Marine API)
    url_olas = (
        f"https://marine-api.open-meteo.com/v1/marine?"
        f"latitude={coords['lat']}&longitude={coords['long']}"
        f"&current=wave_height,wave_direction,wave_period"
        f"&timezone=auto"
    )

    # LLAMADA AL EXPERTO EN AIRE (Forecast API)
    url_viento = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={coords['lat']}&longitude={coords['long']}"
        f"&current=wind_speed_10m,wind_direction_10m"
        f"&timezone=auto"
    )

    # PETICIONES
    response_olas = requests.get(url_olas).json()
    response_viento = requests.get(url_viento).json()

    # DATOS LIMPIOS
    # Si la playa está muy en la orilla, las olas pueden dar null.
    # Usamos .get() para evitar errores si algo viene vacío.
    datos_olas = response_olas.get("current", {})
    datos_viento = response_viento.get("current", {})

    return {
        "playa": coords["nombre"],
        "latitud": coords["lat"],
        "longitud": coords["long"],
        "prevision_actual": {
            "olas": {
                "altura_metros": datos_olas.get("wave_height"),
                "direccion_grados": datos_olas.get("wave_direction"),
                "periodo_segundos": datos_olas.get("wave_period")
            },
            "viento": {
                "velocidad_kmh": datos_viento.get("wind_speed_10m"),
                "direccion_grados": datos_viento.get("wind_direction_10m")
            },
            "momento_lectura": datos_olas.get("time")
        }
    }

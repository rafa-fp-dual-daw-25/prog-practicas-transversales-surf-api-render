from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from utils import cargar_playas, guardar_playa, generar_selector_html, transformar_grados_a_direccion
import requests

app = FastAPI()

# Diccionario con coordenadas de playas famosas
PLAYAS = cargar_playas()


@app.get("/")
def read_root():
    opciones_dinamicas = generar_selector_html(PLAYAS)

    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; text-align: center; background: #f0f8ff; padding: 20px; }}
                
                h1 {{ color: #333; margin-bottom: 30px; }}
                
                select, button {{ padding: 12px; font-size: 16px; border-radius: 8px; border: 1px solid #ccc; margin: 5px; }}
                button {{ background: #007bff; color: white; cursor: pointer; border: none; font-weight: bold; transition: background 0.3s; }}
                button:hover {{ background: #0056b3; }}

                #resultado {{ 
                    opacity: 0; 
                    transition: opacity 0.5s ease; 
                    margin: 20px auto; 
                    max-width: 350px; /* Un poco más estrecho para parecer una tarjeta */
                    background: white; 
                    padding: 25px; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                    text-align: left; /* Importante: reseteamos la alineación general */
                }}

                #resultado h3 {{
                    text-align: center; /* El título de la playa sí lo queremos centrado */
                    color: #007bff;
                    margin-top: 0;
                    border-bottom: 2px solid #f0f8ff;
                    padding-bottom: 15px;
                }}

                .dato-fila {{
                    display: grid;
                    /* Reservamos 90px para el nombre del dato y el resto para el valor */
                    grid-template-columns: 90px 1fr; 
                    gap: 10px;
                    margin-bottom: 8px;
                    align-items: center;
                }}
                
                .etiqueta {{
                    text-align: right;
                    color: #555;
                    font-weight: bold;
                }}
                
                .valor {{
                    text-align: left;
                    color: #333;
                }}
                #contenedor-registro {{
                    margin-top: 40px;
                    padding: 20px;
                    background: #fff;
                    border-radius: 15px;
                    max-width: 500px;
                    margin-left: auto;
                    margin-right: auto;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                }}
                
                .formulario {{
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }}
                
                #contenedor-registro input, #contenedor-registro select {{
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                
                hr {{
                    border: 0;
                    height: 1px;
                    background: #eee;
                    margin: 40px 0;
                }}
            </style>
            <title>Surf API 🌊</title>
        </head>
        <body>
            <h1>¡Bienvenido a la Surf API! 🏄</h1>
            <h2>Consulta tú pico favorito 🌊</h2>
            <select id="selectorPlaya">
                {opciones_dinamicas}
            </select>
            <button type="button" onclick="consultar()">Consultar</button>
            <div id="resultado"></div>
            <hr>
            <div id="contenedor-registro">
                <h2>Registrar nueva playa 🏖️</h2>
                <div class="formulario">
                    <input type="text" id="new-id" placeholder="ID (ej: baldaio)">
                    <input type="text" id="new-nombre" placeholder="Nombre (ej: Playa de Baldaio)">
                    <input type="number" step="any" id="new-lat" placeholder="Latitud">
                    <input type="number" step="any" id="new-long" placeholder="Longitud">
                    <br>
                    <input id="Brasil" name="pais" type="radio">
                    <label for="Brasil">Brasil</label>
                    <input id="España" name="pais" type="radio">
                    <label for="España">España</label>
                    <br>
                    <button type="button" onclick="registrarPlaya()">Guardar Playa</button>
                </div>
                <p id="mensaje-registro"></p>
            </div>
            
            <script>
                async function consultar() {{
                    const playa = document.getElementById('selectorPlaya').value;
                    const response = await fetch('/surf/' + playa);
                    const data = await response.json();
                    
                    const divResultado = document.getElementById('resultado');
                    
                    divResultado.innerHTML = `
                        <h3>${{data.playa}}</h3>
                        <div class="dato-fila">
                            <span class="etiqueta">Olas:</span>
                            <span class="valor">${{data.prevision_actual.olas.altura_metros}} m</span>
                        </div>
                        <div class="dato-fila">
                            <span class="etiqueta">Periodo:</span>
                            <span class="valor">${{data.prevision_actual.olas.periodo_segundos}} s</span>
                        </div>
                        <div class="dato-fila">
                            <span class="etiqueta">Dirección:</span>
                            <span class="valor">${{data.prevision_actual.olas.direccion_texto}} (${{data.prevision_actual.olas.direccion_grados}}º)</span>
                        </div>
                        <div class="dato-fila">
                            <span class="etiqueta">Viento:</span>
                            <span class="valor">${{data.prevision_actual.viento.velocidad_kmh}} km/h (${{data.prevision_actual.viento.direccion_texto}})</span>
                        </div>
                    `;
                    
                    divResultado.style.opacity = '1';
                }}
                
                async function registrarPlaya() {{
                    // 1. Capturamos los datos del formulario
                    const nuevaPlaya = {{
                        id: document.getElementById('new-id').value,
                        nombre: document.getElementById('new-nombre').value,
                        lat: parseFloat(document.getElementById('new-lat').value),
                        long: parseFloat(document.getElementById('new-long').value),
                        pais: document.getElementById('new-pais').value
                    }};

                    const response = await fetch('/playas/add', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json'
                        }},
                        body: JSON.stringify(nuevaPlaya)
                    }});

                    if (response.ok) {{
                        alert("¡Playa guardada con éxito!");
                        // Recargamos la página para que la nueva playa aparezca en el select
                        location.reload(); 
                    }} else {{
                        const errorData = await response.json();
                        alert("Error al guardar: " + errorData.detail);
                    }}
                }}
                
                    const resultado = await response.json();
                    const mensaje = document.getElementById('mensaje-registro');
                
                    if (response.ok) {{
                        mensaje.style.color = "green";
                        mensaje.innerText = resultado.mensaje + " (Refresca para verla en la lista)";
                        // Limpiamos el formulario
                        document.querySelectorAll('#contenedor-registro input').forEach(i => i.value = '');
                    }} else {{
                        mensaje.style.color = "red";
                        mensaje.innerText = "Error: " + resultado.detail;
                    }}
                }}
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/surf/{playa}")
def get_surf_forecast(playa: str):
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

    dir_olas_txt = transformar_grados_a_direccion(datos_olas.get("wave_direction"))
    dir_viento_txt = transformar_grados_a_direccion(datos_viento.get("wind_direction_10m"))

    return {
        "playa": coords["nombre"],
        "latitud": coords["lat"],
        "longitud": coords["long"],
        "prevision_actual": {
            "olas": {
                "altura_metros": datos_olas.get("wave_height"),
                "direccion_grados": datos_olas.get("wave_direction"),
                "direccion_texto": dir_olas_txt,  # Enviamos el texto (N, S, E...)
                "periodo_segundos": datos_olas.get("wave_period")
            },
            "viento": {
                "velocidad_kmh": datos_viento.get("wind_speed_10m"),
                "direccion_grados": datos_viento.get("wind_direction_10m"),
                "direccion_texto": dir_viento_txt  # Enviamos el texto
            },
            "momento_lectura": datos_olas.get("time")
        }
    }

async function consultar() {
    // Obtener el ID seleccionado por el usuario
    const playa = document.getElementById('selectorPlaya').value;

    // Petición GET al backend para obtener datos del clima
    const response = await fetch('/surf/' + playa);
    const data = await response.json();

    const divResultado = document.getElementById('resultado');

    // Inyectar HTML dinámico con Template Literals (comillas invertidas)
    // Clases CSS (.dato-fila) para alinear con Grid
    divResultado.innerHTML = `
        <h3>${data.playa}</h3>
        <div class="dato-fila">
            <span class="etiqueta">Olas:</span>
            <span class="valor">${data.prevision_actual.olas.altura_metros} m</span>
        </div>
        <div class="dato-fila">
            <span class="etiqueta">Periodo:</span>
            <span class="valor">${data.prevision_actual.olas.periodo_segundos} s</span>
        </div>
        <div class="dato-fila">
            <span class="etiqueta">Dirección:</span>
            <span class="valor">${data.prevision_actual.olas.direccion_texto} (${data.prevision_actual.olas.direccion_grados}º)</span>
        </div>
        <div class="dato-fila">
            <span class="etiqueta">Viento:</span>
            <span class="valor">${data.prevision_actual.viento.velocidad_kmh} km/h (${data.prevision_actual.viento.direccion_texto})</span>
        </div>
    `;

    // Hacer visible la tarjeta con una transición suave
    divResultado.style.opacity = '1';
}

async function registrarPlaya() {
    // Detectar qué radio button está marcado (España o Brasil)
    // .value obtiene directamente el valor definido en el HTML
    const paisSeleccionado = document.querySelector('input[name="pais"]:checked');

    if (!paisSeleccionado) {
        alert("Por favor, selecciona un país (España o Brasil)");
        return;
    }

    // Construir objeto JSON con datos del formulario
    const nuevaPlaya = {
        id: document.getElementById('new-id').value,
        nombre: document.getElementById('new-nombre').value,
        lat: parseFloat(document.getElementById('new-lat').value),
        long: parseFloat(document.getElementById('new-long').value),
        pais: paisSeleccionado.value
    };

    // Validación básica antes de enviar
    if (!nuevaPlaya.id || !nuevaPlaya.nombre || isNaN(nuevaPlaya.lat)) {
        alert("Todos los campos son obligatorios");
        return;
    }

    // Petición POST para guardar datos
    const response = await fetch('/playas/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(nuevaPlaya)
    });

    if (response.ok) {
        alert("¡Playa guardada con éxito!");
        // Recargar página para actualizar la lista del selector
        location.reload();
    } else {
        const errorData = await response.json();
        alert("Error al guardar: " + errorData.detail);
    }
}

async function eliminarPlaya() {
    const playaId = document.getElementById('selectorPlaya').value;

    // Confirmación nativa del navegador para evitar borrados accidentales
    if (!confirm(`¿Estás seguro de que quieres eliminar la playa "${playaId}"?`)) {
        return;
    }

    // Petición DELETE al endpoint específico
    const response = await fetch(`/playas/delete/${playaId}`, {
        method: 'DELETE'
    });

    if (response.ok) {
        alert("Playa eliminada con éxito.");
        location.reload();
    } else {
        const errorData = await response.json();
        // Mostrar error si el usuario intenta borrar una playa protegida
        alert("Error: " + errorData.detail);
    }
}
import json
import os

# ============================
# Rutas
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS_JSON = os.path.join(BASE_DIR, "cirugías.json")

# ============================
# Función para obtener cirugías organizadas por fecha
# ============================
def obtener_cirugias_programadas():
    """
    Devuelve un diccionario de cirugías organizadas por fecha:
    {
        "2026-01-22": [
            {"nombre": "Juan", "sesion": "...", "quirofano": "...", "recursos": {...}},
            ...
        ],
        ...
    }
    Solo devuelve fechas que tengan al menos una cirugía programada.
    """
    if not os.path.exists(RUTA_CIRUGIAS_JSON):
        return {}

    with open(RUTA_CIRUGIAS_JSON, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    cirugias_por_fecha = {}

    for q_id, q_data in quirofanos.items():
        for fecha, cirugias_dia in q_data.get("cirugias", {}).items():
            if not cirugias_dia:
                continue
            if fecha not in cirugias_por_fecha:
                cirugias_por_fecha[fecha] = []
            for c in cirugias_dia:
                cirugias_por_fecha[fecha].append({
                    "nombre": c.get("nombre"),
                    "sesion": c.get("sesion"),
                    "quirofano": q_id,
                    "recursos": c.get("recursos", {})
                })

    # Ordenar las fechas
    cirugias_por_fecha = dict(sorted(cirugias_por_fecha.items()))

    return cirugias_por_fecha
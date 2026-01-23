import json
import os

# Ruta a cirugías.json
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS_JSON = os.path.join(BASE_DIR, "Pages/cirugías.json")

def obtener_cirugias_programadas():
    """
    Devuelve una lista plana de todas las cirugías programadas.
    Cada elemento es un diccionario con:
    nombre, fecha, sesion, quirófano y recursos
    """

    if not os.path.exists(RUTA_CIRUGIAS_JSON):
        return []

    with open(RUTA_CIRUGIAS_JSON, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    cirugias = []

    for q_id, q_data in quirofanos.items():
        for fecha, cirugias_dia in q_data.get("cirugias", {}).items():
            for c in cirugias_dia:
                cirugias.append({
                    "nombre": c.get("nombre"),
                    "fecha": fecha,
                    "sesion": c.get("sesion"),
                    "quirofano": q_id,
                    "recursos": c.get("recursos", {})
                })

    return cirugias

def obtener_cirugias_por_fecha():
    """
    Devuelve un diccionario agrupado por fecha.
    Cada clave es una fecha y el valor es la lista de cirugías de ese día.
    Útil para crear selectboxes por fecha en delete_surgery.py
    """

    cirugias = obtener_cirugias_programadas()
    cirugias_por_fecha = {}

    for c in cirugias:
        fecha = c["fecha"]
        if fecha not in cirugias_por_fecha:
            cirugias_por_fecha[fecha] = []
        cirugias_por_fecha[fecha].append(c)

    return cirugias_por_fecha
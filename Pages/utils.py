import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS_JSON = os.path.join(BASE_DIR, "cirugías.json")


def obtener_cirugias_programadas():
    """
    Devuelve una lista plana de todas las cirugías programadas.
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
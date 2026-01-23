import json
import os

# Ruta al JSON de cirugías (nivel superior de Pages)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS_JSON = os.path.join(BASE_DIR, "Pages", "cirugías.json")


def obtener_cirugias_programadas():
   
    if not os.path.exists(RUTA_CIRUGIAS_JSON):
        return []

    with open(RUTA_CIRUGIAS_JSON, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    cirugias = []

    for q_id, q_data in quirofanos.items():
        for fecha, lista_cirugias in q_data.get("cirugias", {}).items():
            for c in lista_cirugias:
                cirugias.append({
                    "nombre": c.get("nombre"),
                    "fecha": fecha,
                    "sesion": c.get("sesion"),
                    "quirofano": q_id,
                    "recursos": c.get("recursos", {})
                })
    return cirugias


def obtener_cirugias_por_fecha():
   
    cirugias = obtener_cirugias_programadas()
    por_fecha = {}

    for c in cirugias:
        fecha = c["fecha"]
        if fecha not in por_fecha:
            por_fecha[fecha] = []
        por_fecha[fecha].append(c)

    # Ordenar las fechas de forma ascendente
    por_fecha_ordenado = dict(sorted(por_fecha.items()))
    return por_fecha_ordenado
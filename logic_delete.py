import streamlit as st
import json
from datetime import datetime, timedelta
import os
from resources_validation import devolver_recursos, lunes_de_la_semana
from visual import ocultar_sidebar
ocultar_sidebar()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
RUTA_CIRUGIAS = os.path.join(BASE_DIR, "Pages", "cirugías.json")
RUTA_RECURSOS = "APP/recursos.json"


def obtener_lunes(fecha_str):
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return (fecha - timedelta(days=fecha.weekday())).isoformat()

def eliminar_cirugia_por_nombre(nombre_cirugia, fecha_cirugia):

    with open(RUTA_CIRUGIAS, "r", encoding="utf-8") as f:
        cirugias = json.load(f)

    encontrada = False

    for q_id, q_data in cirugias.items():
        cirugias_dia = q_data.get("cirugias", {}).get(fecha_cirugia, [])

        for i, c in enumerate(cirugias_dia):
            if c.get("nombre") == nombre_cirugia:

                encontrada = True
                recursos = c.get("recursos", {})

                # Convertir fecha a objeto date
                fecha_obj = datetime.strptime(fecha_cirugia, "%Y-%m-%d").date()

                # Devolver recursos correctamente
                devolver_recursos(fecha_obj, recursos)

                # ELIMINAR LA CIRUGÍA
                del cirugias_dia[i]

                # Si ese día queda vacío, borrar la fecha
                if not cirugias_dia:
                    del cirugias[q_id]["cirugias"][fecha_cirugia]

                break

        if encontrada:
            break

    if not encontrada:
        return False, "LA CIRUGÍA NO EXISTE PARA ESA FECHA"

    # Guardar cambios en el JSON
    with open(RUTA_CIRUGIAS, "w", encoding="utf-8") as f:
        json.dump(cirugias, f, ensure_ascii=False, indent=4)

    return True, "CIRUGÍA ELIMINADA CORRECTAMENTE"
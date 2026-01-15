import json
import os
import streamlit as st
from datetime import date
from resources_validation import cargar_recursos_operativos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS_JSON = os.path.join(BASE_DIR, "cirugías.json")
RUTA_RECURSOS_JSON = os.path.join(BASE_DIR, "APP", "recursos.json")


def eliminar_cirugia(q_id: str, fecha: date, sesion: str):
    fecha_str = str(fecha)

    # ============================
    # Cargar cirugías
    # ============================
    if not os.path.exists(RUTA_CIRUGIAS_JSON):
        return False, "No existe el archivo de cirugías"

    with open(RUTA_CIRUGIAS_JSON, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    cirugias_dia = quirofanos[q_id]["cirugias"].get(fecha_str, [])

    # Buscar la cirugía
    cirugia = None
    for c in cirugias_dia:
        if c["sesion"] == sesion:
            cirugia = c
            break

    if cirugia is None:
        return False, "No se encontró la cirugía"

    recursos_a_revertir = cirugia.get("recursos", {})

    # ============================
    # Revertir recursos gastables
    # ============================
    recursos_json = cargar_recursos_operativos()

    for recurso, cantidad in recursos_a_revertir.items():
        # Session state
        if recurso in st.session_state.recursos_disponibles:
            st.session_state.recursos_disponibles[recurso] += cantidad

        # recursos.json
        if recurso in recursos_json:
            recursos_json[recurso]["stock_semanal"] += cantidad

            if fecha_str in recursos_json[recurso]["consumo_semanal"]:
                recursos_json[recurso]["consumo_semanal"][fecha_str] -= cantidad
                if recursos_json[recurso]["consumo_semanal"][fecha_str] <= 0:
                    del recursos_json[recurso]["consumo_semanal"][fecha_str]

    # Guardar recursos.json
    with open(RUTA_RECURSOS_JSON, "w", encoding="utf-8") as f:
        json.dump({"recursos_operativos": recursos_json}, f, ensure_ascii=False, indent=4)

    # ============================
    # Eliminar cirugía del quirófano
    # ============================
    quirofanos[q_id]["cirugias"][fecha_str].remove(cirugia)

    if not quirofanos[q_id]["cirugias"][fecha_str]:
        del quirofanos[q_id]["cirugias"][fecha_str]

    # Guardar cirugías.json
    with open(RUTA_CIRUGIAS_JSON, "w", encoding="utf-8") as f:
        json.dump(quirofanos, f, ensure_ascii=False, indent=4)

    return True, "Cirugía eliminada y recursos restaurados"
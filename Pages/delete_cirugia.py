import json
import os
import streamlit as st
from datetime import date
from resources_validation import cargar_recursos_operativos

# ============================
# Rutas
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS_JSON = os.path.join(BASE_DIR, "cirugías.json")
RUTA_RECURSOS_JSON = os.path.join(BASE_DIR, "APP", "recursos.json")


def eliminar_cirugia_por_nombre(nombre_cirugia: str):
    """
    Elimina una cirugía identificada por su nombre (paciente).
    Libera quirófano, sesión y TODOS los recursos asociados.
    """

    # ============================
    # Validaciones iniciales
    # ============================
    if not os.path.exists(RUTA_CIRUGIAS_JSON):
        return False, "No existe el archivo de cirugías"

    if "recursos_disponibles" not in st.session_state:
        return False, "Recursos no inicializados en session_state"

    # ============================
    # Cargar cirugías
    # ============================
    with open(RUTA_CIRUGIAS_JSON, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    cirugia_encontrada = None
    q_id_encontrado = None
    fecha_encontrada = None

    # ============================
    # Buscar cirugía por nombre
    # ============================
    for q_id, q_data in quirofanos.items():
        for fecha_str, cirugias_dia in q_data.get("cirugias", {}).items():
            for c in cirugias_dia:
                if c.get("nombre") == nombre_cirugia:
                    cirugia_encontrada = c
                    q_id_encontrado = q_id
                    fecha_encontrada = fecha_str
                    break
            if cirugia_encontrada:
                break
        if cirugia_encontrada:
            break

    if cirugia_encontrada is None:
        return False, "No se encontró una cirugía con ese nombre"

    # ============================
    # Recuperar recursos usados
    # ============================
    recursos_a_revertir = cirugia_encontrada.get("recursos", {})

    recursos_json = cargar_recursos_operativos()

    # ============================
    # Revertir recursos
    # ============================
    for recurso, cantidad in recursos_a_revertir.items():

        # Session state
        if recurso in st.session_state.recursos_disponibles:
            st.session_state.recursos_disponibles[recurso] += cantidad

        # recursos.json
        if recurso in recursos_json:
            recursos_json[recurso]["stock_semanal"] += cantidad

            if fecha_encontrada in recursos_json[recurso]["consumo_semanal"]:
                recursos_json[recurso]["consumo_semanal"][fecha_encontrada] -= cantidad

                if recursos_json[recurso]["consumo_semanal"][fecha_encontrada] <= 0:
                    del recursos_json[recurso]["consumo_semanal"][fecha_encontrada]

    # ============================
    # Guardar recursos.json
    # ============================
    with open(RUTA_RECURSOS_JSON, "w", encoding="utf-8") as f:
        json.dump(
            {"recursos_operativos": recursos_json},
            f,
            ensure_ascii=False,
            indent=4
        )

    # ============================
    # Eliminar cirugía del quirófano
    # ============================
    quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada].remove(cirugia_encontrada)

    # Limpiar fecha si quedó vacía
    if not quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada]:
        del quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada]

    # ============================
    # Guardar cirugías.json
    # ============================
    with open(RUTA_CIRUGIAS_JSON, "w", encoding="utf-8") as f:
        json.dump(quirofanos, f, ensure_ascii=False, indent=4)

    return True, "Cirugía eliminada correctamente"
import json
import os
import streamlit as st
from datetime import date
from resources_validation import cargar_recursos_operativos

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_CIRUGIAS = os.path.join(BASE_DIR, "cirugías.json")
RUTA_RECURSOS = os.path.join(BASE_DIR, "APP", "recursos.json")


def eliminar_cirugia_por_nombre(nombre_cirugia: str):
    if not os.path.exists(RUTA_CIRUGIAS):
        return False, "No existe el archivo de cirugías"

    with open(RUTA_CIRUGIAS, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    cirugia_encontrada = None
    q_id_encontrado = None
    fecha_encontrada = None

    # 1️⃣ Buscar cirugía por nombre
    for q_id, q_data in quirofanos.items():
        for fecha, cirugias in q_data["cirugias"].items():
            for c in cirugias:
                if c["nombre"].lower() == nombre_cirugia.lower():
                    cirugia_encontrada = c
                    q_id_encontrado = q_id
                    fecha_encontrada = fecha
                    break
            if cirugia_encontrada:
                break
        if cirugia_encontrada:
            break

    if not cirugia_encontrada:
        return False, "No se encontró una cirugía con ese nombre"

    recursos_a_liberar = cirugia_encontrada.get("recursos", {})

    # 2️⃣ Revertir recursos en session_state
    for recurso, cantidad in recursos_a_liberar.items():
        if recurso in st.session_state.recursos_disponibles:
            st.session_state.recursos_disponibles[recurso] += cantidad

    # 3️⃣ Revertir recursos en recursos.json
    recursos_json = cargar_recursos_operativos()

    for recurso, cantidad in recursos_a_liberar.items():
        if recurso in recursos_json:
            recursos_json[recurso]["stock_semanal"] += cantidad

            if fecha_encontrada in recursos_json[recurso]["consumo_semanal"]:
                recursos_json[recurso]["consumo_semanal"][fecha_encontrada] -= cantidad
                if recursos_json[recurso]["consumo_semanal"][fecha_encontrada] <= 0:
                    del recursos_json[recurso]["consumo_semanal"][fecha_encontrada]

    with open(RUTA_RECURSOS, "w", encoding="utf-8") as f:
        json.dump({"recursos_operativos": recursos_json}, f, indent=4, ensure_ascii=False)

    # 4️⃣ Eliminar cirugía del quirófano
    quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada].remove(cirugia_encontrada)

    if not quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada]:
        del quirofanos[q_id_encontrado]["cirugias"][fecha_encontrada]

    # 5️⃣ Guardar cirugías.json
    with open(RUTA_CIRUGIAS, "w", encoding="utf-8") as f:
        json.dump(quirofanos, f, indent=4, ensure_ascii=False)

    return True, "CIRUGIA ELIMINADA CORRECTAMENTE"
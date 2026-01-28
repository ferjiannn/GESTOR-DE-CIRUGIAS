import streamlit as st
import json
from datetime import datetime, timedelta
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
RUTA_CIRUGIAS = os.path.join(BASE_DIR, "Pages", "cirugías.json")
RUTA_RECURSOS = "APP/recursos.json"

def inicializar_recursos():
    return {
        "antibioticos": 15,
        "analgesicos": 12,
        "anestesicos": 12,
        "antiinflamatorios": 12,
        "anticoagulantes": 12,
        "antiemeticos": 12,
        "relajantes_musculares": 12,
        "soluciones_intravenosas": 12,
        "medicacion_soporte": 12,
        "campos_esteriles": 12,
        "panos_esteriles": 12,
        "sabanas_esteriles": 12,
        "suturas_grapas": 12,
        "contenedores_esteriles": 12,
        "sets_ortopedicos": 12,
        "sets_artroscopia": 12,
        "implantes_ortopedicos": 12
    }

def obtener_lunes(fecha_str):
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    return (fecha - timedelta(days=fecha.weekday())).isoformat()

def eliminar_cirugia_por_nombre(nombre_cirugia, fecha_cirugia):
    
    # Cargar cirugías
    with open(RUTA_CIRUGIAS, "r", encoding="utf-8") as f:
        cirugias = json.load(f)

    encontrada = False

    # Buscar la cirugía en todos los quirófanos
    for q_id, q_data in cirugias.items():
        cirugias_dia = q_data.get("cirugias", {}).get(fecha_cirugia, [])

        for i, c in enumerate(cirugias_dia):
            if c.get("nombre") == nombre_cirugia:
                encontrada = True
                recursos = c.get("recursos", {})

                # Cargar recursos operativos
                with open(RUTA_RECURSOS, "r", encoding="utf-8") as rf:
                    recursos_operativos = json.load(rf)["recursos_operativos"]

                lunes = obtener_lunes(fecha_cirugia)

                # Asegurar que la semana existe en session_state
                if "recursos_disponibles" in st.session_state:
                    if lunes not in st.session_state.recursos_disponibles:
                        st.session_state.recursos_disponibles[lunes] = inicializar_recursos()

                # Liberar recursos
                for recurso, cantidad in recursos.items():

                    # Liberar consumo semanal en recursos.json
                    consumo = recursos_operativos[recurso].get("consumo_semanal", {})
                    if lunes in consumo:
                        consumo[lunes] -= cantidad
                        if consumo[lunes] <= 0:
                            del consumo[lunes]

                    # Devolver stock semanal en recursos.json
                    recursos_operativos[recurso]["stock_semanal"] += cantidad

                    # Devolver stock a session_state
                    if "recursos_disponibles" in st.session_state:
                        st.session_state.recursos_disponibles[lunes][recurso] += cantidad

                # Guardar recursos actualizados
                with open(RUTA_RECURSOS, "w", encoding="utf-8") as wf:
                    json.dump(
                        {"recursos_operativos": recursos_operativos},
                        wf,
                        ensure_ascii=False,
                        indent=4
                    )

                # Eliminar la cirugía
                del cirugias_dia[i]

                # Si la lista del día queda vacía, limpiar
                if not cirugias_dia:
                    del cirugias[q_id]["cirugias"][fecha_cirugia]

                break

        if encontrada:
            break

    if not encontrada:
        return False, "LA CIRUGÍA NO EXISTE PARA ESA FECHA"

    # Guardar cambios en cirugías.json
    with open(RUTA_CIRUGIAS, "w", encoding="utf-8") as f:
        json.dump(cirugias, f, ensure_ascii=False, indent=4)

    return True, "CIRUGÍA ELIMINADA CORRECTAMENTE"
import json
import os
import streamlit as st
from datetime import date, timedelta


# Rutas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_RECURSOS_JSON = os.path.join(BASE_DIR, "APP", "recursos.json")

# Advertencia (2/3)
UMBRAL_ADVERTENCIA = 2 / 3


# Carga de recursos.json

def cargar_recursos_operativos(semana= None):
    if not os.path.exists(RUTA_RECURSOS_JSON):
        raise FileNotFoundError(f"No se encontró {RUTA_RECURSOS_JSON}")
    with open(RUTA_RECURSOS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    recursos = data.get("recursos_operativos", {})

    return {k: v["stock_semanal"] for k, v in recursos.items()}

# Inicializar recursos

def inicializar_recursos():
    recursos = cargar_recursos_operativos()
    return recursos.copy()


# Obtener lunes de la semana

def lunes_de_la_semana(fecha: date) -> date:
    return fecha - timedelta(days=fecha.weekday())

def validar_recursos(fecha_cirugia: date, recursos_solicitados=None):
   
    errores = []
    advertencias = []

    semana = lunes_de_la_semana(fecha_cirugia)
    stock_actual = st.session_state.recursos_disponibles.get(semana, {})

    recursos = recursos_solicitados or {}

    for recurso, cantidad in recursos.items():
        disponible = stock_actual.get(recurso, 0)

        # Bloqueo si no hay suficiente
        if cantidad > disponible:
            errores.append(f"No hay suficiente {recurso}. Disponible: {disponible}")
            continue

        # Advertencia por bajo stock
        if disponible > 0 and (disponible - cantidad) <= disponible * UMBRAL_ADVERTENCIA:
            advertencias.append(
                f"⚠️ Stock bajo para {recurso}. Disponible después: {disponible - cantidad}"
            )

    ok = len(errores) == 0
    return ok, errores, advertencias


def descontar_recursos(fecha_cirugia: date, recursos_solicitados=None):
    
    semana = lunes_de_la_semana(fecha_cirugia)
    if semana not in st.session_state.recursos_disponibles:
        st.session_state.recursos_disponibles[semana] = inicializar_recursos()
    stock_actual = st.session_state.recursos_disponibles[semana]

    recursos = recursos_solicitados or {}

    # Descontar solo en la semana actual
    for recurso, cantidad in recursos.items():
        if recurso in stock_actual:
            stock_actual[recurso] -= cantidad
            if stock_actual[recurso] < 0:
                stock_actual[recurso] = 0

    # Registrar consumo en JSON (solo histórico)
    with open(RUTA_RECURSOS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    recursos_json = data.get("recursos_operativos", {})

    for recurso, cantidad in recursos.items():
        if recurso in recursos_json:
            fecha_str = str(semana)

            if "consumo_semanal" not in recursos_json[recurso]:
                recursos_json[recurso]["consumo_semanal"] = {}

            recursos_json[recurso]["consumo_semanal"][fecha_str] = (
                recursos_json[recurso]["consumo_semanal"].get(fecha_str, 0) + cantidad
            )

# Guardar JSON completo
    with open(RUTA_RECURSOS_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
        # Guardar JSON
    with open(RUTA_RECURSOS_JSON, "w", encoding="utf-8") as f:
        json.dump({"recursos_operativos": recursos_json}, f, ensure_ascii=False, indent=4)


def devolver_recursos(fecha_cirugia: date, recursos_utilizados: dict):
    semana = lunes_de_la_semana(fecha_cirugia)

    # --- Blindaje de session_state ---

    # Asegurar que exista recursos_disponibles
    if "recursos_disponibles" not in st.session_state:
        st.session_state.recursos_disponibles = {}

    # Asegurar que exista stock_maximo
    if "stock_maximo" not in st.session_state:
        recursos_json = cargar_recursos_operativos()
        st.session_state.stock_maximo = {
            r: v["stock_semanal"] for r, v in recursos_json.items()
        }

    # Inicializar la semana si no existe
    if semana not in st.session_state.recursos_disponibles:
        st.session_state.recursos_disponibles[semana] = inicializar_recursos()

    stock_actual = st.session_state.recursos_disponibles[semana]
    stock_maximo = st.session_state.stock_maximo

    # --- Devolver recursos respetando el límite máximo ---
    for recurso, cantidad in recursos_utilizados.items():
        if recurso in stock_actual:
            stock_actual[recurso] += cantidad

            # No permitir que supere el stock máximo original
            if stock_actual[recurso] > stock_maximo.get(recurso, stock_actual[recurso]):
                stock_actual[recurso] = stock_maximo[recurso]

    # Guardar nuevamente en session_state
    st.session_state.recursos_disponibles[semana] = stock_actual


# Reset semanal si es lunes

def reset_semanal_si_corresponde(recursos_semana):
    lunes_actual = lunes_de_la_semana(date.today())
    if st.session_state.get("ultimo_reset") == lunes_actual:
        return recursos_semana  # ya se reseteó esta semana

    if date.today() == lunes_actual:
        st.session_state.ultimo_reset = lunes_actual
        return inicializar_recursos()

    return recursos_semana


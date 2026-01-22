import json
import os
import streamlit as st
from datetime import date, timedelta

# ============================
# Rutas
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_RECURSOS_JSON = os.path.join(BASE_DIR, "APP", "recursos.json")

# Umbral de advertencia (2/3)
UMBRAL_ADVERTENCIA = 2 / 3

# Receta clínica base: recursos mínimos por cirugía 
RECURSOS_POR_CIRUGIA = {
    "antibioticos": 2,
    "anestesicos": 1,
    "analgesicos": 1,
    "contenedores_esteriles": 1,
    "sets_ortopedicos": 1,
    "sets_artroscopia": 1,
    "implantes_ortopedicos": 1
}

# ============================
# Carga de recursos.json
# ============================
def cargar_recursos_operativos():
    """
    Carga los recursos operativos desde recursos.json
    """
    if not os.path.exists(RUTA_RECURSOS_JSON):
        raise FileNotFoundError(f"No se encontró {RUTA_RECURSOS_JSON}")

    with open(RUTA_RECURSOS_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("recursos_operativos", {})

# ============================
# Inicializar recursos
# ============================
def inicializar_recursos():
    """
    Devuelve un diccionario plano con los recursos disponibles actualmente
    { recurso: stock_semanal }
    """
    recursos = cargar_recursos_operativos()
    return {k: v["stock_semanal"] for k, v in recursos.items()}

# ============================
# Validar recursos
# ============================
def validar_recursos(fecha_cirugia: date, recursos_solicitados=None):
    """
    Valida si se puede realizar una cirugía en la semana de la fecha indicada.

    Retorna:
        ok (bool)
        errores (list[str])
        advertencias (list[str])
    """
    errores = []
    advertencias = []

    # Recursos a usar (por defecto receta clínica)
    recursos = recursos_solicitados or RECURSOS_POR_CIRUGIA

    # Traemos stock actual desde session_state
    stock_actual = st.session_state.recursos_disponibles

    for recurso, cantidad_necesaria in recursos.items():
        disponible = stock_actual.get(recurso, 0)

        # No alcanza el mínimo
        if disponible < cantidad_necesaria:
            errores.append(
                f"No hay suficiente {recurso}. Requerido: {cantidad_necesaria}, disponible: {disponible}"
            )
            continue

        # ⚠️ Advertencia por bajo stock
        if disponible - cantidad_necesaria <= disponible / 3:
            advertencias.append(
                f"⚠️ Stock bajo para {recurso}. Disponible después de esta cirugía: {disponible - cantidad_necesaria}"
            )

    ok = len(errores) == 0
    return ok, errores, advertencias

# ============================
# Descontar recursos
# ============================
def descontar_recursos(fecha_cirugia: date, recursos_solicitados=None):
    """
    Descuenta los recursos confirmados de session_state y actualiza recursos.json
    """
    if recursos_solicitados is None:
        recursos = RECURSOS_POR_CIRUGIA
        
    else:
        recursos = recursos_solicitados
    stock_actual = st.session_state.recursos_disponibles

    # Descontar en session_state
    for recurso, cantidad in recursos.items():
        if recurso in stock_actual:
            stock_actual[recurso] -= cantidad
            if stock_actual[recurso] < 0:
                stock_actual[recurso] = 0  # seguridad

    # Guardar cambios en recursos.json (consumo semanal)
    recursos_json = cargar_recursos_operativos()
    for recurso, cantidad in recursos.items():
        if recurso in recursos_json:
            # registrar consumo en fecha
            fecha_str = str(fecha_cirugia)
            recursos_json[recurso]["consumo_semanal"][fecha_str] = (
                recursos_json[recurso]["consumo_semanal"].get(fecha_str, 0) + cantidad
            )
            # actualizar stock_semanal
            recursos_json[recurso]["stock_semanal"] = stock_actual[recurso]

    # Guardar cambios
    with open(RUTA_RECURSOS_JSON, "w", encoding="utf-8") as f:
        json.dump({"recursos_operativos": recursos_json}, f, ensure_ascii=False, indent=4)

        # ============================
# Opcional: utilidad de lunes de la semana
# ============================
def lunes_de_la_semana(fecha: date) -> date:
    """Devuelve el lunes de la semana de una fecha"""
    return fecha - timedelta(days=fecha.weekday())

def reset_semanal_si_corresponde():
    hoy = date.today()
    lunes_actual = lunes_de_la_semana(hoy)

    # Evitar múltiples resets la misma semana
    if st.session_state.get("ultimo_reset") == lunes_actual:
        return

    recursos = cargar_recursos_operativos()

    for recurso, data in recursos.items():
        # Resetear stock al máximo semanal (suma de consumo + stock actual)
        consumo_total = sum(data["consumo_semanal"].values())
        data["stock_semanal"] += consumo_total
        data["consumo_semanal"] = {}

    # Guardar cambios
    with open(RUTA_RECURSOS_JSON, "w", encoding="utf-8") as f:
        json.dump({"recursos_operativos": recursos}, f, indent=4, ensure_ascii=False)

    # Actualizar session_state
    st.session_state.recursos_disponibles = {
        k: v["stock_semanal"] for k, v in recursos.items()
    }

    st.session_state.ultimo_reset = lunes_actual
import streamlit as st
import json
import os
from datetime import date, timedelta
from resources_validation import (cargar_recursos_operativos, validar_recursos, descontar_recursos, inicializar_recursos, reset_semanal_si_corresponde)
from utils import obtener_lunes_de_semana


if st.session_state.get("reset_surgery", False):
    st.session_state.pop("recursos_disponibles", None)
    st.session_state.pop("agenda", None)
    st.session_state.pop("quirófanos_disponibles", None)
    st.session_state.pop("sesiones_disponibles", None)
    st.session_state.reset_surgery = False

# ============================
# Inicialización de recursos
# ============================

if "recursos_disponibles" not in st.session_state:
   
    st.session_state.recursos_disponibles = inicializar_recursos()

# ============================
# Rutas y JSON de quirófanos
# ============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_JSON = os.path.join(BASE_DIR, "cirugías.json")

def guardar_en_json(quirofanos):
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(quirofanos, f, ensure_ascii=False, indent=4)

def inicializar_quirofanos():
    return {
        "Q0-1": {"estado": "disponible", "cirugias": {}},
        "Q0-2": {"estado": "disponible", "cirugias": {}}
    }

def cargar_desde_json():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data:
                return data
    return inicializar_quirofanos()

# ============================
# Constantes y sesiones
# ============================
MAX_CIRUGIAS_POR_DIA = 2
SESIONES = ["Mañana (8:00)", "Tarde (14:00)"]

# ============================
# Límites máximos por cirugía
# ============================
LIMITES_RECURSOS = {
    "antibioticos": 3,
    "analgesicos": 5,
    "anestesicos": 1,
    "antiinflamatorios": 2,
    "anticoagulantes": 1,
    "antiemeticos": 1,
    "relajantes_musculares": 1,
    "soluciones_intravenosas": 2,
    "medicacion_soporte": 2,
    "campos_esteriles": 3,
    "panos_esteriles": 3,
    "sabanas_esteriles": 2,
    "suturas_grapas": 4,
    "contenedores_esteriles": 1,
    "sets_ortopedicos": 1,
    "sets_artroscopia": 1,
    "implantes_ortopedicos": 2
}

# ============================
# Funciones auxiliares
# ============================
def obtener_quirofanos_disponibles(quirofanos, fecha):
    disponibles = []
    for q_id, q_data in quirofanos.items():
        cirugias_dia = q_data["cirugias"].get(str(fecha), [])
        if not isinstance(cirugias_dia, list):
            cirugias_dia = []
        if len(cirugias_dia) < MAX_CIRUGIAS_POR_DIA:
            disponibles.append(q_id)
    return disponibles

def validar_sesion(quirofano, fecha, sesion):
    cirugias_dia = quirofano["cirugias"].get(str(fecha), [])
    for c in cirugias_dia:
        if c["sesion"] == sesion:
            return False
    return True

def registrar_cirugia(quirofanos, q_id, fecha, sesion, recursos_solicitados, nombre):
    fecha_str = str(fecha)
    if fecha_str not in quirofanos[q_id]["cirugias"]:
        quirofanos[q_id]["cirugias"][fecha_str] = []
    cirugia = {
        "nombre": nombre,
        "sesion": sesion,
        "recursos": recursos_solicitados
    }
    quirofanos[q_id]["cirugias"][fecha_str].append(cirugia)

def sugerir_alternativa(quirofanos, fecha, q_original, sesion_original):
    fecha_str = str(fecha)

    # Otra sesión en el mismo quirófano
    if q_original is not None and q_original in quirofanos:
        cirugias_mismo_q = quirofanos[q_original].get("cirugias", {}).get(fecha_str, [])
        sesiones_ocupadas = [c["sesion"] for c in cirugias_mismo_q]

        for s in SESIONES:
            if s != sesion_original and s not in sesiones_ocupadas:
                return fecha, q_original, s

    # Otro quirófano en la misma fecha
    for q_id, q_data in quirofanos.items():
        if q_id == q_original:
            continue

        cirugias_dia = q_data.get("cirugias", {}).get(fecha_str, [])
        if len(cirugias_dia) >= MAX_CIRUGIAS_POR_DIA:
            continue

        sesiones_ocupadas = [c["sesion"] for c in cirugias_dia]
        for s in SESIONES:
            if s not in sesiones_ocupadas:
                return fecha, q_id, s

    # Otra fecha (hasta 30 días)
    for i in range(1, 31):
        nueva_fecha = fecha + timedelta(days=i)
        nueva_fecha_str = str(nueva_fecha)

        for q_id, q_data in quirofanos.items():
            cirugias_dia = q_data.get("cirugias", {}).get(nueva_fecha_str, [])
            if len(cirugias_dia) >= MAX_CIRUGIAS_POR_DIA:
                continue

            sesiones_ocupadas = [c["sesion"] for c in cirugias_dia]
            for s in SESIONES:
                if s not in sesiones_ocupadas:
                    return nueva_fecha, q_id, s

    return None, None, None

# ============================
# Estado de quirófanos
# ============================
if "quirofanos" not in st.session_state:
    st.session_state.quirofanos = cargar_desde_json()


if "recargar_estado" not in st.session_state:
    st.session_state.recargar_estado = False

if st.session_state.recargar_estado:
    st.session_state.quirofanos = cargar_desde_json()
    st.session_state.recargar_estado = False


st.markdown("# PLANIFICACIÓN DE CIRUGÍAS")

# Selección de fecha
hoy = date.today() + timedelta(days = 1)
fecha = st.date_input(
    "SELECCIONA LA FECHA",
    min_value=hoy,
    max_value=hoy + timedelta(days=30)
)

semana = fecha - timedelta(days=fecha.weekday())


if semana not in st.session_state.recursos_disponibles:
    st.session_state.recursos_disponibles[semana] = inicializar_recursos()
else:
    # Resetea stock completo si es lunes
    st.session_state.recursos_disponibles[semana] = reset_semanal_si_corresponde(st.session_state.recursos_disponibles[semana])

quirofanos_disponibles = obtener_quirofanos_disponibles(st.session_state.quirofanos, fecha)


# Selección de sesión
sesion = st.radio("SELECCIONA LA SESIÓN", SESIONES)

# ============================
# Recursos solicitados (nombres consistentes con data.json y recursos.json)
# ============================
st.subheader("RECURSOS PARA LA CIRUGÍA")

# Cargar recursos disponibles para mostrar
if semana not in st.session_state.recursos_disponibles:
    st.session_state.recursos_disponibles[semana] = inicializar_recursos()

recursos_actuales = st.session_state.recursos_disponibles[semana]

# Diccionario donde guardaremos lo que el usuario solicita
recursos_solicitados = {}

lunes_semana_cirugia = obtener_lunes_de_semana(fecha)

# Crear un input por cada recurso disponible
recursos_solicitados = {}

# Inicializa los valores en session_state si no existen
for recurso in recursos_actuales.keys():
    if f"input_{recurso}" not in st.session_state:
        st.session_state[f"input_{recurso}"] = 0

# Crear un input por cada recurso disponible usando session_state
recursos_solicitados = {}

# Crear los number_input sin del
for recurso, stock in recursos_actuales.items():
    max_clinico = LIMITES_RECURSOS.get(recurso, stock)

    # Si queremos resetear el input, usamos 0 temporalmente
    valor_inicial = 0 if st.session_state.get(f"reset_{recurso}", False) else st.session_state.get(f"input_{recurso}", 0)

    cantidad = st.number_input(
        label=f"{recurso} (stock disponible: {stock}, max por cirugia: {max_clinico})",
        min_value=0,
        max_value=min(stock, max_clinico),
        value=valor_inicial,
        step=1,
        key=f"input_{recurso}"
    )

    # Guardar en session_state normalmente
    st.session_state[f"input_{recurso}"] = cantidad

    if cantidad > 0:
        recursos_solicitados[recurso] = cantidad

    # Si estaba marcado para reset, desmarcamos
    if st.session_state.get(f"reset_{recurso}", False):
        st.session_state[f"reset_{recurso}"] = False

# lunes de la semana de la cirugía
    
    dias_desde_lunes = fecha.weekday()
    lunes_semana_cirugia = fecha - timedelta(days=dias_desde_lunes)

# ============================
# Validación temprana de recursos
# ============================

ok, errores, advertencias = validar_recursos(lunes_semana_cirugia, recursos_solicitados)

if not ok:
    st.error("No se puede programar la cirugía por falta de recursos:")
    for e in errores:
        st.error(f"❌ {e}")
    st.stop()

q_data = None

if not quirofanos_disponibles:
    st.error("No hay quirófanos disponibles para esta fecha.")

    sugerencia = sugerir_alternativa(
        st.session_state.quirofanos,
        fecha,
        None,
        None
    )

    if sugerencia:
        f, q, s = sugerencia
        st.warning(
            f"Sugerencia:\n"
            f"📅 Fecha: {f}\n"
            f"🏥 Quirófano: {q}\n"
            f"⏰ Sesión: {s}"
        )
    else:
        st.error("No hay alternativas disponibles en los próximos 30 días.")

    st.stop()
else:
    q_seleccionado = st.selectbox("Selecciona el quirófano", quirofanos_disponibles)
    q_data = st.session_state.quirofanos[q_seleccionado]
    if validar_sesion(q_data, fecha, sesion):
        st.success(f"Quirófano {q_seleccionado} disponible para la sesión {sesion}.")

nombre_cirugia = st.text_input("NOMBRE DEL PACIENTE (especificar quirófano)", max_chars=50)

# ============================
# Bloque de AGENDAR cirugía
# ============================
# ============================
# Bloque de AGENDAR cirugía
# ============================
if st.button("AGENDAR"):

    if q_data is None:
        st.error("NO HAY QUIRÓFANO VÁLIDO SELECCIONADO")
        st.stop()

    if not nombre_cirugia.strip():
        st.error("DEBE INTRODUCIR EL NOMBRE DEL PACIENTE")
        st.stop()

    # Validar sesión
    if not validar_sesion(q_data, fecha, sesion):
        st.error("NO DISPONIBLE")

        sugerencia = sugerir_alternativa(
            st.session_state.quirofanos,
            fecha,
            q_seleccionado,
            sesion
        )

        if sugerencia:
            f, q, s = sugerencia
            st.warning(
                f"Sugerencia:\n"
                f"📅 Fecha: {f}\n"
                f"🏥 Quirófano: {q}\n"
                f"⏰ Sesión: {s}"
            )
        else:
            st.error("No hay alternativas disponibles para esta fecha.")

        st.stop()

    # Validar recursos 
    lunes_semana_cirugia = obtener_lunes_de_semana(fecha)
    
    ok, errores, advertencias = validar_recursos(lunes_semana_cirugia, recursos_solicitados)

    if not ok:
        for e in errores:
            st.error(f"❌ {e}")
        st.stop()

    for a in advertencias:
        st.warning(a)

    # Descontar recursos
    descontar_recursos(lunes_semana_cirugia, recursos_solicitados)
    
    # Registrar cirugía
    registrar_cirugia(
        st.session_state.quirofanos,
        q_seleccionado,
        fecha,
        sesion,
        recursos_solicitados,
        nombre_cirugia
    )

    # Guardar cambios en JSON
    guardar_en_json(st.session_state.quirofanos)

    st.success("CIRUGÍA AGENDADA CORRECTAMENTE")

    for recurso in recursos_actuales.keys():
        st.session_state[f"reset_{recurso}"] = True
   
    # Actualizar la variable que contiene el stock disponible para que se muestre correctamente
    recursos_actuales = st.session_state.recursos_disponibles[lunes_semana_cirugia]

# ============================
# Botones fijos de navegación
# ============================

if "ir_a_delete" not in st.session_state:
    st.session_state.ir_a_delete = False
if "ir_a_staff" not in st.session_state:
    st.session_state.ir_a_staff = False

def marcar_delete():
    st.session_state.ir_a_delete = True

def marcar_staff():
    st.session_state.ir_a_staff = True

col1, col2 = st.columns(2)
with col1:
    st.button("VER CIRUGÍAS AGENDADAS", on_click=marcar_delete)
with col2:
    st.button("ATRÁS", on_click=marcar_staff)

if st.session_state.ir_a_delete:
    st.session_state.ir_a_delete = False
    st.switch_page("Pages/watch_surgery.py")

if st.session_state.ir_a_staff:
    st.session_state.ir_a_staff = False
    st.switch_page("Pages/staff_access.py")
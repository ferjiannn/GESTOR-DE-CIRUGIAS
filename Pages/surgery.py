import streamlit as st
import json
import os
from datetime import date, timedelta
from resources_validation import cargar_recursos_operativos, validar_recursos, descontar_recursos, inicializar_recursos

# ============================
# Inicialización de recursos
# ============================
if "recursos_disponibles" not in st.session_state:
    recursos = cargar_recursos_operativos()
    # convertir a formato plano: recurso -> stock actual
    st.session_state.recursos_disponibles = {k: v["stock_semanal"] for k, v in recursos.items()}
    

if "recursos_disponibles" not in st.session_state:
    # Inicializa con el stock real de data.json
    st.session_state.recursos_disponibles = inicializar_recursos()

    st.write("DEBUG: Recursos disponibles:", st.session_state.recursos_disponibles)

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

def registrar_cirugia(quirofanos, q_id, fecha, sesion, recursos_solicitados):
    fecha_str = str(fecha)
    if fecha_str not in quirofanos[q_id]["cirugias"]:
        quirofanos[q_id]["cirugias"][fecha_str] = []
    cirugia = {
        "sesion": sesion,
        "recursos": recursos_solicitados
    }
    quirofanos[q_id]["cirugias"][fecha_str].append(cirugia)

def sugerir_alternativa(quirofanos, fecha, q_original, sesion_original):
    fecha_str = str(fecha)
    # 1️⃣ Otra sesión en el mismo quirófano
    cirugias_mismo_q = quirofanos[q_original]["cirugias"].get(fecha_str, [])
    sesiones_ocupadas = [c["sesion"] for c in cirugias_mismo_q]
    for s in SESIONES:
        if s != sesion_original and s not in sesiones_ocupadas:
            return fecha, q_original, s
    # 2️⃣ Otro quirófano en la misma fecha
    for q_id, q_data in quirofanos.items():
        if q_id == q_original:
            continue
        cirugias_dia = q_data["cirugias"].get(fecha_str, [])
        if len(cirugias_dia) >= MAX_CIRUGIAS_POR_DIA:
            continue
        sesiones_ocupadas = [c["sesion"] for c in cirugias_dia]
        for s in SESIONES:
            if s not in sesiones_ocupadas:
                return fecha, q_id, s
    # 3️⃣ Otra fecha (siguiente disponible)
    for i in range(1, 31):
        nueva_fecha = fecha + timedelta(days=i)
        nueva_fecha_str = str(nueva_fecha)
        for q_id, q_data in quirofanos.items():
            cirugias_dia = q_data["cirugias"].get(nueva_fecha_str, [])
            if len(cirugias_dia) >= MAX_CIRUGIAS_POR_DIA:
                continue
            sesiones_ocupadas = [c["sesion"] for c in cirugias_dia]
            for s in SESIONES:
                if s not in sesiones_ocupadas:
                    return nueva_fecha, q_id, s
    return None

# ============================
# Estado de quirófanos
# ============================
if "quirofanos" not in st.session_state:
    st.session_state.quirofanos = cargar_desde_json()

# ============================
# Interfaz Streamlit
# ============================
st.markdown("# PLANIFICACIÓN DE CIRUGÍAS")

# Selección de fecha
hoy = date.today()
fecha = st.date_input(
    "Selecciona la fecha de cirugía",
    min_value=hoy,
    max_value=hoy + timedelta(days=30)
)

# Selección de sesión
sesion = st.radio("Selecciona la sesión", SESIONES)

# ============================
# Recursos solicitados (nombres consistentes con data.json y recursos.json)
# ============================
st.subheader("Recursos para la cirugía")

# Cargar recursos disponibles para mostrar
recursos_actuales = st.session_state.recursos_disponibles

# Diccionario donde guardaremos lo que el usuario solicita
recursos_solicitados = {}

# Crear un input por cada recurso disponible
for recurso, stock in recursos_actuales.items():

    max_clinico = LIMITES_RECURSOS.get(recurso, stock)
    cantidad = st.number_input(
        label=f"{recurso} (stock disponible: {stock}, max por cirugia: {max_clinico})",
        min_value=0,
        max_value=min(stock, max_clinico),
        value=0,
        step=1
    )
    if cantidad > 0:
        recursos_solicitados[recurso] = cantidad


# ============================
# Validación temprana de recursos
# ============================
ok, errores, advertencias = validar_recursos(fecha, recursos_solicitados)

if not ok:
    st.error("No se puede programar la cirugía por falta de recursos:")
    for e in errores:
        st.error(f"❌ {e}")
    st.stop()

for a in advertencias:
    st.warning(f"⚠️ {a}")

# Mostrar quirófanos disponibles
quirofanos_disponibles = obtener_quirofanos_disponibles(st.session_state.quirofanos, fecha)

if not quirofanos_disponibles:
    st.error("No hay quirófanos disponibles para esta fecha.")
else:
    q_seleccionado = st.selectbox("Selecciona el quirófano", quirofanos_disponibles)
    q_data = st.session_state.quirofanos[q_seleccionado]
    if validar_sesion(q_data, fecha, sesion):
        st.success(f"Quirófano {q_seleccionado} disponible para la sesión {sesion}.")

# ============================
# Bloque de AGENDAR cirugía
# ============================
if st.button("AGENDAR"):
    # Validación de sesión
    if not validar_sesion(q_data, fecha, sesion):
        st.error("La sesión seleccionada no está disponible")
        st.stop()

    # Validación de recursos
    ok, errores, advertencias = validar_recursos(fecha, recursos_solicitados)
    if not ok:
        for e in errores:
            st.error(f"❌ {e}")
        st.stop()

    for a in advertencias:
        st.warning(a)

    # Descontar recursos
    descontar_recursos(fecha, recursos_solicitados)

    # Registrar cirugía
    registrar_cirugia(st.session_state.quirofanos, q_seleccionado, fecha, sesion, recursos_solicitados)

    # Guardar en JSON
    guardar_en_json(st.session_state.quirofanos)

    st.success("Cirugía agendada correctamente")
else:
    # Sugerencias alternativas
    sugerencia = sugerir_alternativa(st.session_state.quirofanos, fecha, q_seleccionado, sesion)
    if sugerencia is not None:
        f, q, s = sugerencia
        st.warning(
            f"No disponible.\n\n"
            f"Sugerencia:\n"
            f"📅 Fecha: {f}\n"
            f"🏥 Quirófano: {q}\n"
            f"⏰ Sesión: {s}"
        )
    else:
        st.error("No hay alternativas disponibles para esta fecha.")
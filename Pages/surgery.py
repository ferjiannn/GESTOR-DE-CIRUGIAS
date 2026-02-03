import streamlit as st
import json
import os
from datetime import date, timedelta
from resources_validation import (
    cargar_recursos_operativos,
    validar_recursos,
    descontar_recursos,
    inicializar_recursos,
    reset_semanal_si_corresponde,
    lunes_de_la_semana
)
from utils import obtener_lunes_de_semana
from visual import ocultar_sidebar
ocultar_sidebar()
from visual import validar_recursos_criticos

# INICIALIZACION GLOBAL


if "stock_maximo" not in st.session_state:
    recursos_json = cargar_recursos_operativos()
    st.session_state.stock_maximo =recursos_json.copy()

if "recursos_disponibles" not in st.session_state:
    st.session_state.recursos_disponibles = {}
# Reset general si se indicó

if st.session_state.get("reset_surgery", False):
    for key in ["recursos_disponibles", "agenda", "quirófanos_disponibles", "sesiones_disponibles"]:
        st.session_state.pop(key, None)
   

# Inicialización de recursos

if "recursos_disponibles" not in st.session_state:
    st.session_state.recursos_disponibles = {}


# json de quirófanos

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


# limites

MAX_CIRUGIAS_POR_DIA = 2
SESIONES = ["Mañana (8:00)", "Tarde (14:00)"]

LIMITES_RECURSOS = {
    "Antibioticos": 3,
    "Analgesicos": 5,
    "Anestesicos": 1,
    "Antiinflamatorios": 2,
    "Anticoagulantes": 1,
    "Antiemeticos": 1,
    "Relajantes musculares": 1,
    "Soluciones intravenosas": 2,
    "Medicacion de soporte": 2,
    "Campos esteriles": 3,
    "Paños esteriles": 3,
    "Sabanas esteriles": 2,
    "Suturas y grapas": 4,
    "Contenedores esteriles": 1,
    "Sets ortopedicos": 1,
    "Sets de artroscopia": 1,
    "Implantes ortopedicos": 2
}


# Funciones quirófanos

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
    if q_original and q_original in quirofanos:
        cirugias = quirofanos[q_original].get("cirugias", {}).get(fecha_str, [])
        sesiones_ocupadas = [c["sesion"] for c in cirugias]
        for s in SESIONES:
            if s != sesion_original and s not in sesiones_ocupadas:
                return fecha, q_original, s

    # Otro quirófano en la misma fecha

    for q_id, q_data in quirofanos.items():
        if q_id == q_original:
            continue
        cirugias = q_data.get("cirugias", {}).get(fecha_str, [])
        if len(cirugias) < MAX_CIRUGIAS_POR_DIA:
            sesiones_ocupadas = [c["sesion"] for c in cirugias]
            for s in SESIONES:
                if s not in sesiones_ocupadas:
                    return fecha, q_id, s

    # Otra fecha (hasta 30 días)
    for i in range(1, 31):
        nueva_fecha = fecha + timedelta(days=i)
        nueva_fecha_str = str(nueva_fecha)
        for q_id, q_data in quirofanos.items():
            cirugias = q_data.get("cirugias", {}).get(nueva_fecha_str, [])
            if len(cirugias) < MAX_CIRUGIAS_POR_DIA:
                sesiones_ocupadas = [c["sesion"] for c in cirugias]
                for s in SESIONES:
                    if s not in sesiones_ocupadas:
                        return nueva_fecha, q_id, s

    return None, None, None


# Estado inicial quirófanos

if "quirofanos" not in st.session_state:
    st.session_state.quirofanos = cargar_desde_json()

if "recargar_estado" not in st.session_state:
    st.session_state.recargar_estado = False

if st.session_state.recargar_estado:
    st.session_state.quirofanos = cargar_desde_json()
    st.session_state.recargar_estado = False

# Principal

st.markdown("# PLANIFICACIÓN DE CIRUGÍAS")

hoy = date.today() + timedelta(days=1)
fecha = st.date_input("SELECCIONA LA FECHA", min_value=hoy, max_value=hoy + timedelta(days=30))

semana = fecha - timedelta(days=fecha.weekday())

# Inicializar recursos por semana
if semana not in st.session_state.recursos_disponibles:
    st.session_state.recursos_disponibles[semana] = cargar_recursos_operativos(semana)

quirofanos_disponibles = list(st.session_state.quirofanos.keys())
sesion = st.radio("SELECCIONA LA SESIÓN", SESIONES)


lunes_semana_cirugia = semana


# ==========================
# INPUTS DE RECURSOS
# ==========================
st.subheader("RECURSOS A SOLICITAR")
recursos_actuales = st.session_state.recursos_disponibles.get(lunes_semana_cirugia, inicializar_recursos())
recursos_solicitados = {}

for recurso, stock in recursos_actuales.items():
    # Inicializar session_state si no existe
    if f"input_{recurso}" not in st.session_state:
        st.session_state[f"input_{recurso}"] = 0
    if f"reset_{recurso}" not in st.session_state:
        st.session_state[f"reset_{recurso}"] = False

    max_por_cirugia = LIMITES_RECURSOS.get(recurso, stock)
    max_permitido = min(stock, max_por_cirugia)

    # Blindaje: que el valor nunca exceda el máximo permitido
    if st.session_state[f"input_{recurso}"] > max_permitido:
        st.session_state[f"input_{recurso}"] = max_permitido

    # Crear número input con key única
    cantidad = st.number_input(
        label=f"{recurso} (DISPONIBLE: {stock}, LÍMITE POR CIRUGÍA: {max_por_cirugia})",
        min_value=0,
        max_value=max_permitido,
        value=st.session_state[f"input_{recurso}"],
        step=1,
        key=f"input_{recurso}"
    )

    recursos_solicitados[recurso] = cantidad

    # Resetear si corresponde
    if st.session_state[f"reset_{recurso}"]:
        st.session_state[f"reset_{recurso}"] = False

    
ok, errores, advertencias = validar_recursos(lunes_semana_cirugia, recursos_solicitados)
if not ok:
    st.error("NO SE PUEDE PROGRAMAR LA CIRUGÍA POR FALTA DE RECURSOS:")
    for e in errores:
        st.error(f"❌ {e}")
    st.stop()

q_data = None
if not quirofanos_disponibles:
    st.error("NO HAY QUIRÓFANOS DISPONIBLES PARA ESTA FECHA.")

    sugerencia = sugerir_alternativa(st.session_state.quirofanos, fecha, None, None)
    if sugerencia:
        f, q, s = sugerencia
        st.info(f"SUGERENCIA:\n📅 FECHA: {f}\n🏥 QUIRÓFANO: {q}\n⏰ SESIÓN: {s}")
    else:
        st.error("NO HAY ALTERNATIVAS DISPONIBLES EN LOS PRÓXIMOS 30 DÍAS")
    st.stop()
else:
    q_seleccionado = st.selectbox("SELECCCIONA EL QUIRÓFANO", quirofanos_disponibles)
    q_data = st.session_state.quirofanos[q_seleccionado]
    if validar_sesion(q_data, fecha, sesion):
        st.success(f"QUIRÓFANO {q_seleccionado} DISPONIBLE PARA LA SESIÓN {sesion}.")

nombre_cirugia = st.text_input("NOMBRE DEL PACIENTE (especificar quirófano)", max_chars=50)

st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    background-color: #0A6ED1;
    color: white;
    font-size: 18px;
    height: 55px;
    border-radius: 12px;
    border: none;
    font-weight: 600;
}
div.stButton > button:hover {
    background-color: #084C9E;
}
</style>
""", unsafe_allow_html=True)


if st.button("AGENDAR"):

    if not nombre_cirugia.strip():
        st.error("DEBE INTRODUCIR EL NOMBRE DEL PACIENTE")
        st.stop()

    if not validar_sesion(q_data, fecha, sesion):
        st.error("NO DISPONIBLE")
        sugerencia = sugerir_alternativa(st.session_state.quirofanos, fecha, q_seleccionado, sesion)
        if sugerencia:
            f, q, s = sugerencia
            st.info(f"SUGERENCIA:\n📅 FECHA: {f}\n🏥 QUIRÓFANO: {q}\n⏰ SESIÓN: {s}")
        else:
            st.error("NO HAY ALTERNATIVAS DISPONIBLES PARA ESTA FECHA")
        st.stop()

    # VALIDAR RECURSOS NORMALES
    ok, errores, advertencias = validar_recursos(lunes_semana_cirugia, recursos_solicitados)
    if not ok:
        for e in errores:
            st.error(f"❌ {e}")
        st.stop()

    # VALIDAR RECURSOS CRÍTICOS
    from visual import validar_recursos_criticos
    stock_semana = st.session_state.recursos_disponibles[lunes_semana_cirugia]

    ok_criticos, mensaje_critico = validar_recursos_criticos(
        stock_semana,
        recursos_solicitados
    )

    if not ok_criticos:
        st.error(mensaje_critico)
        st.stop()

    # MOSTRAR ADVERTENCIAS
    for a in advertencias:
        st.warning(a)

    # DESCONTAR RECURSOS Y REGISTRAR CIRUGÍA
    descontar_recursos(lunes_semana_cirugia, recursos_solicitados)

    registrar_cirugia(
        st.session_state.quirofanos,
        q_seleccionado,
        fecha,
        sesion,
        recursos_solicitados,
        nombre_cirugia
    )

    guardar_en_json(st.session_state.quirofanos)

    # bandera para exito
    st.session_state.cirugia_exitosa = True  

    # RESET de los inputs de recursos
    recursos_actuales = st.session_state.recursos_disponibles[lunes_semana_cirugia]
    for r in recursos_actuales:
        st.session_state[f"reset_{r}"] = True


# MOSTRAR SUCCESS SI HUBO AGENDAMIENTO

if st.session_state.get("cirugia_exitosa"):
    st.success("CIRUGÍA AGENDADA CORRECTAMENTE")
    st.session_state.cirugia_exitosa = False
   

# Botones de navegación

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
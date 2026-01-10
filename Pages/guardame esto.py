import streamlit as st
import json
import unicodedata

def main():
    st.markdown("### PERSONAL ACCESS")

    if "clicked" not in st.session_state:
        st.session_state.clicked = False

if "acceso" not in st.session_state:
    st.session_state.acceso = False

with open ("APP\data.json", "r", encoding = "utf-8") as Data:
    appdata = json.load(Data) 

    staff = appdata.get("staff", {})
    staff_data = staff
    staff_list = []
    for key in staff_data:
        categoria = staff_data.get(key)
        
        if isinstance(categoria, list):
            staff_list.extend(categoria)


    input_name = st.text_input("NOMBRE")
    input_id = st.text_input("IDENTIFICACIÓN")
   

def handle_click():
    st.session_state.clicked = True

st.button("ACCEDER", on_click=handle_click)

if st.session_state.clicked:
    acceso_concedido = False


    for person in staff_list:
        if (
    person.get("nombre", "").strip()
        == input_name.strip()
        and person.get("id").strip()
        == input_id.strip()
    ):
            acceso_concedido = True
            break

    if acceso_concedido:
        st.session_state.acceso = True
        
    else:
        st.error("ACCESO DENEGADO")
    st.session_state.clicked = False

    if st.session_state.acceso:
        st.switch_page("surgery")
        






























'''import streamlit as st
import json 
import os
from datetime import date, timedelta

RUTA_JSON = "cirugías.json"

st.markdown("# PLANIFICATION")
# -----------------------------
# Datos iniciales (quirófanos)
# -----------------------------
def inicializar_quirofanos():
    return {
        "Q0-1": {"estado": "disponible", "cirugias": {}},
        "Q0-2": {"estado": "disponible", "cirugias": {}}
    }

# -----------------------------
# Constantes
# -----------------------------
MAX_CIRUGIAS_POR_DIA = 2
SESIONES = ["Mañana (8:00)", "Tarde (14:00)"]

# -----------------------------
# Funciones auxiliares
# -----------------------------
def obtener_quirofanos_disponibles(quirofanos, fecha):
    disponibles = []
    for q_id, q_data in quirofanos.items():
        cirugias_dia = q_data["cirugias"].get(str(fecha), [])
        if len(cirugias_dia) < MAX_CIRUGIAS_POR_DIA:
            disponibles.append(q_id)
    return disponibles

def validar_sesion(quirofano, fecha, sesion):
    cirugias_quirofano = quirofano["cirugias"].get(str(fecha), [])
    return sesion not in cirugias_quirofano

# -----------------------------
# Placeholder de validación de recursos
# -----------------------------
def validar_recursos_placeholder():
    """
    Simula la validación de recursos sin decrementar stock.
    Retorna True si hipotéticamente todos los recursos están disponibles.
    """
    # Aquí más adelante integrarás tu lógica completa de:
    # - Medicamentos
    # - Instrumental
    # - Personal
    # - Recursos físicos
    # Por ahora siempre devuelve True para fines de prueba
    return True, "Todos los recursos disponibles"


if "quirofanos" not in st.session_state:
    st.session_state.quirofanos = inicializar_quirofanos()


# Selección de fecha

hoy = date.today()
fecha = st.date_input(
    "Selecciona la fecha de cirugía",
    min_value=hoy,
    max_value=hoy + timedelta(days=30)
)


# Selección de sesión

sesion = st.radio("Selecciona la sesión", SESIONES)


# Mostrar quirófanos disponibles

quirofanos_disponibles = obtener_quirofanos_disponibles(st.session_state.quirofanos, fecha)

if not quirofanos_disponibles:
    st.error("No hay quirófanos disponibles para esta fecha.")
else:
    q_seleccionado = st.selectbox("Selecciona el quirófano", quirofanos_disponibles)
    
    # Validar sesión
    q_data = st.session_state.quirofanos[q_seleccionado]
    if validar_sesion(q_data, fecha, sesion):
        st.success(f"Quirófano {q_seleccionado} disponible para la sesión {sesion}.") '''
        
    

#### SURGERY.PY
'''    import streamlit as st
import json 
import os
from datetime import date, timedelta
from resources_validation import validar_recursos, descontar_recursos, inicializar_recursos

if "recursos_disponibles" not in st.session_state:
    st.session_state.recursos_disponibles = inicializar_recursos()

RUTA_JSON = "cirugías.json"

def guardar_en_json(quirofanos):
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(quirofanos, f, ensure_ascii=False, indent=4)


def cargar_desde_json():
    if os.path.exists(RUTA_JSON):
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            if data:   # 👈 clave
                return data
    return inicializar_quirofanos()

st.markdown("# PLANIFICATION")
# -----------------------------
# Datos iniciales (quirófanos)
# -----------------------------
def inicializar_quirofanos():
    return {
        "Q0-1": {"estado": "disponible", "cirugias": {}},
        "Q0-2": {"estado": "disponible", "cirugias": {}}
    }

# -----------------------------
# Constantes
# -----------------------------
MAX_CIRUGIAS_POR_DIA = 2
SESIONES = ["Mañana (8:00)", "Tarde (14:00)"]

# -----------------------------
# Funciones auxiliares
# -----------------------------
def obtener_quirofanos_disponibles(quirofanos, fecha):
    disponibles = []

    for q_id, q_data in quirofanos.items():
        cirugias_dia = q_data["cirugias"].get(str(fecha), [])

        # Seguridad: si algo raro viene del JSON
        if not isinstance(cirugias_dia, list):
            cirugias_dia = []

        # Cada elemento es una cirugía (dict)
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
# -----------------------------
# Placeholder de validación de recursos
# -----------------------------
def validar_recursos_placeholder():
    """
    Simula la validación de recursos sin decrementar stock.
    Retorna True si hipotéticamente todos los recursos están disponibles.
    """
    # Aquí más adelante integrarás tu lógica completa de:
    # - Medicamentos
    # - Instrumental
    # - Personal
    # - Recursos físicos
    # Por ahora siempre devuelve True para fines de prueba
    return True, "Todos los recursos disponibles"

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
        sesiones_ocupadas = [c["sesion"] for c in cirugias_dia]

        if len(cirugias_dia) >= MAX_CIRUGIAS_POR_DIA:
            continue

        for s in SESIONES:
            if s not in sesiones_ocupadas:
                return fecha, q_id, s

    # 3️⃣ Otra fecha (siguiente disponible)
    i = 1
    while i <= 30:  # límite razonable
        nueva_fecha = fecha + timedelta(days=i)
        nueva_fecha_str = str(nueva_fecha)

        for q_id, q_data in quirofanos.items():
            cirugias_dia = q_data["cirugias"].get(nueva_fecha_str, [])
            sesiones_ocupadas = [c["sesion"] for c in cirugias_dia]

            if len(cirugias_dia) >= MAX_CIRUGIAS_POR_DIA:
                continue

            for s in SESIONES:
                if s not in sesiones_ocupadas:
                    return nueva_fecha, q_id, s

        i += 1

    return None

if "quirofanos" not in st.session_state:
    st.session_state.quirofanos = cargar_desde_json()

# Selección de fecha

hoy = date.today()
fecha = st.date_input(
    "Selecciona la fecha de cirugía",
    min_value=hoy,
    max_value=hoy + timedelta(days=30)
)


# Selección de sesión

sesion = st.radio("Selecciona la sesión", SESIONES)

# -----------------------------
# Selección de recursos
# -----------------------------
st.subheader("Recursos para la cirugía")

recursos_solicitados = {
    "antibioticos": 2,
    "anestesicos": 1,
    "analgesicos": 1,
    "contenedores esteriles": 1    
}


# -----------------------------
# Validación temprana de recursos
# -----------------------------
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
    
    # Validar sesión
    q_data = st.session_state.quirofanos[q_seleccionado]
    if validar_sesion(q_data, fecha, sesion):
        st.success(f"Quirófano {q_seleccionado} disponible para la sesión {sesion}.")

# -----------------------------
# Inicializar stock de recursos si no existe
# -----------------------------
if "recursos_disponibles" not in st.session_state:
    st.session_state.recursos_disponibles = inicializar_recursos()

# -----------------------------
# Bloque de AGENDAR cirugía
# -----------------------------
if st.button("AGENDAR"):

    # 1️⃣ Validación de infraestructura (sesión y quirófano)
    if not validar_sesion(q_data, fecha, sesion):
        st.error("La sesión seleccionada no está disponible")
        st.stop()

    # 2️⃣ Validación clínica (recursos)
    ok, errores, advertencias = validar_recursos(fecha, recursos_solicitados)

    # Si hay errores críticos → bloquea la cirugía
    if not ok:
        for e in errores:
            st.error(e)
        st.stop()

    # Si hay advertencias → solo alerta, no bloquea
    for a in advertencias:
        st.warning(a)

    # 3️⃣ Descontar recursos confirmados
    descontar_recursos(fecha, recursos_solicitados)

    # 4️⃣ Registro de la cirugía en el JSON
    registrar_cirugia(
        st.session_state.quirofanos,
        q_seleccionado,
        fecha,
        sesion,
        recursos_solicitados   # 👈 nuevo parámetro
    )

    # 5️⃣ Guardar en JSON
    guardar_en_json(st.session_state.quirofanos)

    st.success("Cirugía agendada correctamente")

else:
    # Sugerencia alternativa si el quirófano o sesión no están disponibles
    sugerencia = sugerir_alternativa(
        st.session_state.quirofanos,
        fecha,
        q_seleccionado,
        sesion
    )

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
        st.error("No hay alternativas disponibles para esta fecha.")'''
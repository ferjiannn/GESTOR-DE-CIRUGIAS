import streamlit as st
from utils import obtener_cirugias_por_fecha
from logic_delete import eliminar_cirugia_por_nombre
import os
from datetime import date, datetime
import json
from visual import ocultar_sidebar
ocultar_sidebar()

def eliminar_cirugias_pasadas():
   
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RUTA_CIRUGIAS = os.path.join(BASE_DIR, "Pages", "cirugías.json")

    if not os.path.exists(RUTA_CIRUGIAS):
        return 0  # No hay cirugías que procesar

    with open(RUTA_CIRUGIAS, "r", encoding="utf-8") as f:
        quirofanos = json.load(f)

    hoy = date.today()
    eliminadas = 0

    for q_id, q_data in quirofanos.items():
        cirugias_por_fecha = q_data.get("cirugias", {})
        fechas_a_eliminar = []

        for fecha_str, lista_cirugias in cirugias_por_fecha.items():
            fecha_obj = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_obj < hoy:
                eliminadas += len(lista_cirugias)
                fechas_a_eliminar.append(fecha_str)

        for f in fechas_a_eliminar:
            del cirugias_por_fecha[f]

    if eliminadas > 0:
        with open(RUTA_CIRUGIAS, "w", encoding="utf-8") as f:
            json.dump(quirofanos, f, ensure_ascii=False, indent=4)

    return eliminadas


cirugias_eliminadas = eliminar_cirugias_pasadas()

if cirugias_eliminadas > 0:
    st.info(f"Se eliminaron automáticamente {cirugias_eliminadas} cirugías pasadas.")

st.markdown("# CIRUGÍAS AGENDADAS")

if "ir_a_staff" not in st.session_state:
    st.session_state.ir_a_staff = False

def marcar_staff():
    st.session_state.ir_a_staff = True


# Obtener cirugías agrupadas por fecha

cirugias_por_fecha = obtener_cirugias_por_fecha()  # devuelve dict {fecha: [cirugias]}

if not cirugias_por_fecha:
    st.info("NO HAY CIRUGÍAS AGENDADAS ACTUALMENTE.")
    if st.button("ATRÁS", on_click=marcar_staff):
        st.switch_page("Pages/staff_access.py")
    st.stop()


# Selección de fecha

fecha_seleccionada = st.selectbox(
    "SELECCIONA LA FECHA",
    sorted(cirugias_por_fecha.keys())
)


# Selección de cirugía dentro de la fecha

nombre_seleccionado = st.selectbox(
    "SELECCIONA LA CIRUGÍA",
    [c["nombre"] for c in cirugias_por_fecha[fecha_seleccionada]]
)


# Confirmación

st.warning("SE ELIMINARÁ LA CIRUGÍA SELECCIONADA")
confirmar = st.checkbox("CONFIRMAR")


# Botón de eliminación

if st.button("ELIMINAR CIRUGÍA"):
    if not confirmar:
        st.error("DEBES CONFIRMAR LA ELIMINACIÓN.")
        st.stop()

    # Llamada CORRECTA con nombre + fecha
    ok, mensaje = eliminar_cirugia_por_nombre(nombre_seleccionado, fecha_seleccionada)

    if ok:
        st.success(mensaje)
        st.session_state.recargar_estado = True
        st.session_state.pop("recursos_disponibles", None)
        st.session_state.pop("agenda", None)
        st.session_state.reset_surgery = True
        st.rerun()

    
    else:
        st.error(mensaje)

st.button("ATRÁS", on_click=marcar_staff)


if st.session_state.ir_a_staff:
    st.session_state.ir_a_staff = False
    st.switch_page("Pages/staff_access.py")
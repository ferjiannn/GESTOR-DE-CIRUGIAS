import streamlit as st
from utils import obtener_cirugias_por_fecha
from logic_delete import eliminar_cirugia_por_nombre
import os
from datetime import date, datetime
import json
from auxiliar_functions import ocultar_sidebar
ocultar_sidebar()

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

if "confirmar_delete" not in st.session_state:
    st.session_state.confirmar_delete = False


if not st.session_state.confirmar_delete:
    if st.button("ELIMINAR CIRUGÍA"):
        st.session_state.confirmar_delete = True
        st.rerun()

else:
    st.warning("CONFIRME QUE DESEA ELIMINAR ESTA CIRUGÍA")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("CONFIRMAR ELIMINACIÓN"):
            ok, mensaje = eliminar_cirugia_por_nombre(nombre_seleccionado, fecha_seleccionada)

            if ok:
                st.session_state.recargar_estado = True
                
                # Reset inmediato
                st.session_state.confirmar_delete = False
                
                st.rerun()
            else:
                st.error(mensaje)

    with col2:
        if st.button("CANCELAR"):
            st.session_state.confirmar_delete = False
            st.rerun()

st.divider()

if st.button("ATRÁS"):
    st.switch_page("Pages/staff_access.py")
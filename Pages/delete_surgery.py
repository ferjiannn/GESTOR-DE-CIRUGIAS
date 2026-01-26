import streamlit as st
from utils import obtener_cirugias_por_fecha
from logic_delete import eliminar_cirugia_por_nombre

st.markdown("# ELIMINAR CIRUGÍA")

# ============================
# Obtener cirugías agrupadas por fecha
# ============================
cirugias_por_fecha = obtener_cirugias_por_fecha()  # devuelve dict {fecha: [cirugias]}

if not cirugias_por_fecha:
    st.info("NO HAY CIRUGÍAS PROGRAMADAS ACTUALMENTE.")
    st.stop()

# ============================
# Selección de fecha
# ============================
fecha_seleccionada = st.selectbox(
    "SELECCIONA LA FECHA",
    sorted(cirugias_por_fecha.keys())
)

# ============================
# Selección de cirugía dentro de la fecha
# ============================
nombre_seleccionado = st.selectbox(
    "SELECCIONA LA CIRUGÍA",
    [c["nombre"] for c in cirugias_por_fecha[fecha_seleccionada]]
)

# ============================
# Confirmación
# ============================
st.warning("SE ELIMINARÁ LA CIRUGÍA SELECCIONADA")
confirmar = st.checkbox("CONFIRMAR")

# ============================
# Botón de eliminación
# ============================
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

if "ir_a_staff" not in st.session_state:
    st.session_state.ir_a_staff = False

def marcar_staff():
    st.session_state.ir_a_staff = True

st.button("ATRÁS", on_click=marcar_staff)


if st.session_state.ir_a_staff:
    st.session_state.ir_a_staff = False
    st.switch_page("Pages/staff_access.py")
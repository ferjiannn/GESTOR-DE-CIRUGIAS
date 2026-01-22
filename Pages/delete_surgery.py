import streamlit as st
from utils import obtener_cirugias_programadas
from logic_delete import eliminar_cirugia_por_nombre

st.markdown("# ELIMINAR CIRUGÍA")

# ============================
# Cargar cirugías existentes
# ============================
cirugias = obtener_cirugias_programadas()

if not cirugias:
    st.info("No hay cirugías programadas actualmente.")
    st.stop()

# Obtener solo los nombres
nombres_cirugias = sorted([c["nombre"] for c in cirugias])

# ============================
# Selección de cirugía
# ============================
nombre_seleccionado = st.selectbox(
    "Selecciona la cirugía a eliminar",
    nombres_cirugias
)

# ============================
# Confirmación
# ============================
st.warning(
    "⚠️ Esta acción eliminará la cirugía seleccionada"
)

confirmar = st.checkbox("Confirmo que deseo eliminar esta cirugía")

# ============================
# Botón de eliminación
# ============================
if st.button("ELIMINAR CIRUGÍA"):
    if not confirmar:
        st.error("Debes confirmar la eliminación.")
        st.stop()

    ok, mensaje = eliminar_cirugia_por_nombre(nombre_seleccionado)

    if ok:
        st.success(mensaje)
        st.experimental_rerun()
    else:
        st.error(mensaje)
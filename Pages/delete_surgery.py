import streamlit as st
from utils import obtener_cirugias_por_fecha
from logic_delete import eliminar_cirugia_por_nombre

st.markdown("# ELIMINAR CIRUGÍA")

# ============================
# Obtener cirugías por fecha
# ============================
cirugias_por_fecha = obtener_cirugias_por_fecha()

if not cirugias_por_fecha:
    st.info("NO HAY CIRUGÍAS PROGRAMADAS ACTUALMENTE.")
    st.stop()

# ============================
# Selección de fecha
# ============================
fecha_seleccionada = st.selectbox(
    "SELECCIONA LA FECHA DE LA CIRUGÍA",
    list(cirugias_por_fecha.keys())
)

# Obtener solo los nombres de pacientes de esa fecha
nombres_cirugias = [c["nombre"] for c in cirugias_por_fecha[fecha_seleccionada]]

# ============================
# Selección de cirugía
# ============================
nombre_seleccionado = st.selectbox(
    f"CIRUGÍAS PROGRAMADAS PARA {fecha_seleccionada}",
    nombres_cirugias
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

    ok, mensaje = eliminar_cirugia_por_nombre(nombre_seleccionado)

    if ok:
        st.success(mensaje.upper())
        st.experimental_rerun()  # Refresca la página para actualizar los selectbox
    else:
        st.error(mensaje.upper())
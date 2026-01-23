import streamlit as st
from utils import obtener_cirugias_por_fecha
from logic_delete import eliminar_cirugia_por_nombre

st.markdown("# ELIMINAR CIRUGÍA")

# ============================
# Cargar cirugías existentes por fecha
# ============================
cirugias_por_fecha = obtener_cirugias_por_fecha()

if not cirugias_por_fecha:
    st.info("NO HAY CIRUGÍAS PROGRAMADAS ACTUALMENTE.")
    st.stop()

# ============================
# Mostrar selectboxes por fecha
# ============================
seleccion_fecha = None
seleccion_nombre = None

for fecha, lista_cirugias in cirugias_por_fecha.items():
    st.subheader(f"FECHA: {fecha}")

    nombres = [c["nombre"] for c in lista_cirugias]
    nombre_seleccionado = st.selectbox(
        f"SELECCIONA LA CIRUGÍA DEL DÍA {fecha}",
        nombres,
        key=fecha  # clave única para cada selectbox
    )

    # Guardamos la última selección (o la que quieras usar para eliminar)
    seleccion_fecha = fecha
    seleccion_nombre = nombre_seleccionado

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

    ok, mensaje = eliminar_cirugia_por_nombre(seleccion_nombre)

    if ok:
        st.success(mensaje)
        st.experimental_set_query_params()  # recarga la página sin usar experimental_rerun
        st.experimental_rerun = None  # previene error si la función no existe
    else:
        st.error(mensaje)
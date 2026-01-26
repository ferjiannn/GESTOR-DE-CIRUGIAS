import streamlit as st
import json

st.markdown("# STAFF ACCESS")

# ============================
# Session state
# ============================
if "acceso" not in st.session_state:
    st.session_state.acceso = False

# ============================
# Cargar staff desde data.json
# ============================
with open("APP/data.json", "r", encoding="utf-8") as Data:
    appdata = json.load(Data)

staff = appdata.get("staff", {})
staff_list = []

for categoria in staff.values():
    if isinstance(categoria, list):
        staff_list.extend(categoria)

# ============================
# Inputs
# ============================
input_name = st.text_input("NOMBRE")
input_id = st.text_input("IDENTIFICACIÓN")

# ============================
# Botón ACCEDER
# ============================
if st.button("ACCEDER"):

    # Validación de campos vacíos
    if not input_name.strip() or not input_id.strip():
        st.error("DEBE INGRESAR LOS DATOS REQUERIDOS")
        st.stop()

    acceso_concedido = False

    for person in staff_list:
        if (
            person.get("nombre", "").strip() == input_name.strip()
            and person.get("id", "").strip() == input_id.strip()
        ):
            acceso_concedido = True
            break

    if acceso_concedido:
        st.session_state.acceso = True
    else:
        st.error("ACCESO DENEGADO")
        st.session_state.acceso = False

# ============================
# Opciones posteriores al acceso
# ============================
if st.session_state.acceso:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("AGENDAR CIRUGÍA"):
                st.switch_page("Pages/surgery.py")

        with col2:
            if st.button("ELIMINAR CIRUGÍA"):
                st.switch_page("Pages/delete_surgery.py")
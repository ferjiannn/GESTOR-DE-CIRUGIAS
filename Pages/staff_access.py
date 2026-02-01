import streamlit as st
import json
from visual import ocultar_sidebar
ocultar_sidebar()

st.markdown("# INGRESE SUS DATOS")


# Session state

if "acceso" not in st.session_state:
    st.session_state.acceso = False


# Cargar staff desde data.json

with open("APP/data.json", "r", encoding="utf-8") as Data:
    appdata = json.load(Data)

staff = appdata.get("staff", {})
staff_list = []

for categoria in staff.values():
    if isinstance(categoria, list):
        staff_list.extend(categoria)


# Inputs

input_name = st.text_input(
    label="",
    placeholder= "NOMBRE")
input_id = st.text_input(
    label="",
    placeholder="IDENTIFICACIÓN")

# ESTILO BOTÓN 

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



# Botón ACCEDER

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


# Opciones posteriores al acceso

if st.session_state.acceso:

        col1, col2 = st.columns(2)

        with col1:
            if st.button("AGENDAR CIRUGÍA"):
                st.switch_page("Pages/surgery.py")

        with col2:
            if st.button("VER CIRUGÍAS AGENDADAS"):
                st.switch_page("Pages/watch_surgery.py")
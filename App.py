import streamlit as st
import json
from PIL import Image
import os
from auxiliar_functions import ocultar_sidebar

ocultar_sidebar()

st.set_page_config(
    page_title="JF Bone & Motion Center",
    page_icon="🏥",
    layout="centered"
)


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

# LOGO

logo_path = os.path.join("APP", "logo.png")

st.write("")
st.write("")

col1, col2, col3 = st.columns([1, 3, 1])

with col2:
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)

st.write("")


# ESLOGAN

st.markdown(
    "<h2 style='text-align: center;'>Bienvenido a nuestro sistema</h2>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align: center; font-size:18px; color:#0A6ED1;'>"
    "Reconstruimos movimiento. Restauramos vidas."
    "</p>",
    unsafe_allow_html=True
)

st.write("")
st.write("")
st.divider()


# CONTRASEÑA

with open("APP/data.json", "r") as Data:
    appdata = json.load(Data)

with open("APP/password.json", "r") as confidential:
    data = json.load(confidential)
    real_password = data["password"]

st.markdown("### Ingrese la contraseña")
input_password = st.text_input("", type="password", placeholder="CONTRASEÑA")

st.write("")


# BOTÓN ACCESO

if st.button("ACCEDER"):
    if input_password == real_password:
        st.switch_page("Pages/staff_access.py")
    else:
        st.error("ACCESO DENEGADO")
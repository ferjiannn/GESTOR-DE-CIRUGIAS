import streamlit as st
import json
from PIL import Image
import os
from visual import ocultar_sidebar
ocultar_sidebar()


# Configuración página

st.set_page_config(page_title="JF Bone & Motion Center", page_icon="🏥", layout="centered")


# Nombre y logo del hospital

HOSPITAL_NAME = "JF Bone & Motion Center"
logo_path = os.path.join("APP", "logo.png")  # Logo que vamos a generar

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if os.path.exists(logo_path):
        st.image(logo_path, width=120)
    st.markdown(f"### {HOSPITAL_NAME}", unsafe_allow_html=True)

st.markdown("---")


# Cargar datos

with open("APP/data.json", "r") as Data:
    appdata = json.load(Data)

with open("APP/password.json", "r") as confidential:
    data = json.load(confidential)
    real_password = data["password"]


# Input de contraseña centrado

st.markdown("### Ingrese la contraseña para acceder al sistema")
input_password = st.text_input("", type="password", placeholder="CONTRASEÑA", key="password_input")


# Botón de ingreso estilizado

button_style = """
    <style>
    div.stButton > button {
        width: 100%;
        background-color: #0072B2;
        color: white;
        font-size: 18px;
        height: 50px;
        border-radius: 8px;
    }
    div.stButton > button:hover {
        background-color: #005C91;
        color: #ffffff;
    }
    </style>
"""
st.markdown(button_style, unsafe_allow_html=True)


# Boton de acceso

if st.button("ACCEDER"):
    if input_password == real_password:
       
        st.switch_page("Pages/staff_access.py")
    else:
        st.error("ACCESO DENEGADO")
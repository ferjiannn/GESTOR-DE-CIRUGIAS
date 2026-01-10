import streamlit as st
import json

st.title("SURGERY PROGRAMMER")

with open("APP\data.json", "r") as Data:
    appdata = json.load(Data)

    with open("APP\password.json", "r") as confidential:
        data = json.load(confidential)
        real_password = data["password"]

        input_password = st.text_input("CONTRASEÑA", type="password")

    if st.button("INGRESAR CONTRASEÑA"):
        if input_password == real_password:
            st.switch_page("pages\staff_access.py")
        else:
            st.error("ACCESO DENEGADO")





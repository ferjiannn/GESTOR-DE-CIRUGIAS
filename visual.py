
import streamlit as st

def ocultar_sidebar():
    
    st.markdown(
        """
        <style>
        /* Oculta el sidebar izquierdo completo */
        #MainMenu {visibility: hidden;}  /* Oculta el menú hamburguesa */
        footer {visibility: hidden;}    /* Oculta el footer de Streamlit */
        [data-testid="stSidebar"] {display: none;}  /* Oculta el sidebar real */
        </style>
        """,
        unsafe_allow_html=True
    )
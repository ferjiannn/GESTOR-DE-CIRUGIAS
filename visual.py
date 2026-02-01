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

# critical_resources.py

RECURSOS_CRITICOS = [
    "Anestesicos",
    "Campos esteriles",
    "Suturas y grapas",
    "Soluciones intravenosas",
    "Sets ortopedicos",
    "Contenedores esteriles"
]
def validar_recursos_criticos(stock_semana, recursos_solicitados):

    for recurso in RECURSOS_CRITICOS:

        # 1️⃣ Si no hay stock disponible en la semana → bloqueo automático
        if stock_semana.get(recurso, 0) <= 0:
            return False, f"NO SE PUEDE EFECTUAR LA CIRUGÍA SIN {recurso}"

        # 2️⃣ Si hay stock pero el usuario no seleccionó al menos 1
        if recurso not in recursos_solicitados or recursos_solicitados.get(recurso, 0) <= 0:
            return False, f"NO SE PUEDE EFECTUAR LA CIRUGÍA SIN {recurso}"

    return True, None